import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./fitbuddy.db"
)

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }
else:
    connect_args = {}


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    name = Column(String(100), nullable=False)

    age = Column(Integer, nullable=False)

    weight = Column(Float, nullable=False)

    goal = Column(String(100), nullable=False)

    intensity = Column(String(100), nullable=False)

    experience = Column(
        String(100),
        nullable=False,
        default="Beginner"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    plans = relationship(
        "WorkoutPlan",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class WorkoutPlan(Base):

    __tablename__ = "workout_plans"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        String(100),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )

    original_plan = Column(
        Text,
        nullable=False
    )

    updated_plan = Column(
        Text,
        nullable=True
    )

    nutrition_tip = Column(
        Text,
        nullable=True
    )

    feedback = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="plans"
    )


Base.metadata.create_all(
    bind=engine
)


def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def save_user(
    db: Session,
    user_id: str,
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
    experience: str = "Beginner"
):

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if user:

        user.name = name
        user.age = age
        user.weight = weight
        user.goal = goal
        user.intensity = intensity
        user.experience = experience

    else:

        user = User(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
            experience=experience
        )

        db.add(user)

    db.commit()
    db.refresh(user)

    return user


def save_plan(
    db: Session,
    user_id: str,
    original_plan: str,
    nutrition_tip: str = ""
):

    plan = WorkoutPlan(
        user_id=user_id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip
    )

    db.add(plan)

    db.commit()
    db.refresh(plan)

    return plan


def update_plan(
    db: Session,
    user_id: str,
    updated_plan: str,
    feedback: str
):

    plan = (
        db.query(WorkoutPlan)
        .filter(
            WorkoutPlan.user_id == user_id
        )
        .order_by(
            WorkoutPlan.id.desc()
        )
        .first()
    )

    if not plan:
        return None

    plan.updated_plan = updated_plan
    plan.feedback = feedback
    plan.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(plan)

    return plan


def get_user(
    db: Session,
    user_id: str
):

    return (
        db.query(User)
        .filter(
            User.user_id == user_id
        )
        .first()
    )


def get_latest_plan(
    db: Session,
    user_id: str
):

    return (
        db.query(WorkoutPlan)
        .filter(
            WorkoutPlan.user_id == user_id
        )
        .order_by(
            WorkoutPlan.id.desc()
        )
        .first()
    )


def get_all_users(
    db: Session
):

    return (
        db.query(User)
        .order_by(
            User.id.desc()
        )
        .all()
    )