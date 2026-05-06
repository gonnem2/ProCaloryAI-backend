"""add meal table + add core request table

Revision ID: baef36a66a17
Revises: e261a863c269
Create Date: 2026-04-27 19:38:38.431230

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "baef36a66a17"
down_revision: Union[str, Sequence[str], None] = "e261a863c269"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
