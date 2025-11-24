from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

from ..schemas import UploadContactsResponse, ConfirmContactsRequest, CampaignResponse, ContactPreview
from ..db import get_db
from ..models import Campaign, Contact, SequenceStep
from ..services.contacts_import import parse_contacts_file, confirm_contacts_from_payload

from fastapi import Depends
from sqlalchemy.orm import Session

router = APIRouter(tags=["upload"])


@router.post("/upload-contacts", response_model=UploadContactsResponse)
async def upload_contacts(
    file: UploadFile = File(...),
):
    try:
        contents = await file.read()
        preview_rows = parse_contacts_file(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")

    inferred_columns = ["email", "first_name", "company", "role", "hobbies", "mbti_type"]
    return UploadContactsResponse(preview_rows=preview_rows, inferred_columns=inferred_columns)


@router.post("/contacts/confirm", response_model=CampaignResponse)
async def confirm_contacts(
    payload: ConfirmContactsRequest,
    db: Session = Depends(get_db),
):
    rows = confirm_contacts_from_payload(payload.contacts)
    if not rows:
        raise HTTPException(status_code=400, detail="No valid contacts")

    campaign = Campaign(
        name=payload.campaign_name,
        product_name=payload.product_name,
        product_description=payload.product_description,
    )
    db.add(campaign)
    db.flush()

    # default 3-step sequence
    steps = [
        SequenceStep(campaign_id=campaign.id, step_number=1, offset_days=0, name="Initial email"),
        SequenceStep(campaign_id=campaign.id, step_number=2, offset_days=3, name="Follow-up"),
        SequenceStep(campaign_id=campaign.id, step_number=3, offset_days=7, name="Final reminder"),
    ]
    db.add_all(steps)

    contacts = [
        Contact(
            email=row["email"],
            first_name=row.get("first_name"),
            company=row.get("company"),
            role=row.get("role"),
            hobbies=row.get("hobbies"),
            mbti_type=row.get("mbti_type"),
        )
        for row in rows
    ]
    db.add_all(contacts)

    db.commit()
    db.refresh(campaign)

    return CampaignResponse(
        id=campaign.id,
        name=campaign.name,
        product_name=campaign.product_name or "",
        product_description=campaign.product_description,
    )


@router.get("/contacts", response_model=List[ContactPreview])
def list_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return [
        ContactPreview(
            id=c.id,
            email=c.email,
            first_name=c.first_name,
            company=c.company,
            role=c.role,
            hobbies=c.hobbies,
            mbti_type=c.mbti_type,
        )
        for c in contacts
    ]
