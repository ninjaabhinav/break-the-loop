from datetime import datetime

from pydantic import BaseModel, Field


class UrgeCreate(BaseModel):
    """Submitted when the user says 'I'm having an urge' and logs context."""

    loop_id: int | None = None
    trigger: str = Field(min_length=1, max_length=150)
    context: str = Field(min_length=1, max_length=150)
    emotion: str = Field(min_length=1, max_length=100)
    urge_intensity: int = Field(ge=1, le=10)
    raw_text: str | None = None


class InterventionSelection(BaseModel):
    """Submitted once the user picks (or skips) the recommended intervention."""

    intervention_selected_id: int | None = None


class OutcomeReport(BaseModel):
    """Submitted after the intervention window ends."""

    intervention_completed: bool
    post_intervention_urge: int | None = Field(default=None, ge=1, le=10)
    behavior_occurred: bool
    delay_minutes: float | None = None
    user_rating: int | None = Field(default=None, ge=1, le=5)


class EventOut(BaseModel):
    id: int
    loop_id: int | None
    trigger: str
    context: str
    emotion: str
    urge_intensity: int
    intervention_offered_id: int | None
    intervention_selected_id: int | None
    intervention_completed: bool | None
    post_intervention_urge: int | None
    behavior_occurred: bool | None
    delay_minutes: float | None
    user_rating: int | None
    recommendation_method: str | None
    created_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True
