"""
Standalone endpoint for govt scheme lookup.
"""
from fastapi import APIRouter, HTTPException

from app import schemas, schemes_engine

router = APIRouter(prefix="/schemes", tags=["Govt Schemes"])


@router.get("/{condition_text}", response_model=schemas.SchemeListOut)
def get_schemes(condition_text: str):
    condition_key, schemes = schemes_engine.find_schemes(condition_text)
    if not condition_key:
        raise HTTPException(status_code=404, detail="No matching government scheme found for this condition")

    return schemas.SchemeListOut(
        condition=condition_key,
        schemes=[schemas.SchemeOut(condition=condition_key, **s) for s in schemes],
    )