from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Intervention(Base):
    """
    A candidate micro-intervention in the structured intervention library.
    Seeded initially, editable later as the evidence base grows.
    """

    __tablename__ = "interventions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Matching fields used by the rule-based recommender.
    # Comma-separated lists of tags, e.g. "stress,boredom" or "studying,late_night"
    target_trigger: Mapped[str] = mapped_column(String(255), default="")
    target_emotion: Mapped[str] = mapped_column(String(255), default="")
    target_behavior: Mapped[str] = mapped_column(String(255), default="")

    duration_minutes: Mapped[int] = mapped_column(Integer, default=5)
    difficulty: Mapped[str] = mapped_column(String(20), default="easy")  # easy | medium | hard
    required_environment: Mapped[str] = mapped_column(String(150), default="anywhere")
    evidence_note: Mapped[str] = mapped_column(Text, default="")
