# Key Features Implementation

This document outlines the implementation of core features in the email automation app.

## 1. File Upload & Contact Import

### Frontend (`FileUpload.jsx`, `UploadPage.jsx`)
- Accepts CSV or Excel files via `<input type="file">`.
- Basic validation: checks file presence before upload.
- Sends file as `FormData` to `/api/upload-contacts`.

### Backend (`upload.py`, `contacts_import.py`)
- Endpoint: `POST /upload-contacts`
- Parses up to 20 rows for preview using Pandas.
- Auto-renames columns: Maps common variants (e.g., "Email Address" → "email", "First Name" → "first_name").
- Validates required "email" column presence.
- Returns `UploadContactsResponse` with mapped preview rows and column suggestions.
- On `POST /contacts/confirm`, saves to DB: creates `Campaign`, `SequenceStep`s (default 3-step sequence), and `Contact` records.

### Error Handling
- Generic 400 for parse failures (e.g., invalid format, missing email).
- Rolls back transactions on failures.

## 2. AI Integration (GROQ/OpenAI Proxy)

### Backend (`services/groq_llm.py`, `agent.py`)
- LangChain `ChatGroq` wrapper with configurable model (`llama3-8b-8192`), temperature, and token limits.
- Agent built with LangChain's `create_agent` using tools for email generation, classification, and sending.

### Key Tools
- `generate_sequence_email_tool`: Generates subject/body for contact in sequence step. Uses chain with prompt + dynamic data (product, recipient profile, step).
- `classify_reply_tool`: Classifies incoming replies as simple (auto-reply) or complex.
- `draft_reply_tool`: Drafts responses for complex replies.
- `send_email_tool`: Updates status and timestamps on send.

### Prompt Engineering
- Base template per campaign allows customization.
- Injects: product name/desc, contact firstName/company/role/hobbies/MBTI, step number/name, sender name.
- Structured JSON output for subject/body extraction.
- Fallback plaintext generators for reliability.

### Sequence Logic
- Creates 1 email per (contact × step) idempottently.
- Regenerate flag deletes non-reply emails to reset.

## 3. Email Sending & Tracking

### Sending (`email_service.py`, `emails.py`)
- `send_email_via_sendgrid`: Composes MIME email, sends via SendGrid API.
- Tracks `provider_message_id` for webhook matching.
- `POST /api/emails/send`: Batch sends by campaign/step, updates `sent_at`, status to "sent".

### Webhook Tracking (`webhooks.py`)
- `/webhook/sendgrid`: Receives events (delivered, open, click, bounce, spam, reply).
- Creates `EmailEvent` records with metadata.
- Updates `EmailInstance` status (e.g., delivered, replied).

### Analytics (`campaigns.py`)
- `GET /api/campaigns/{id}`: Aggregates counts from `EmailInstance` and event counts via joins.
- Returns summary: totals, sent emails with engagement metrics.

## Architecture Overview

### Backend
- **Framework**: FastAPI with Pydantic for schemas.
- **DB**: SQLAlchemy ORM with PostgreSQL/SQLite.
- **AI**: Groq via LangChain agents/tools.
- **Email**: SendGrid API + webhooks for tracking.
- **Security**: CORS, rate limiting stubs.

### Frontend
- **Framework**: React with Vite.
- **Routing**: React Router.
- **UI**: Components (FileUpload, EmailEditor, StatusTable) with Tailwind CSS.
- **API**: Axios calls to FastAPI endpoints.

### Data Flow
1. Upload → Parse → Confirm → Campaign Creation.
2. Generate → AI Drafts (idempotent).
3. Edit/Send → Status/Events Tracking → Analytics.

This implementation ensures scalability, error resilience, and personalization via AI.
