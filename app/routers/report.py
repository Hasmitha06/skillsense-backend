from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app import models, schemas, reports
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/report", tags=["report"])


def _latest_or_404(db: Session, user: models.User, role_key: str) -> models.Assessment:
    a = (
        db.query(models.Assessment)
        .filter(models.Assessment.user_id == user.id, models.Assessment.role_key == role_key)
        .order_by(models.Assessment.created_at.desc())
        .first()
    )
    if not a:
        raise HTTPException(status_code=404, detail="No assessment found for this role yet.")
    return a


@router.get("/json", response_model=schemas.AssessmentResult)
def report_json(
    role_key: str = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    a = _latest_or_404(db, current_user, role_key)
    return schemas.AssessmentResult(
        id=a.id, role_key=a.role_key, created_at=a.created_at, overall_score=a.overall_score,
        skills=a.skills, strengths=a.strengths, gaps=a.gaps, readiness=a.readiness,
        recommendation=a.recommendation, roadmap=a.roadmap,
    )


@router.get("/pdf")
def report_pdf(
    role_key: str = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    role = db.query(models.Role).filter(models.Role.key == role_key).first()
    if not role:
        raise HTTPException(status_code=404, detail="Unknown role_key.")
    a = _latest_or_404(db, current_user, role_key)
    buf = reports.build_pdf(current_user, role, a)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=SkillSense_Performance_Report.pdf"},
    )


@router.get("/excel")
def report_excel(
    role_key: str = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    role = db.query(models.Role).filter(models.Role.key == role_key).first()
    if not role:
        raise HTTPException(status_code=404, detail="Unknown role_key.")
    a = _latest_or_404(db, current_user, role_key)
    buf = reports.build_excel(role, a)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=SkillSense_Skill_Matrix.xlsx"},
    )
