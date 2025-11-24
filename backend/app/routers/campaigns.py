from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Campaign, SequenceStep, Contact, EmailInstance, EmailStatus
from ..schemas import (
    GenerateEmailsRequest,
    EmailInstanceBase,
    CampaignStatusSummary,
)

from ..services.agent import get_email_agent 

router = APIRouter(prefix="/campaigns", tags=["campaigns"])



@router.get("/{campaign_id}", response_model=CampaignStatusSummary)
def get_campaign_status(
    campaign_id: int,
    db: Session = Depends(get_db),
):
    from ..schemas import EmailAnalytics
    from ..models import EmailEvent

    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    total = db.query(EmailInstance).filter(EmailInstance.campaign_id == campaign_id).count()
    sent = db.query(EmailInstance).filter(
        EmailInstance.campaign_id == campaign_id, EmailInstance.status == EmailStatus.sent
    ).count()
    delivered = db.query(EmailInstance).filter(
        EmailInstance.campaign_id == campaign_id, EmailInstance.status == EmailStatus.delivered
    ).count()
    failed = db.query(EmailInstance).filter(
        EmailInstance.campaign_id == campaign_id, EmailInstance.status == EmailStatus.failed
    ).count()
    replied = db.query(EmailInstance).filter(
        EmailInstance.campaign_id == campaign_id, EmailInstance.status == EmailStatus.replied
    ).count()
    draft = db.query(EmailInstance).filter(
        EmailInstance.campaign_id == campaign_id, EmailInstance.status == EmailStatus.draft
    ).count()

    # Get sent emails with analytics
    sent_emails_data = db.query(EmailInstance, Contact.email, Contact.first_name).join(
        Contact, EmailInstance.contact_id == Contact.id
    ).filter(EmailInstance.campaign_id == campaign_id, EmailInstance.status == EmailStatus.sent).all()

    sent_emails = []
    for email, recipient_email, recipient_name in sent_emails_data:
        open_count = db.query(EmailEvent).filter(
            EmailEvent.email_id == email.id, EmailEvent.event_type == 'open'
        ).count()
        click_count = db.query(EmailEvent).filter(
            EmailEvent.email_id == email.id, EmailEvent.event_type == 'click'
        ).count()
        bounce = db.query(EmailEvent).filter(
            EmailEvent.email_id == email.id, EmailEvent.event_type.in_(['bounce', 'spam'])
        ).count() > 0

        sent_emails.append(EmailAnalytics(
            id=email.id,
            subject=email.subject,
            recipient_email=recipient_email,
            recipient_name=recipient_name or "",
            status=email.status.value,
            sent_at=email.sent_at,
            open_count=open_count,
            click_count=click_count,
            bounce=bounce,
        ))

    return CampaignStatusSummary(
        total_emails=total,
        sent=sent,
        delivered=delivered,
        failed=failed,
        replied=replied,
        draft=draft,
        sent_emails=sent_emails,
    )


@router.post("/{campaign_id}/generate-emails", response_model=List[EmailInstanceBase])
def generate_emails(
    campaign_id: int,
    payload: GenerateEmailsRequest,
    db: Session = Depends(get_db),
):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if payload.contact_ids:
        contacts = db.query(Contact).filter(Contact.id.in_(payload.contact_ids)).all()
        if not contacts:
            raise HTTPException(status_code=400, detail="No valid contacts found")
    else:
        contacts = db.query(Contact).all()
    steps = (
        db.query(SequenceStep)
        .filter(SequenceStep.campaign_id == campaign_id)
        .order_by(SequenceStep.step_number)
        .all()
    )

    if not contacts or not steps:
        raise HTTPException(status_code=400, detail="Campaign missing contacts or steps")

    if payload.regenerate:
        db.query(EmailInstance).filter(
            EmailInstance.campaign_id == campaign_id, EmailInstance.is_reply == False
        ).delete()
        db.commit()

    email_instances: list[EmailInstance] = []
    agent = get_email_agent()

    # For each (contact, step), check if already exists, if not, generate
    for contact in contacts:
        for step in steps:
            existing_email = db.query(EmailInstance).filter(
                EmailInstance.campaign_id == campaign_id,
                EmailInstance.contact_id == contact.id,
                EmailInstance.sequence_step_id == step.id,
                EmailInstance.is_reply == False,
            ).first()

            if existing_email:
                email_instances.append(existing_email)
                continue  # Skip generation if already exists

            state = agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                "Generate an outreach email for this contact and step. "
                                f"Use generate_sequence_email_tool with contact_id={contact.id} "
                                f"and step_id={step.id}. "
                                "Return the tool result."
                            ),
                        }
                    ]
                }
            )
            # The tool itself already creates the EmailInstance in the DB.
            # To keep things simple, we just fetch the latest email for this contact+step.
            latest_email = (
                db.query(EmailInstance)
                .filter(
                    EmailInstance.campaign_id == campaign_id,
                    EmailInstance.contact_id == contact.id,
                    EmailInstance.sequence_step_id == step.id,
                )
                .order_by(EmailInstance.id.desc())
                .first()
            )
            if latest_email:
                email_instances.append(latest_email)

    return [EmailInstanceBase.model_validate(e) for e in email_instances]
