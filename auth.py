from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, seed
from ..database import get_db
from ..auth import make_token, hash_password, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.AuthResponse)
def register(payload: schemas.RegisterIn, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
        birth_date=payload.birth_date,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.AuthResponse(token=make_token(user.id), user=user)


@router.post("/login", response_model=schemas.AuthResponse)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or user.password_hash != hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return schemas.AuthResponse(token=make_token(user.id), user=user)


@router.post("/demo", response_model=schemas.AuthResponse)
def demo_login(db: Session = Depends(get_db)):
    """Judges click 'Try Demo Journey' -- no registration needed."""
    seed.seed_astrologers(db)
    user = seed.get_or_create_demo_user(db)
    return schemas.AuthResponse(token=make_token(user.id), user=user)


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user
