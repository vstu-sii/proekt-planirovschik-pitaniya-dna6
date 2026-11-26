import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DietaryRestriction(Base):
    __tablename__ = "dietary_restrictions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    restriction_type: Mapped[str] = mapped_column(String(30), nullable=False)


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (CheckConstraint("price_per_kg >= 0", name="ck_products_price_nonnegative"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    price_per_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    calories_per_100g: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    protein_per_100g: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    fat_per_100g: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    carbs_per_100g: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)


class PantryItem(Base):
    __tablename__ = "pantry_items"
    __table_args__ = (CheckConstraint("amount_g > 0", name="ck_pantry_amount_positive"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
    amount_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class MealPlan(Base):
    __tablename__ = "meal_plans"
    __table_args__ = (
        CheckConstraint("budget_amount > 0", name="ck_plans_budget_positive"),
        CheckConstraint("days_count BETWEEN 1 AND 14", name="ck_plans_days_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    goal: Mapped[str] = mapped_column(String(200), nullable=False)
    budget_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    budget_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    days_count: Mapped[int] = mapped_column(Integer, nullable=False)
    max_cook_time_min: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DayPlan(Base):
    __tablename__ = "day_plans"
    __table_args__ = (
        CheckConstraint("day_number > 0", name="ck_day_number_positive"),
        UniqueConstraint("plan_id", "day_number", name="uq_day_per_plan"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meal_plans.id", ondelete="CASCADE"))
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    day_plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("day_plans.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text)
    cook_time_min: Mapped[int] = mapped_column(Integer, nullable=False)


class MealIngredient(Base):
    __tablename__ = "meal_ingredients"
    __table_args__ = (CheckConstraint("amount_g > 0", name="ck_ingredient_amount_positive"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meals.id", ondelete="CASCADE"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
    amount_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"
    __table_args__ = (
        CheckConstraint("amount_g > 0", name="ck_shopping_amount_positive"),
        CheckConstraint("estimated_cost >= 0", name="ck_shopping_cost_nonnegative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meal_plans.id", ondelete="CASCADE"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))
    amount_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
