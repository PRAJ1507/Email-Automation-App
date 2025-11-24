from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship

from .db import Base


class EmailStatus(str, enum.Enum):
    draft = "draft"
    awaiting_review = "awaiting_review"
    queued = "queued"
    sent = "sent"
    delivered = "delivered"
    failed = "failed"
    replied = "replied"


class EventType(str, enum.Enum):
    sent = "sent"
    delivered = "delivered"
    open = "open"
    click = "click"
    bounce = "bounce"
    spam = "spam"
    reply = "reply"


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    company = Column(String, nullable=True)
    role = Column(String, nullable=True)
    hobbies = Column(Text, nullable=True)
    mbti_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    emails = relationship("EmailInstance", back_populates="contact")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    product_name = Column(String, nullable=True)
    product_description = Column(Text, nullable=True)
    base_prompt_template = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    steps = relationship("SequenceStep", back_populates="campaign")
    emails = relationship("EmailInstance", back_populates="campaign")


class SequenceStep(Base):
    __tablename__ = "sequence_steps"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    offset_days = Column(Integer, default=0)
    name = Column(String, nullable=False)

    campaign = relationship("Campaign", back_populates="steps")
    emails = relationship("EmailInstance", back_populates="sequence_step")


class EmailInstance(Base):
    __tablename__ = "email_instances"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    sequence_step_id = Column(Integer, ForeignKey("sequence_steps.id"), nullable=True)

    is_reply = Column(Boolean, default=False)
    parent_email_id = Column(Integer, ForeignKey("email_instances.id"), nullable=True)

    subject = Column(String, nullable=False)
    body_text = Column(Text, nullable=False)
    status = Column(Enum(EmailStatus), default=EmailStatus.draft)

    sent_at = Column(DateTime, nullable=True)

    provider_message_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="emails")
    contact = relationship("Contact", back_populates="emails")
    sequence_step = relationship("SequenceStep", back_populates="emails")
    events = relationship("EmailEvent", back_populates="email", cascade="all, delete-orphan")
    parent_email = relationship("EmailInstance", remote_side=[id])


class EmailEvent(Base):
    __tablename__ = "email_events"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("email_instances.id"), nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    event_metadata = Column(JSON, nullable=True)  # ✅ renamed
    created_at = Column(DateTime, default=datetime.utcnow)

    email = relationship("EmailInstance", back_populates="events")
