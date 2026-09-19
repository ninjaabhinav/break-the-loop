from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BehaviorLoop(Base):
    """
    A single unwanted behavioral loop the user is trying to interrupt,
    e.g. 'doomscrolling while studying' or 'smoking after meals'.
    """

    __tablename__ = "behavior_loops"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    behavior_category: Mapped[str] = mapped_column(String(100), nullable=False)
    typical_trigger: Mapped[str | None] = mapped_column(String(255), nullable=True)
    typical_context: Mapped[str | None] = mapped_column(String(255), nullable=True)
    typical_emotion: Mapped[str | None] = mapped_column(String(100), nullable=True)
    frequency_description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    baseline_frequency_per_day: Mapped[float | None] = mapped_column(Float, nullable=True)
    history_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="loops")
    events = relationship("Event", back_populates="loop", cascade="all, delete-orphan")


class OnboardingMessage(Base):
    """
    Stores the conversational onboarding exchange so the LLM extraction
    history is auditable and reusable for future context.
    """

    __tablename__ = "onboarding_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="onboarding_messages")
