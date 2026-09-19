from datetime import datetime

from pydantic import BaseModel, Field


class BehaviorLoopCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    behavior_category: str
    typical_trigger: str | None = None
    typical_context: str | None = None
    typical_emotion: str | None = None
    frequency_description: str | None = None
    baseline_frequency_per_day: float | None = None
    history_notes: str | None = None


class BehaviorLoopUpdate(BaseModel):
    name: str | None = None
    typical_trigger: str | None = None
    typical_context: str | None = None
    typical_emotion: str | None = None
    frequency_description: str | None = None
    baseline_frequency_per_day: float | None = None
    history_notes: str | None = None
    is_active: bool | None = None


class BehaviorLoopOut(BaseModel):
    id: int
    name: str
    behavior_category: str
    typical_trigger: str | None
    typical_context: str | None
    typical_emotion: str | None
    frequency_description: str | None
    baseline_frequency_per_day: float | None
    history_notes: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
