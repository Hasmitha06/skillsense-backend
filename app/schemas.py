from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ---- Auth ----
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    target_role_key: str | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---- Roles ----
class RoleOut(BaseModel):
    key: str
    name: str
    blurb: str
    color: str
    threshold: float

    class Config:
        from_attributes = True


class SetRoleIn(BaseModel):
    role_key: str


# ---- Questions ----
class QuestionOut(BaseModel):
    id: int
    topic: str
    prompt: str
    options: list[str]

    class Config:
        from_attributes = True


# ---- Assessment ----
class AssessmentSubmit(BaseModel):
    role_key: str
    answers: dict[int, int]  # question_id -> selected option index


class Strength(BaseModel):
    topic: str
    detail: str


class Gap(BaseModel):
    topic: str
    pattern: str
    severity: str  # "high" | "medium"


class Skill(BaseModel):
    name: str
    score: float


class Recommendation(BaseModel):
    headline: str
    detail: str
    actions: list[str]


class RoadmapPhase(BaseModel):
    window: str
    goals: list[str]


class Readiness(BaseModel):
    score: float
    threshold: float
    label: str
    note: str


class AssessmentResult(BaseModel):
    id: int
    role_key: str
    created_at: datetime
    overall_score: float
    skills: list[Skill]
    strengths: list[Strength]
    gaps: list[Gap]
    readiness: Readiness
    recommendation: Recommendation
    roadmap: list[RoadmapPhase]

    class Config:
        from_attributes = True


class ProgressPoint(BaseModel):
    topic: str
    previous: float
    current: float
