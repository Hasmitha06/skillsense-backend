from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=list[schemas.ProgressPoint])
def get_progress(
    role_key: str = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    assessments = (
        db.query(models.Assessment)
        .filter(models.Assessment.user_id == current_user.id, models.Assessment.role_key == role_key)
        .order_by(models.Assessment.created_at.desc())
        .limit(2)
        .all()
    )

    if len(assessments) < 2:
        return []  # not enough history yet — frontend can prompt the user to retest

    current, previous = assessments[0], assessments[1]
    prev_scores = {s["name"]: s["score"] for s in previous.skills}
    curr_scores = {s["name"]: s["score"] for s in current.skills}

    topics = curr_scores.keys()
    return [
        schemas.ProgressPoint(topic=t, previous=prev_scores.get(t, 0), current=curr_scores.get(t, 0))
        for t in topics
    ]
