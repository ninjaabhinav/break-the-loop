from pydantic import BaseModel


class InterventionEffectiveness(BaseModel):
    intervention_name: str
    times_used: int
    success_rate: float  # fraction of uses where behavior_occurred == False


class TriggerFrequency(BaseModel):
    trigger: str
    count: int


class AnalyticsOut(BaseModel):
    baseline_frequency_per_day: float | None
    current_frequency_per_day: float | None
    total_urges_logged: int
    interventions_attempted: int
    interventions_completed: int
    successful_interruptions: int
    interruption_rate: float
    average_urge_before: float | None
    average_urge_after: float | None
    average_delay_minutes: float | None
    most_effective_intervention: str | None
    intervention_breakdown: list[InterventionEffectiveness]
    trigger_breakdown: list[TriggerFrequency]
