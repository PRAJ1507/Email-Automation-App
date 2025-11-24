from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routers import upload, campaigns, emails, webhooks

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Email Automation App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(emails.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
