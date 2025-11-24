import json
from datetime import datetime
from typing import Optional, Dict, Any

from langchain.tools import tool
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from ..config import settings
from ..db import SessionLocal
from ..models import (
    Contact,
    Campaign,
    SequenceStep,
    EmailInstance,
    EmailStatus,
)


# -------------------------------------------------------------------
# LLM helper
# -------------------------------------------------------------------

def _get_llm():
    """Central place to construct the Groq-backed chat model."""
    return ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL_NAME,
        temperature=0.5,
        max_tokens=1500,
    )


def _parse_json(text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    """Try to extract JSON from a string; fall back gracefully."""
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        snippet = text[start:end]
        return json.loads(snippet)
    except Exception:
        return fallback


# -------------------------------------------------------------------
# Prompts (we'll parse JSON ourselves instead of using StructuredOutputParser)
# -------------------------------------------------------------------

INITIAL_PROMPT = ChatPromptTemplate.from_template(
    """
You are an email writing assistant helping a single user send a short, professional yet personal sales/marketing email.

Product:
- Name: {product_name}
- Description: {product_description}

Recipient:
- First name: {first_name}
- Company: {company}
- Role: {role}
- Hobbies: {hobbies}
- MBTI personality type: {mbti}

Sequence step: {step_number} ({step_name})

Constraints:
- Keep body under 180 words.
- Mention the company and, if relevant, the role.
- Use a friendly, concise tone.
- No emojis.

Return ONLY a valid JSON object with exactly two string fields:
- "subject" → the subject line
- "body" → the email body

Do NOT include any explanation, markdown, or backticks. Only the JSON.
"""
)


REPLY_CLASS_PROMPT = ChatPromptTemplate.from_template(
    """
You are helping decide if an incoming email reply is a simple query that can be safely auto-answered.

Original email (sent by us):
{original_email}

Incoming reply (from recipient):
{incoming_reply}

Question:
Is this a simple query where a short, factual answer is enough
(e.g. asking for a link, pricing, availability, quick clarification)?

Return ONLY a valid JSON object with exactly two fields:
- "is_simple": either the string "yes" or the string "no"
- "reason": a short explanation string

Do NOT include explanation or markdown outside of the JSON. Only output the JSON object.
"""
)



REPLY_DRAFT_PROMPT = ChatPromptTemplate.from_template(
    """
You are writing an email reply on behalf of the user.

Original email we sent:
{original_email}

Incoming reply from recipient:
{incoming_reply}

Goal:
{goal}

Write a short, polite, helpful reply email body in plain text.
Constraints:
- No markdown.
- No emojis.
- Sign off with "Best regards, {sender_first_name}".

Return ONLY the email body as plain text, no JSON, no quotes, no extra commentary.
"""
)


# -------------------------------------------------------------------
# Tools – used by the agent, and they also touch the DB
# -------------------------------------------------------------------

@tool
def generate_sequence_email_tool(contact_id: int, step_id: int) -> dict:
    """
    Generate a subject and body for an initial sequence email
    for a given contact and sequence step. Returns JSON with
    keys: subject, body, email_instance_id.
    """
    db = SessionLocal()
    try:
        contact: Optional[Contact] = db.get(Contact, contact_id)
        step: Optional[SequenceStep] = db.get(SequenceStep, step_id)
        if not contact or not step:
            return {"error": "Invalid contact_id or step_id"}

        campaign: Optional[Campaign] = db.get(Campaign, step.campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}

        # Build prompt dynamically, incorporating base_prompt_template if available
        base_prompt_text = campaign.base_prompt_template or """
You are an email writing assistant helping a single user send a short, professional yet personal sales/marketing email."""

        full_prompt_template = base_prompt_text + """

Product:
- Name: {product_name}
- Description: {product_description}

Recipient:
- First name: {first_name}
- Company: {company}
- Role: {role}
- Hobbies: {hobbies}
- MBTI personality type: {mbti}

Sequence step: {step_number} ({step_name})
This is a {step_name} email in a sequence. Tailor the content accordingly - initial outreach might introduce, follow-ups build on previous contact, finals might close or create urgency.

Constraints:
- Keep body under 180 words.
- The body must start with "Dear {first_name},".
- Mention the company and, if relevant, the role.
- Use a friendly, concise tone.
- No emojis.
- Sign off with "Best regards, {sender_first_name}".

Return ONLY a valid JSON object with exactly two string fields:
- "subject" → the subject line
- "body" → the email body content only (do not include greeting or sign-off in the JSON body field, as they are fixed)

Do NOT include any explanation, markdown, or backticks. Only the JSON.
"""
        dynamic_prompt = ChatPromptTemplate.from_template(full_prompt_template)

        llm_json = _get_llm().bind(response_format={"type": "json_object"})
        chain = dynamic_prompt | llm_json
        fallback = {
            "subject": f"Hello{ ' ' + contact.first_name if contact.first_name else '' },",
            "body": (
                f"Dear{ ' ' + contact.first_name if contact.first_name else '' },\n\n"
                f"I wanted to reach out regarding our product: {campaign.product_name}.\n"
                f"{campaign.product_description or 'We think you might find it valuable.'}\n"
                f"If you have any questions, feel free to reply.\n\n"
                f"Best regards,\n"
                f"{settings.SENDER_FIRST_NAME}"
            )
        }

        msg = chain.invoke(
            {
                "product_name": campaign.product_name,
                "product_description": campaign.product_description or "",
                "first_name": contact.first_name or "",
                "company": contact.company or "",
                "role": contact.role or "",
                "hobbies": contact.hobbies or "",
                "mbti": contact.mbti_type or "",
                "step_number": step.step_number,
                "step_name": step.name,
                "sender_first_name": settings.SENDER_FIRST_NAME,
            }
        )
        raw = msg.content if hasattr(msg, "content") else str(msg)
        data = _parse_json(raw, fallback)

        subject = data.get("subject", fallback["subject"])
        # Construct full body with greeting and sign-off, avoiding double greeting or sign-off
        content = data["body"]
        if content.strip().startswith("Dear"):
            base_body = content
        else:
            base_body = f"Dear {contact.first_name},\n\n{content}"

        # If it already has sign-off, don't add again
        if "Best regards" in base_body or "Regards," in base_body:
            full_body = base_body
        else:
            full_body = f"{base_body}\n\nBest regards,\n{settings.SENDER_FIRST_NAME}"
        body = full_body

        # Create EmailInstance as draft
        email = EmailInstance(
            campaign_id=campaign.id,
            contact_id=contact.id,
            sequence_step_id=step.id,
            subject=subject,
            body_text=body,
            status=EmailStatus.draft,
            is_reply=False,
        )
        db.add(email)
        db.commit()
        db.refresh(email)

        return {
            "email_instance_id": email.id,
            "subject": subject,
            "body": body,
        }
    finally:
        db.close()


@tool
def classify_reply_tool(original_email_id: int, incoming_text: str) -> dict:
    """
    Classify whether a reply is simple enough to auto-respond.
    Returns JSON with keys: is_simple (bool), reason (str).
    """
    db = SessionLocal()
    try:
        original: Optional[EmailInstance] = db.get(EmailInstance, original_email_id)
        if not original:
            return {"error": "Original email not found"}

        llm = _get_llm()
        chain = REPLY_CLASS_PROMPT | llm
        msg = chain.invoke(
            {
                "original_email": original.body_text,
                "incoming_reply": incoming_text,
            }
        )
        raw = msg.content if hasattr(msg, "content") else str(msg)
        data = _parse_json(raw, {"is_simple": "no", "reason": "Failed to parse"})

        is_simple = str(data.get("is_simple", "")).strip().lower() == "yes"
        reason = data.get("reason", "")
        return {"is_simple": is_simple, "reason": reason}
    finally:
        db.close()


@tool
def draft_reply_tool(original_email_id: int, incoming_text: str, goal: str) -> dict:
    """
    Draft a reply email body for the given original email + incoming reply.
    Returns JSON with keys: body, reply_email_id.
    """
    db = SessionLocal()
    try:
        original: Optional[EmailInstance] = db.get(EmailInstance, original_email_id)
        if not original:
            return {"error": "Original email not found"}

        llm = _get_llm()
        chain = REPLY_DRAFT_PROMPT | llm
        msg = chain.invoke(
            {
                "original_email": original.body_text,
                "incoming_reply": incoming_text,
                "goal": goal,
                "sender_first_name": settings.SENDER_FIRST_NAME,
            }
        )
        body = msg.content if hasattr(msg, "content") else str(msg)

        reply_email = EmailInstance(
            campaign_id=original.campaign_id,
            contact_id=original.contact_id,
            sequence_step_id=None,
            is_reply=True,
            parent_email_id=original.id,
            subject=f"Re: {original.subject}",
            body_text=body,
            status=EmailStatus.awaiting_review,
        )
        db.add(reply_email)
        db.commit()
        db.refresh(reply_email)

        return {"reply_email_id": reply_email.id, "body": body}
    finally:
        db.close()


@tool
def send_email_tool(email_instance_id: int) -> str:
    """
    Send the given email instance via SendGrid and update its status.
    Returns a short status string.
    """
    from .email_service import send_email_via_sendgrid  # local import to avoid cycles

    db = SessionLocal()
    try:
        email: Optional[EmailInstance] = db.get(EmailInstance, email_instance_id)
        if not email:
            return "Email not found."

        contact: Optional[Contact] = db.get(Contact, email.contact_id)
        if not contact:
            return "Contact not found."

        msg_id = send_email_via_sendgrid(
            to_email=contact.email,
            subject=email.subject,
            body_text=email.body_text,
            email_instance_id=email.id,
        )
        email.provider_message_id = msg_id
        email.sent_at = datetime.utcnow()
        email.status = EmailStatus.sent
        db.commit()
        return f"Email {email.id} sent."
    finally:
        db.close()


# -------------------------------------------------------------------
# Build the LangChain agent
# -------------------------------------------------------------------

TOOLS = [
    generate_sequence_email_tool,
    classify_reply_tool,
    draft_reply_tool,
    send_email_tool,
]

SYSTEM_PROMPT = (
    "You are an email automation agent for a single user.\n"
    "You can:\n"
    "1) Generate initial outreach sequence emails.\n"
    "2) Analyze incoming replies to see if they are simple queries.\n"
    "3) Draft replies.\n"
    "4) Send emails.\n\n"
    "Rules:\n"
    "- When asked to generate one or more outreach emails, call generate_sequence_email_tool for each sequence step.\n"
    "- For replies, first call classify_reply_tool.\n"
    "- If classify_reply_tool.is_simple is true, you may call draft_reply_tool "
    "and then send_email_tool to auto-send.\n"
    "- If classify_reply_tool.is_simple is false, call draft_reply_tool only. "
    "Do NOT call send_email_tool; just prepare a draft for human review.\n"
    "- Keep emails short, professional and personal.\n"
)


def get_email_agent():
    """
    Construct and return a LangChain agent that knows how to use the tools above.
    """
    llm = _get_llm()
    agent = create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent


# -------------------------------------------------------------------
# Optional helpers (used by routes if you want more direct control)
# -------------------------------------------------------------------

def run_initial_sequence_agent(contact_id: int, step_id: int) -> Dict[str, Any]:
    """
    Convenience helper: ask the agent to generate one email for (contact, step).
    """
    agent = get_email_agent()
    state = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Generate an outreach email for this contact and step. "
                        f"Use generate_sequence_email_tool with contact_id={contact_id} "
                        f"and step_id={step_id}. "
                        "Return the tool result."
                    ),
                }
            ]
        }
    )
    final_msg = state["messages"][-1]
    return getattr(final_msg, "tool_calls", None) or {"summary": final_msg.content}


def run_reply_agent(
    original_email_id: int,
    incoming_text: str,
    recipient_email: str,
    auto_send_goal: str = "Help the user respond and move the conversation forward.",
) -> Dict[str, Any]:
    """
    Run the reply agent logic; used if you want to trigger it manually.
    """
    agent = get_email_agent()
    state = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "We received an email reply.\n"
                        f"Original email id: {original_email_id}\n"
                        f"Incoming reply text: {incoming_text}\n"
                        f"Recipient's email address: {recipient_email}\n\n"
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
