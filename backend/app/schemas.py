from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import EmailStatus


class ContactPreview(BaseModel):
    email: str
    first_name: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    hobbies: Optional[str] = None
    mbti_type: Optional[str] = None

class ContactBase(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None
    company: Optional[str] = None


class UploadContactsResponse(BaseModel):
    preview_rows: List[ContactPreview]
    inferred_columns: List[str]


class ConfirmContact(BaseModel):
    email: str
    first_name: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    hobbies: Optional[str] = None
    mbti_type: Optional[str] = None


class ConfirmContactsRequest(BaseModel):
    campaign_name: str
    product_name: str
    product_description: str
    contacts: List[ConfirmContact]


class CampaignResponse(BaseModel):
    id: int
    name: str
    product_name: str
    product_description: Optional[str]

    class Config:
        from_attributes = True


class EmailInstanceBase(BaseModel):
    id: int
    campaign_id: int
    contact_id: int
    sequence_step_id: Optional[int]
    subject: str
    body_text: str
    status: EmailStatus
    is_reply: bool

    class Config:
        from_attributes = True


class UpdateEmailRequest(BaseModel):
    subject: Optional[str] = None
    body_text: Optional[str] = None
    status: Optional[EmailStatus] = None


class GenerateEmailsRequest(BaseModel):
    regenerate: bool = False
    contact_ids: Optional[List[int]] = None


class EmailAnalytics(BaseModel):
    id: int
    subject: str
    recipient_email: str
    recipient_name: str
    status: str
    sent_at: Optional[datetime]
    open_count: int
    click_count: int
    bounce: bool

class CampaignStatusSummary(BaseModel):
    total_emails: int
    sent: int
    delivered: int
    failed: int
    replied: int
    draft: int
    sent_emails: List[EmailAnalytics]


class SendEmailsRequest(BaseModel):
    step_number: int
    send_mode: str = Field("immediate", pattern="^(immediate|schedule)$")
    # For now we only support immediate; this is for future scheduling.


class ReplyWebhookPayload(BaseModel):
    original_email_id: int
    incoming_text: str
    from_email: str
