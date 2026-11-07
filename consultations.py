from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, ai
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/api/consultations", tags=["consultations"])


@router.get("", response_model=List[schemas.ConsultationOut])
def list_consultations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Consultation)
        .filter(models.Consultation.user_id == current_user.id)
        .order_by(models.Consultation.created_at.desc())
        .all()
    )


@router.get("/{consultation_id}", response_model=schemas.ConsultationOut)
def get_consultation(
    consultation_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    c = db.query(models.Consultation).filter(
        models.Consultation.id == consultation_id,
        models.Consultation.user_id == current_user.id,
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return c


@router.post("", response_model=schemas.ConsultationOut)
def create_consultation(
    payload: schemas.ConsultationCreateIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    astrologer = db.query(models.Astrologer).filter(
        models.Astrologer.id == payload.astrologer_id
    ).first()
    if not astrologer:
        raise HTTPException(status_code=404, detail="Astrologer not found")

    transcript = (
        f"{current_user.name}: {payload.user_message}\n"
        f"{astrologer.name}: Thank you for sharing that. Based on your current "
        f"planetary transits, this is a meaningful period for {payload.topic.lower()} "
        f"matters. Let's translate this into a clear, actionable path forward."
    )

    consultation = models.Consultation(
        user_id=current_user.id,
        astrologer_id=astrologer.id,
        topic=payload.topic,
        transcript=transcript,
        status="completed",
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    ai_result = ai.generate_consultation_summary(transcript, payload.topic)
    insight = models.Insight(
        consultation_id=consultation.id,
        summary=ai_result["summary"],
        key_points=ai_result["key_points"],
        category=ai_result.get("category", payload.topic),
    )
    db.add(insight)

    db.add(models.JourneyEvent(
        user_id=current_user.id,
        type="consultation_completed",
        title="Consultation completed",
        description=f"{payload.topic} reading with {astrologer.name}",
    ))
    db.commit()
    db.refresh(consultation)
    return consultation


@router.post("/{consultation_id}/save-to-memory", response_model=schemas.InsightOut)
def save_to_memory(
    consultation_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """AstroLive Memory: persist this consultation's insight so future Journey
    screens can reference it."""
    consultation = db.query(models.Consultation).filter(
        models.Consultation.id == consultation_id,
        models.Consultation.user_id == current_user.id,
    ).first()
    if not consultation or not consultation.insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    consultation.insight.saved_to_memory = True
    db.add(models.JourneyEvent(
        user_id=current_user.id,
        type="memory_saved",
        title="Saved to AstroLive Memory",
        description=consultation.insight.summary[:120],
    ))
    db.commit()
    db.refresh(consultation.insight)
    return consultation.insight
