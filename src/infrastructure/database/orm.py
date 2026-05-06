import logging
from datetime import datetime
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Enum,
    Float,
    Boolean,
    DateTime,
    JSON,
    ForeignKey,
    event,
)
from sqlalchemy.orm import registry, class_mapper
from sqlalchemy.orm.exc import UnmappedClassError

from src.domain.models import AnalysisStatus
from src.domain.models.user import UserRoles
from src.domain.models.meal_log import MealType, MealSource
from src.domain.models.goal import GoalType
from src.domain import models

logger = logging.getLogger(__name__)
metadata = MetaData()
mapper_registry = registry()


users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(255), nullable=False),
    Column("hashed_password", String(255), nullable=False),
    Column("email", String(255), unique=True, nullable=False),
    Column(
        "role", Enum(UserRoles), nullable=False, server_default=UserRoles.user.value
    ),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
)

meal_logs = Table(
    "meal_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    ),
    Column("name", String(255), nullable=False),
    Column("calories", Float, nullable=False),
    Column("protein", Float, nullable=False),
    Column("fat", Float, nullable=False),
    Column("carbs", Float, nullable=False),
    Column("meal_type", Enum(MealType), nullable=False),
    Column("source", Enum(MealSource), nullable=False, default=MealSource.manual),
    Column("eaten_at", DateTime, nullable=False, default=datetime.now),
    Column("s3_key", String(512), nullable=True),
)

goals = Table(
    "goals",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    ),
    Column("goal_type", Enum(GoalType), nullable=False),
    Column("target_kg", Float, nullable=False),
    Column("current_weight_kg", Float, nullable=False),
    Column("daily_calories", Float, nullable=False),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
)

preferences = Table(
    "preferences",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    ),
    Column("diet_type", String(64), default="balanced"),
    Column("meals_per_day", Integer, default=3),
    Column("water_goal_ml", Integer, default=2000),
    Column("notifications_enabled", Boolean, default=True),
)

privacy_settings = Table(
    "privacy_settings",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    ),
    Column("analytics_enabled", Boolean, default=True),
    Column("crash_reports_enabled", Boolean, default=True),
    Column("personalization_enabled", Boolean, default=True),
)

analysis_requests = Table(
    "analysis_requests",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    ),
    Column("s3_key", String(512), nullable=False),
    Column(
        "status", Enum(AnalysisStatus), nullable=False, default=AnalysisStatus.pending
    ),
    Column("meal_log_id", Integer, ForeignKey("meal_logs.id"), nullable=True),
    Column("result", JSON, nullable=True),
    Column("created_at", DateTime, default=datetime.now, nullable=False),
)


def _is_mapped(model) -> bool:
    try:
        class_mapper(model)
        return True
    except UnmappedClassError:
        return False


def start_mappers():
    if _is_mapped(models.User):
        return
    mapper_registry.map_imperatively(models.User, users)
    mapper_registry.map_imperatively(models.MealLog, meal_logs)
    mapper_registry.map_imperatively(models.Goal, goals)
    mapper_registry.map_imperatively(models.Preferences, preferences)
    mapper_registry.map_imperatively(models.PrivacySettings, privacy_settings)
    mapper_registry.map_imperatively(models.AnalysisRequest, analysis_requests)
    logger.info("ORM mappers initialized")


@event.listens_for(models.User, "load")
def receive_load_user(obj, _):
    obj.events = []


@event.listens_for(models.MealLog, "load")
def receive_load_meal(obj, _):
    obj.events = []


@event.listens_for(models.Goal, "load")
def receive_load_goal(obj, _):
    obj.events = []


@event.listens_for(models.Preferences, "load")
def receive_load_prefs(obj, _):
    obj.events = []


@event.listens_for(models.PrivacySettings, "load")
def receive_load_privacy(obj, _):
    obj.events = []


@event.listens_for(models.AnalysisRequest, "load")
def receive_load_analysis(obj, _):
    obj.events = []
