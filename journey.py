from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, ai
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/api/journey", tags=["journey"])


@router.get("", response_model=schemas.JourneyOut)
def get_journey(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Prefer the most recent active goal, but fall back to the most recently
    # completed one so the Journey screen still shows something meaningful
    # right after a user finishes their last action (rather than going blank).
    goal = (
        db.query(models.Goal)
        .filter(models.Goal.user_id == current_user.id, models.Goal.status == "active")
        .order_by(models.Goal.created_at.desc())
        .first()
    )
    if not goal:
        goal = (
            db.query(models.Goal)
            .filter(models.Goal.user_id == current_user.id)
            .order_by(models.Goal.created_at.desc())
            .first()
        )

    events = (
        db.query(models.JourneyEvent)
        .filter(models.JourneyEvent.user_id == current_user.id)
        .order_by(models.JourneyEvent.created_at.asc())
        .all()
    )

    has_consultation = any(e.type == "consultation_completed" for e in events)
    has_goal = goal is not None
    first_action_done = False
    second_action_done = False
    if goal:
        completed = [a for a in goal.actions if a.is_completed]
        first_action_done = len(completed) >= 1
        second_action_done = len(completed) >= 2
    has_upcoming_date = db.query(models.ImportantDate).filter(
        models.ImportantDate.user_id == current_user.id
    ).count() > 0
    has_followup = any("Follow-up" in (dt.title or "") for dt in db.query(models.ImportantDate).filter(
        models.ImportantDate.user_id == current_user.id
    ).all())

    milestones = [
        {"key": "consultation", "label": "Consultation completed", "done": has_consultation},
        {"key": "goal", "label": "Goal created", "done": has_goal},
        {"key": "action1", "label": "First action completed", "done": first_action_done},
        {"key": "action2", "label": "Second action completed", "done": second_action_done},
        {"key": "date", "label": "Important date approaching", "done": has_upcoming_date},
        {"key": "followup", "label": "Follow-up consultation", "done": has_followup},
    ]

    category = goal.category if goal else "Career"
    today_insight = ai.generate_daily_insight(category)
    today_action = next((a for a in (goal.actions if goal else []) if not a.is_completed), None)

    return schemas.JourneyOut(
        goal=goal,
        progress_percent=goal.progress if goal else 0,
        milestones=milestones,
        today_insight=today_insight,
        today_action=today_action,
        events=list(reversed(events)),
    )


dates_router = APIRouter(prefix="/api/important-dates", tags=["important-dates"])


@dates_router.get("", response_model=List[schemas.ImportantDateOut])
def list_dates(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.ImportantDate).filter(
        models.ImportantDate.user_id == current_user.id
    ).order_by(models.ImportantDate.date.asc()).all()


@dates_router.post("", response_model=schemas.ImportantDateOut)
def create_date(
    payload: schemas.ImportantDateCreateIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    d = models.ImportantDate(user_id=current_user.id, **payload.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


@dates_router.post("/{date_id}/toggle-reminder", response_model=schemas.ImportantDateOut)
def toggle_reminder(
    date_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    d = db.query(models.ImportantDate).filter(
        models.ImportantDate.id == date_id, models.ImportantDate.user_id == current_user.id
    ).first()
    if not d:
        raise HTTPException(status_code=404, detail="Date not found")
    d.reminder_enabled = not d.reminder_enabled
    if d.reminder_enabled:
        db.add(models.Notification(
            user_id=current_user.id,
            message=f"Reminder set for '{d.title}' on {d.date}.",
            type="reminder",
        ))
    db.commit()
    db.refresh(d)
    return d


share_router = APIRouter(prefix="/api/share-card", tags=["share"])


@share_router.post("", response_model=schemas.ShareCardOut)
def generate_share_card(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    goal = db.query(models.Goal).filter(
        models.Goal.user_id == current_user.id
    ).order_by(models.Goal.created_at.desc()).first()
    completed_actions = 0
    total_actions = 0
    if goal:
        completed_actions = sum(1 for a in goal.actions if a.is_completed)
        total_actions = len(goal.actions)

    stats = {
        "zodiac_sign": current_user.zodiac_sign or "\u2728",
        "goal_title": goal.title if goal else "Starting my journey",
        "progress_percent": goal.progress if goal else 0,
        "actions_completed": completed_actions,
        "actions_total": total_actions,
    }
    card = models.ShareCard(
        user_id=current_user.id,
        headline=f"{current_user.name}'s Astro Journey",
        stats=stats,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@share_router.get("/latest", response_model=schemas.ShareCardOut)
def latest_share_card(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    card = db.query(models.ShareCard).filter(
        models.ShareCard.user_id == current_user.id
    ).order_by(models.ShareCard.created_at.desc()).first()
    if not card:
        raise HTTPException(status_code=404, detail="No share card yet")
    return card


notifications_router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@notifications_router.get("", response_model=List[schemas.NotificationOut])
def list_notifications(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id
    ).order_by(models.Notification.created_at.desc()).all()


@notifications_router.post("/{notification_id}/read", response_model=schemas.NotificationOut)
def mark_read(notification_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    n = db.query(models.Notification).filter(
        models.Notification.id == notification_id, models.Notification.user_id == current_user.id
    ).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.is_read = True
    db.commit()
    db.refresh(n)
    return n


analytics_router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@analytics_router.get("", response_model=schemas.AnalyticsOut)
def get_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    consultations = db.query(models.Consultation).filter(
        models.Consultation.user_id == current_user.id
    ).all()
    goals = db.query(models.Goal).filter(models.Goal.user_id == current_user.id).all()
    all_actions = [a for g in goals for a in g.actions]
    completed_actions = [a for a in all_actions if a.is_completed]

    category_breakdown = {}
    for g in goals:
        category_breakdown[g.category] = category_breakdown.get(g.category, 0) + 1

    active_goal = next((g for g in goals if g.status == "active"), None)

    return schemas.AnalyticsOut(
        total_consultations=len(consultations),
        total_goals=len(goals),
        active_goals=sum(1 for g in goals if g.status == "active"),
        completed_actions=len(completed_actions),
        total_actions=len(all_actions),
        current_streak_days=min(len(completed_actions), 7),
        journey_progress=active_goal.progress if active_goal else 0,
        category_breakdown=category_breakdown,
    )
