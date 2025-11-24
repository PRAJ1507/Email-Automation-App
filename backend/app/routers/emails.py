from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import EmailInstance, EmailStatus, Campaign, SequenceStep
from ..schemas import EmailInstanceBase, UpdateEmailRequest, SendEmailsRequest
from ..services.email_service import send_email_via_sendgrid

router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("/", response_model=List[EmailInstanceBase])
def list_emails(
    campaign_id: int,
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(EmailInstance).filter(EmailInstance.campaign_id == campaign_id)
    if status:
        query = query.filter(EmailInstance.status == EmailStatus(status))
    emails = query.order_by(EmailInstance.id.desc()).all()
    return [EmailInstanceBase.model_validate(e) for e in emails]


@router.put("/{email_id}", response_model=EmailInstanceBase)
def update_email(
    email_id: int,
    payload: UpdateEmailRequest,
    db: Session = Depends(get_db),
):
    email = db.get(EmailInstance, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    if payload.subject is not None:
        email.subject = payload.subject
    if payload.body_text is not None:
        email.body_text = payload.body_text
    if payload.status is not None:
        email.status = payload.status

    db.commit()
    db.refresh(email)
    return EmailInstanceBase.model_validate(email)


@router.post("/send", response_model=int)
def send_emails(
    payload: SendEmailsRequest,
    campaign_id: int,
    db: Session = Depends(get_db),
):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    step = (
        db.query(SequenceStep)
        .filter(SequenceStep.campaign_id == campaign_id, SequenceStep.step_number == payload.step_number)
        .first()
    )
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    emails = (
        db.query(EmailInstance)
        .filter(
            EmailInstance.campaign_id == campaign_id,
            EmailInstance.sequence_step_id == step.id,
            EmailInstance.status.in_([EmailStatus.draft, EmailStatus.awaiting_review]),
            EmailInstance.is_reply == False,
        )
        .all()
    )

    sent_count = 0
    for email in emails:
        msg_id = send_email_via_sendgrid(
            to_email=email.contact.email,
            subject=email.subject,
            body_text=email.body_text,
            email_instance_id=email.id,
        )
        email.provider_message_id = msg_id
        email.sent_at = datetime.utcnow()
        email.status = EmailStatus.sent
        sent_count += 1

    db.commit()
    return sent_count
