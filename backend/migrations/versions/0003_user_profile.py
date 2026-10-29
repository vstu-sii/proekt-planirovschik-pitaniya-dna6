"""Store profile values used for personalisation.

Revision ID: 0003
Revises: 0002
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("height_cm", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("weight_kg", sa.Numeric(6, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "weight_kg")
    op.drop_column("users", "height_cm")
