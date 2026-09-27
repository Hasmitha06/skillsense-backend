from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    target_role_key = Column(String, ForeignKey("roles.key"), nullable=True)
    created_at = Column(DateTime, default=utcnow)

    assessments = relationship("Assessment", back_populates="user")


class Role(Base):
    __tablename__ = "roles"

    key = Column(String, primary_key=True)  # e.g. "java", "python", "ai", "frontend"
    name = Column(String, nullable=False)
    blurb = Column(String, nullable=False)
    color = Column(String, nullable=False)
    topics = Column(JSON, nullable=False)  # list of topic names relevant to this role
    threshold = Column(Float, default=80.0)  # readiness threshold (%)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    options = Column(JSON, nullable=False)  # list[str]
    correct_index = Column(Integer, nullable=False)
    mistake_pattern = Column(String, nullable=False)  # shown as a gap explanation when answered wrong


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_key = Column(String, ForeignKey("roles.key"), nullable=False)
    created_at = Column(DateTime, default=utcnow)

    answers = Column(JSON, nullable=False)  # {question_id: selected_index}
    skills = Column(JSON, nullable=False)  # [{name, score}]
    strengths = Column(JSON, nullable=False)  # [{topic, detail}]
    gaps = Column(JSON, nullable=False)  # [{topic, pattern, severity}]
    overall_score = Column(Float, nullable=False)
    readiness = Column(JSON, nullable=False)  # {score, threshold, label, note}
    recommendation = Column(JSON, nullable=False)  # {headline, detail, actions}
    roadmap = Column(JSON, nullable=False)  # [{window, goals}]

    user = relationship("User", back_populates="assessments")
