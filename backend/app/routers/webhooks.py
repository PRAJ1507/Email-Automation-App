
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from ..models import EmailInstance, EmailEvent, EventType, EmailStatus
from ..schemas import ReplyWebhookPayload
from ..services.agent import get_email_agent

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/sendgrid-events")
async def sendgrid_events(
    events: List[dict] = Body(...),
    db: Session = Depends(get_db),
):
    """
    Map basic SendGrid delivered/bounce/etc. events to EmailEvent.
    You should configure SendGrid Event Webhook to send JSON here.
    """
    for ev in events:
        email_instance_id = ev.get("email_instance_id") or ev.get("custom_args", {}).get("email_instance_id")
        if not email_instance_id:
            continue
        email = db.get(EmailInstance, int(email_instance_id))
        if not email:
            continue

        event_type_str = ev.get("event")
        if not event_type_str:
            continue
        try:
            event_type = EventType(event_type_str)
        except Exception:
            continue

        email_event = EmailEvent(
            email_id=email.id,
            event_type=event_type,
            event_metadata=ev,
        )
        db.add(email_event)

        if event_type == EventType.delivered:
            email.status = EmailStatus.delivered
        elif event_type == EventType.bounce:
            email.status = EmailStatus.failed
        elif event_type == EventType.reply:
            email.status = EmailStatus.replied

    db.commit()
    return {"ok": True}


@router.post("/reply")
async def handle_reply(
    payload: ReplyWebhookPayload,
    db: Session = Depends(get_db),
):
    """
    Handle a reply:
    - Use the LangChain agent to classify and draft a reply.
    - Agent decides whether to auto-send (simple query) or just create a draft.
    """
    original = db.get(EmailInstance, payload.original_email_id)
    if not original:
        raise HTTPException(status_code=404, detail="Original email not found")

    agent = get_email_agent()
    state = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "We received an email reply.\n"
                        f"Original email id: {payload.original_email_id}\n"
                        f"Incoming reply text: {payload.incoming_text}\n"
                        f"Recipient's email address: {payload.from_email}\n\n"
                        "1) Call classify_reply_tool to see if the reply is simple.\n"
                        "2) Call draft_reply_tool to create a reply body.\n"
                        "3) If classify_reply_tool.is_simple is true, "
                        "call send_email_tool to send the reply automatically.\n"
                        "4) Otherwise, only create the draft and do NOT send.\n"
                        "Return a short summary of what you did."
                    ),
                }
            ]
        }
    )

    final_msg = state["messages"][-1]
    return {"summary": final_msg.content}