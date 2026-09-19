from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Event(Base):
    """
    One full urge -> intervention -> outcome record. This is the primary
    unit of data the ML recommendation engine trains on.
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    loop_id: Mapped[int | None] = mapped_column(ForeignKey("behavior_loops.id"), nullable=True)

    trigger: Mapped[str] = mapped_column(String(150), nullable=False)
    context: Mapped[str] = mapped_column(String(150), nullable=False)
    emotion: Mapped[str] = mapped_column(String(100), nullable=False)
    urge_intensity: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-10

    intervention_offered_id: Mapped[int | None] = mapped_column(ForeignKey("interventions.id"), nullable=True)
    intervention_selected_id: Mapped[int | None] = mapped_column(ForeignKey("interventions.id"), nullable=True)
    intervention_completed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    post_intervention_urge: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-10
    behavior_occurred: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    delay_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)
    user_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5

    recommendation_method: Mapped[str | None] = mapped_column(String(20), nullable=True)  # rule_based | ml
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="events")
    loop = relationship("BehaviorLoop", back_populates="events")
