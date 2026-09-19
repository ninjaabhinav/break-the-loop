from pydantic import BaseModel


class InterventionOut(BaseModel):
    id: int
    name: str
    description: str
    duration_minutes: int
    difficulty: str
    required_environment: str
    evidence_note: str

    class Config:
        from_attributes = True


class RankedIntervention(BaseModel):
    intervention: InterventionOut
    score: float  # pseudo-probability the intervention will help, 0-1


class RecommendationOut(BaseModel):
    event_id: int
    method: str  # "rule_based" | "ml"
    primary: RankedIntervention
    backups: list[RankedIntervention]
