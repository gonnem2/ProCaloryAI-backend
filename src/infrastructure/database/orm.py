from datetime import datetime

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Enum,
    event,
    Float,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import registry, class_mapper
from sqlalchemy.orm.exc import UnmappedClassError

from src.domain.models import AnalysisStatus
from src.domain.models.user import UserRoles
from src.domain import models

metadata = MetaData()
mapper_registry = registry()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(255)),
    Column("hashed_password", String(255)),
    Column("email", String(255), unique=True),
    Column(
        "role", Enum(UserRoles), nullable=False, server_default=UserRoles.user.value
    ),
)


dishes = Table(
    "dishes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(255), nullable=False),
    Column("calories_per_100g", Float, nullable=False),
    Column("protein_per_100g", Float, nullable=False),
    Column("fat_per_100g", Float, nullable=False),
    Column("carbs_per_100g", Float, nullable=False),
    Column("created_by_user_id", Integer, ForeignKey("users.id"), nullable=False),
)

meal_logs = Table(
    "meal_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("dish_id", Integer, ForeignKey("dishes.id"), nullable=False),
    Column("weight_grams", Float, nullable=False),
    Column("eaten_at", DateTime, default=datetime.now),
)

analysis_requests = Table(
    "analysis_requests",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("s3_key", String(512), nullable=False),
    Column(
        "status", Enum(AnalysisStatus), nullable=False, default=AnalysisStatus.pending
    ),
    Column("dish_id", Integer, ForeignKey("dishes.id"), nullable=True),
    Column("created_at", DateTime, default=datetime.now),
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
    mapper_registry.map_imperatively(models.Dish, dishes)
    mapper_registry.map_imperatively(models.MealLog, meal_logs)
    mapper_registry.map_imperatively(models.AnalysisRequest, analysis_requests)


@event.listens_for(models.User, "load")
def receive_load(user, _):
    user.events = []
