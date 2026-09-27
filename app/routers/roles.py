from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[schemas.RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return db.query(models.Role).all()
