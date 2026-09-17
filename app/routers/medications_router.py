"""
Medication interaction checker.

Uses a small static, curated table of known dangerous drug-pair
interactions (NOT AI-generated, for safety/accuracy). Matching is
case-insensitive substring matching on generic drug names.
"""

from itertools import combinations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth


router = APIRouter(
    prefix="/medications",
    tags=["Medications"]
)


# Curated list of known dangerous combinations.
INTERACTION_TABLE = [
    (
        "aspirin",
        "warfarin",
        "Increased risk of dangerous bleeding."
    ),
    (
        "ibuprofen",
        "warfarin",
        "Increased risk of dangerous bleeding."
    ),
    (
        "paracetamol",
        "alcohol",
        "Increased risk of liver damage."
    ),
    (
        "metformin",
        "alcohol",
        "Increased risk of lactic acidosis."
    ),
    (
        "sildenafil",
        "nitrate",
        "Can cause a dangerous drop in blood pressure."
    ),
    (
        "maoi",
        "ssri",
        "Risk of serotonin syndrome — a serious reaction."
    ),
    (
        "ace inhibitor",
        "potassium",
        "Risk of dangerously high potassium levels (hyperkalemia)."
    ),
    (
        "statin",
        "grapefruit",
        "Increased risk of statin toxicity/side effects."
    ),
    (
        "insulin",
        "alcohol",
        "Increased risk of dangerous low blood sugar (hypoglycemia)."
    ),
    (
        "tetracycline",
        "antacid",
        "Antacids can reduce absorption of the antibiotic, making it less effective."
    ),
]


def _check_pair(name_a: str, name_b: str):
    a = name_a.lower()
    b = name_b.lower()

    for drug_a, drug_b, warning in INTERACTION_TABLE:
        if (drug_a in a and drug_b in b) or (
            drug_a in b and drug_b in a
        ):
            return warning

    return None


def _compute_warnings(
    medications: list[models.Medication],
) -> list[schemas.MedicationWarning]:

    warnings = []

    for med_a, med_b in combinations(medications, 2):
        warning_text = _check_pair(
            med_a.name,
            med_b.name
        )

        if warning_text:
            warnings.append(
                schemas.MedicationWarning(
                    drug_a=med_a.name,
                    drug_b=med_b.name,
                    warning=warning_text,
                )
            )

    return warnings


@router.get(
    "",
    response_model=schemas.MedicationListOut
)
def list_medications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    meds = (
        db.query(models.Medication)
        .filter(
            models.Medication.user_id == current_user.id
        )
        .all()
    )

    warnings = _compute_warnings(meds)

    return schemas.MedicationListOut(
        medications=meds,
        warnings=warnings
    )


@router.post(
    "",
    response_model=schemas.MedicationListOut,
    status_code=201
)
def add_medication(
    payload: schemas.MedicationIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    entry = models.Medication(
        user_id=current_user.id,
        name=payload.name.strip()
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    meds = (
        db.query(models.Medication)
        .filter(
            models.Medication.user_id == current_user.id
        )
        .all()
    )

    warnings = _compute_warnings(meds)

    return schemas.MedicationListOut(
        medications=meds,
        warnings=warnings
    )


@router.delete(
    "/{medication_id}",
    status_code=204
)
def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    entry = (
        db.query(models.Medication)
        .filter(
            models.Medication.id == medication_id,
            models.Medication.user_id == current_user.id,
        )
        .first()
    )

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Medication not found"
        )

    db.delete(entry)
    db.commit()

    return None