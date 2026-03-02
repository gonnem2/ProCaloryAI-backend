from sqlalchemy import MetaData, Table, Column, Integer, String, Enum, event
from sqlalchemy.orm import mapper

from src.domain.models.user import UserRoles
from src.domain import models


metadata = MetaData()


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


def start_mappers():
    mapper(models.User, users)


@event.listens_for(models.User, "load")
def receive_load(user, _):
    user.events = []
