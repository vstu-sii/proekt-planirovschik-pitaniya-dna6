"""Create the initial meal planner schema.

Revision ID: 0001
Revises: None
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "users",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "products",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("name", sa.String(160), nullable=False, unique=True),
        sa.Column("price_per_kg", sa.Numeric(10, 2), nullable=False),
        sa.Column("calories_per_100g", sa.Numeric(8, 2), nullable=False),
        sa.Column("protein_per_100g", sa.Numeric(8, 2), nullable=False),
        sa.Column("fat_per_100g", sa.Numeric(8, 2), nullable=False),
        sa.Column("carbs_per_100g", sa.Numeric(8, 2), nullable=False),
        sa.CheckConstraint("price_per_kg >= 0", name="ck_products_price_nonnegative"),
    )
    op.create_table(
        "dietary_restrictions",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("restriction_type", sa.String(30), nullable=False),
    )
    op.create_table(
        "pantry_items",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", uuid, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("amount_g", sa.Numeric(10, 2), nullable=False),
        sa.CheckConstraint("amount_g > 0", name="ck_pantry_amount_positive"),
    )
    op.create_table(
        "meal_plans",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("goal", sa.String(200), nullable=False),
        sa.Column("budget_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("budget_currency", sa.String(3), nullable=False, server_default="RUB"),
        sa.Column("days_count", sa.Integer(), nullable=False),
        sa.Column("max_cook_time_min", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("budget_amount > 0", name="ck_plans_budget_positive"),
        sa.CheckConstraint("days_count BETWEEN 1 AND 14", name="ck_plans_days_range"),
    )
    op.create_table(
        "day_plans",
        sa.Column("id", uuid, primary_key=True),
        sa.Column(
            "plan_id", uuid, sa.ForeignKey("meal_plans.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.CheckConstraint("day_number > 0", name="ck_day_number_positive"),
        sa.UniqueConstraint("plan_id", "day_number", name="uq_day_per_plan"),
    )
    op.create_table(
        "meals",
        sa.Column("id", uuid, primary_key=True),
        sa.Column(
            "day_plan_id", uuid, sa.ForeignKey("day_plans.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("meal_type", sa.String(20), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("cook_time_min", sa.Integer(), nullable=False),
    )
    op.create_table(
        "meal_ingredients",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("meal_id", uuid, sa.ForeignKey("meals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", uuid, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("amount_g", sa.Numeric(10, 2), nullable=False),
        sa.CheckConstraint("amount_g > 0", name="ck_ingredient_amount_positive"),
    )
    op.create_table(
        "shopping_list_items",
        sa.Column("id", uuid, primary_key=True),
        sa.Column(
            "plan_id", uuid, sa.ForeignKey("meal_plans.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("product_id", uuid, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("amount_g", sa.Numeric(10, 2), nullable=False),
        sa.Column("estimated_cost", sa.Numeric(10, 2), nullable=False),
        sa.CheckConstraint("amount_g > 0", name="ck_shopping_amount_positive"),
        sa.CheckConstraint("estimated_cost >= 0", name="ck_shopping_cost_nonnegative"),
    )


def downgrade() -> None:
    for table in (
        "shopping_list_items",
        "meal_ingredients",
        "meals",
        "day_plans",
        "meal_plans",
        "pantry_items",
        "dietary_restrictions",
        "products",
        "users",
    ):
        op.drop_table(table)
