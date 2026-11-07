from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, ai
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/api/goals", tags=["goals"])


def _recalc_progress(goal: models.Goal):
    if not goal.actions:
        goal.progress = 0
        return
    done = sum(1 for a in goal.actions if a.is_completed)
    goal.progress = round(100 * done / len(goal.actions))
    if goal.progress == 100:
        goal.status = "completed"


@router.get("", response_model=List[schemas.GoalOut])
def list_goals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Goal).filter(models.Goal.user_id == current_user.id).all()


@router.post("", response_model=schemas.GoalOut)
def create_goal(
    payload: schemas.GoalCreateIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    goal = models.Goal(
        user_id=current_user.id,
        insight_id=payload.insight_id,
        title=payload.title,
        category=payload.category,
        description=payload.description,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)

    action_titles = payload.actions or ai.suggest_actions(payload.category)
    for i, title in enumerate(action_titles):
        db.add(models.Action(goal_id=goal.id, title=title, order=i))

    db.add(models.JourneyEvent(
        user_id=current_user.id,
        type="goal_created",
        title="Goal created",
        description=payload.title,
    ))
    db.commit()
    db.refresh(goal)
    return goal


@router.post("/actions/{action_id}/complete", response_model=schemas.ActionOut)
def complete_action(
    action_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    from datetime import datetime
    action = db.query(models.Action).join(models.Goal).filter(
        models.Action.id == action_id,
        models.Goal.user_id == current_user.id,
    ).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    action.is_completed = not action.is_completed
    action.completed_at = datetime.utcnow() if action.is_completed else None
    db.commit()

    goal = db.query(models.Goal).filter(models.Goal.id == action.goal_id).first()
    _recalc_progress(goal)

    if action.is_completed:
        db.add(models.JourneyEvent(
            user_id=current_user.id,
            type="action_completed",
            title="Action completed",
            description=action.title,
        ))
    db.commit()
    db.refresh(action)
    return action
