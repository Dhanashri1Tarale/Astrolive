from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, seed
from ..database import get_db

router = APIRouter(prefix="/api/astrologers", tags=["astrologers"])


@router.get("", response_model=List[schemas.AstrologerOut])
def list_astrologers(specialty: Optional[str] = None, db: Session = Depends(get_db)):
    seed.seed_astrologers(db)
    q = db.query(models.Astrologer)
    if specialty:
        q = q.filter(models.Astrologer.specialty == specialty)
    return q.all()


@router.get("/{astrologer_id}", response_model=schemas.AstrologerOut)
def get_astrologer(astrologer_id: str, db: Session = Depends(get_db)):
    return db.query(models.Astrologer).filter(models.Astrologer.id == astrologer_id).first()
