from typing import Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, CustomArg  # 👈 add CustomArg here

from ..config import settings

sg_client = SendGridAPIClient(settings.SENDGRID_API_KEY)


def send_email_via_sendgrid(
    to_email: str,
    subject: str,
    body_text: str,
    email_instance_id: int,
) -> Optional[str]:
    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body_text,
    )

    # ✅ Correct way for current SendGrid SDK
    try:
        message.add_custom_arg(CustomArg("email_instance_id", str(email_instance_id)))
    except Exception:
        # If anything goes wrong with custom args, just skip them
        pass

    response = sg_client.send(message)
    msg_id = (
        response.headers.get("X-Message-Id")
        or response.headers.get("X-Message-ID")
        or ""
    )
    return msg_id
