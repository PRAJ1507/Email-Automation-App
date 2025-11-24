# Email Automation App

An AI-powered email marketing automation tool that helps users create personalized email sequences, manage contacts, and track campaign performance.

## Features

- **Contact Import**: Upload CSV/Excel files with contact information
- **AI-Powered Email Generation**: Generate personalized emails using Groq/OpenAI
- **Sequence Management**: Create and manage multi-step email campaigns
- **Email Tracking**: Monitor delivery, opens, clicks, and replies via SendGrid
- **Analytics Dashboard**: View campaign performance and engagement metrics
- **Reply Handling**: Automatic classification and drafting of responses

## Tech Stack

**Backend:**
- Python 3.11+ with FastAPI
- SQLAlchemy ORM (PostgreSQL/SQLite)
- LangChain + Groq for AI
- SendGrid for email delivery
- APScheduler for background tasks

**Frontend:**
- React with Vite
- Tailwind CSS for styling
- Axios for API calls

**Infrastructure:**
- Docker support (planned)
- Webhook integration for real-time updates

## Quick Setup (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Database: PostgreSQL (recommended) or SQLite
- API Keys: Groq (AI) and SendGrid (email)

### Backend Installation
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Or: uv sync (if using uv)
```

### Environment Setup
1. `.env`
2. Fill in your API keys:
   - `DATABASE_URL` (e.g., `postgresql://user:pass@localhost/db`)
   - `GROQ_API_KEY`
   - `SENDGRID_API_KEY` and `SENDGRID_FROM_EMAIL`

### Run Database Migrations
```bash
alembic upgrade head
```

### Start Backend
```bash
uvicorn app.main:app --reload
# API available at http://localhost:8000
```

### Frontend Installation
```bash
cd frontend
npm install
npm run dev
# App available at http://localhost:5173
```

### Usage
1. **Upload Contacts**: Upload CSV/Excel with email column and optional name/company details
2. **Campaign Setup**: Review and confirm contacts to create email campaign
3. **Generate Emails**: AI generates personalized drafts for each contact in the sequence
4. **Send & Track**: Send emails and monitor performance
5. **Analyze Results**: View click/open rates in the dashboard

## Detailed Documentation

- **[Setup Guide](backend/SETUP.md)**: Complete installation and configuration
- **[Implementation](backend/IMPLEMENTATION.md)**: Architecture and feature details
- **[AI Prompts](backend/PROMPTS.md)**: Sample prompts for email generation

## Project Structure

```
email-automation-app/
├── backend/
│   ├── app/
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # Business logic (AI, email, imports)
│   │   ├── models.py    # Database models
│   │   ├── schemas.py   # Pydantic models
│   │   └── main.py      # FastAPI app
│   ├── requirements.txt
│   ├── SETUP.md
│   ├── IMPLEMENTATION.md
│   └── PROMPTS.md
└── frontend/
    ├── src/
    │   ├── pages/       # Main app pages
    │   ├── components/  # Reusable UI components
    │   └── lib/         # API utilities
    └── package.json
```

## API Overview

- **POST /api/upload-contacts**: Upload and parse contact files
- **POST /api/contacts/confirm**: Create campaign from contacts
- **POST /api/campaigns/{id}/generate-emails**: AI generate email drafts
- **POST /api/emails/send**: Send bulk emails
- **GET /api/campaigns/{id}**: Get campaign status and analytics
- **POST /api/webhook/sendgrid**: Receive SendGrid events

## Configuration

Edit `backend/app/config.py` for:
- AI model settings (temperature, max tokens)
- Email sequence defaults (3-step: Initial → Follow-up → Final)
- Base prompt templates for customization

## Development

- Use `uvicorn` with `--reload` for backend live reloading
- Frontend uses Vite HMR (Hot Module Replacement)
- Code formatting: Prettier for JS, Black for Python

## Contribution

1. Fork the repository
2. Create a feature branch
3. Commit changes with clear messages
4. Submit a pull request

- Add tests for new features
- Update documentation for API changes
- Ensure compatibility with existing workflows

## License

MIT License - feel free to use for commercial and personal projects.

## Support

For issues or questions:
- Check the [backend/SETUP.md](backend/SETUP.md) for troubleshooting
- Ensure API keys are valid and databases connected
- Review logs for debugging hints

Built with ❤️ using FastAPI, React, and AI
