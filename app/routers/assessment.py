from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas, ai_engine
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/assessment", tags=["assessment"])


def _get_role_or_404(db: Session, role_key: str) -> models.Role:
    role = db.query(models.Role).filter(models.Role.key == role_key).first()
    if not role:
        raise HTTPException(status_code=404, detail="Unknown role_key.")
    return role


def _to_result_schema(a: models.Assessment) -> schemas.AssessmentResult:
    return schemas.AssessmentResult(
        id=a.id,
        role_key=a.role_key,
        created_at=a.created_at,
        overall_score=a.overall_score,
        skills=a.skills,
        strengths=a.strengths,
        gaps=a.gaps,
        readiness=a.readiness,
        recommendation=a.recommendation,
        roadmap=a.roadmap,
    )


@router.get("/questions", response_model=list[schemas.QuestionOut])
def get_questions(role_key: str = Query(...), db: Session = Depends(get_db)):
    role = _get_role_or_404(db, role_key)
    questions = db.query(models.Question).filter(models.Question.topic.in_(role.topics)).all()
    return questions


@router.post("/submit", response_model=schemas.AssessmentResult)
def submit_assessment(
    payload: schemas.AssessmentSubmit,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    role = _get_role_or_404(db, payload.role_key)
    questions = db.query(models.Question).filter(models.Question.topic.in_(role.topics)).all()
    if not questions:
        raise HTTPException(status_code=400, detail="No questions configured for this role yet.")

    result = ai_engine.evaluate(role, questions, payload.answers)

    assessment = models.Assessment(
        user_id=current_user.id,
        role_key=role.key,
        answers={str(k): v for k, v in payload.answers.items()},
        skills=result["skills"],
        strengths=result["strengths"],
        gaps=result["gaps"],
        overall_score=result["overall_score"],
        readiness=result["readiness"],
        recommendation=result["recommendation"],
        roadmap=result["roadmap"],
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    # Keep the user's target role in sync with whatever they just assessed against
    current_user.target_role_key = role.key
    db.commit()

    return _to_result_schema(assessment)


@router.get("/latest", response_model=schemas.AssessmentResult)
def latest_assessment(
    role_key: str = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    assessment = (
        db.query(models.Assessment)
        .filter(models.Assessment.user_id == current_user.id, models.Assessment.role_key == role_key)
        .order_by(models.Assessment.created_at.desc())
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessment found for this role yet.")
    return _to_result_schema(assessment)
