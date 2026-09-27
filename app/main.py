from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine, SessionLocal
from app import seed_data
from app.routers import auth, roles, assessment, progress, report

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    seed_data.seed(db)

app = FastAPI(title="SkillSense AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(assessment.router)
app.include_router(progress.router)
app.include_router(report.router)


@app.get("/health")
def health():
    return {"status": "ok"}
