from io import BytesIO
from typing import List, Dict

import pandas as pd

from ..schemas import ContactPreview, ConfirmContact


REQUIRED_COLUMN = "email"


def parse_contacts_file(file_bytes: bytes, filename: str) -> List[ContactPreview]:
    buffer = BytesIO(file_bytes)
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(buffer)
    else:
        df = pd.read_excel(buffer)

    df_cols = [c.strip().lower() for c in df.columns]

    rename_map = {}
    for col in df.columns:
        low = col.strip().lower()
        if low in ["email", "email address"]:
            rename_map[col] = "email"
        elif low in ["first name", "firstname", "fname", "name"]:
            rename_map[col] = "first_name"
        elif low in ["company", "company name"]:
            rename_map[col] = "company"
        elif low in ["role", "job title", "title"]:
            rename_map[col] = "role"
        elif low in ["hobbies", "interests"]:
            rename_map[col] = "hobbies"
        elif low in ["mbti", "mbti type"]:
            rename_map[col] = "mbti_type"

    df = df.rename(columns=rename_map)

    if "email" not in df.columns:
        raise ValueError(f"Columns found: {sorted(df.columns.tolist())}. One must be renamed to 'email' (case-insensitive variants include: 'email address', 'email', 'mail', etc.).")

    preview_rows: List[ContactPreview] = []
    for _, row in df.head(20).iterrows():
        preview_rows.append(
            ContactPreview(
                email=str(row.get("email", "")).strip(),
                first_name=row.get("first_name"),
                company=row.get("company"),
                role=row.get("role"),
                hobbies=row.get("hobbies"),
                mbti_type=row.get("mbti_type"),
            )
        )

    return preview_rows


def confirm_contacts_from_payload(contacts: List[ConfirmContact]) -> List[Dict]:
    rows: List[Dict] = []
    for c in contacts:
        if not c.email:
            continue
        rows.append(
            {
                "email": c.email,
                "first_name": c.first_name,
                "company": c.company,
                "role": c.role,
                "hobbies": c.hobbies,
                "mbti_type": c.mbti_type,
            }
        )
    return rows
