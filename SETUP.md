# Local Setup and Run

## Prerequisites
- Python 3.11+
- Node.js 18+
- Database: PostgreSQL (recommended) or SQLite (for dev)
- API Keys: SendGrid (email sending) and Groq (AI generation)

## Backend Setup
Navigate to the backend directory and set up the Python environment:

```bash
cd backend
python -m venv .venv  # Create virtual environment
source .venv/bin/activate  # Activate (Windows: .venv\Scripts\activate)
pip install -r requirements.txt  # Install dependencies
```

Alternatively, if using uv for faster installs:
```bash
uv sync
```

### Environment Configuration
Create a `.env`


Key variables to set:
- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:pass@localhost/db`)
- `SENDGRID_API_KEY`: Your SendGrid API key
- `GROQ_API_KEY`: Your Groq API key for AI
- `SENDGRID_FROM_EMAIL`: Verified sending email address
- Other settings as needed

### Database Initialization
For PostgreSQL, run migrations:
```bash
alembic upgrade head
```

For a clean start or to reset, you can drop the `email_instances` table if schema issues arise.

### Run Backend
Start the FastAPI server:
```bash
uvicorn app.main:app --reload
# Server runs on http://localhost:8000
```

## Frontend Setup
In the frontend directory:

```bash
cd frontend
npm install
npm run dev
```

The React app will be available at `http://localhost:5173` (Vite dev server).

## Full Application Usage
1. Open frontend in browser.
2. Upload CSV/Excel with contacts (must have 'email' column, others auto-detected).
3. Review and confirm to create campaign.
4. Generate AI-powered emails for contacts (idempotent, no duplicates).
5. Edit drafts, then send via SendGrid.
6. Monitor status and analytics in the dashboard.

## Notes
- Use `uv` where possible for faster dependency management.
- Ensure API keys are valid to avoid feature failures.
- For production, configure proper database and reverse proxy (e.g., NGINX).
