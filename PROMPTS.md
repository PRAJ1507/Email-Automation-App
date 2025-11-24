# Sample Prompts for AI Email Generation

This document provides sample prompts used in the email automation system, powered by Groq (Llama 3.1 8B model).

## 1. Initial Sequence Email Generation Prompt

Used in `generate_sequence_email_tool` for creating personalized outreach emails.

**Template:**
```
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
- "body" → the email body content only (do not include greeting or sign-off in the JSON body field, as they are fixed)
```

**Example Input Data:**
- product_name: "AI Email Bot"
- product_description: "An AI-powered tool for personalized email marketing that saves time and boosts response rates."
- first_name: "John"
- company: "TechCorp"
- role: "CTO"
- hobbies: "reading sci-fi"
- mbti: "INTJ"
- step_number: "1"
- step_name: "Initial Outreach"

**Expected Output (JSON):**
```json
{
  "subject": "Exploring AI Solutions for TechCorp",
  "body": "I hope this email finds you well. As the CTO of TechCorp, you're likely interested in innovative tools. Our AI Email Bot personalizes marketing emails, potentially boosting your team's efficiency. Given your enjoyment of reading sci-fi, you might appreciate how it uses advanced algorithms to craft messages."
}
```

## 2. Reply Classification Prompt

Used in `classify_reply_tool` to determine if a reply is simple enough for auto-respond.

**Template:**
```
You are helping decide if an incoming email reply is a simple query that can be safely auto-answered.

Original email (sent by us):
{original_email}

Incoming reply (from recipient):
{incoming_reply}

Question:
Is this a simple query where a short, factual answer is enough (e.g. asking for a link, pricing, availability, quick clarification)?

Return ONLY a valid JSON object with exactly two fields:
- "is_simple": either the string "yes" or the string "no"
- "reason": a short explanation string

Do NOT include explanation or markdown outside of the JSON. Only output the JSON object.
```

**Example Input:**
- original_email: "Dear John, Our AI Bot helps automate emails. Reply if interested in a demo."
- incoming_reply: "What's the pricing?"

**Expected Output:**
```json
{
  "is_simple": "yes",
  "reason": "Query asks for pricing info, which is factual."
}
```

## 3. Reply Drafting Prompt

Used in `draft_reply_tool` for composing responses to complex replies.

**Template:**
```
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
```

**Example Input:**
- original_email: "Interested in our AI tool?"
- incoming_reply: "What integrations do you support?"
- goal: "Provide info and encourage scheduling a call."
- sender_first_name: "Alice"

**Expected Output:**
```
Thank you for your interest. Our AI Email Bot currently integrates with SendGrid, Mailchimp, and HubSpot. More details are on our website. Would you like to schedule a demo call?

Best regards, Alice
```

## General Notes on Prompt Design

- **Personalization**: Prompts inject recipient data (product, profile) for tailored content.
- **Constraints**: Word limits, tone, format ensure consistency.
- **Fallbacks**: Plaintext generators in code handle API failures.
- **Customizable**: Base `campaign.base_prompt_template` allows user edits.
- **JSON Structure**: Ensures parsable output for subject/body extraction.

These prompts drive the AI agent, enabling intelligent, context-aware email automation.
