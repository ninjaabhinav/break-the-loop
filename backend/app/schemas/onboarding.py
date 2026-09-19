from pydantic import BaseModel


class OnboardingMessageIn(BaseModel):
    message: str


class ExtractedBehavior(BaseModel):
    behavior: str | None = None
    behavior_category: str | None = None
    trigger: str | None = None
    context: str | None = None
    emotion: str | None = None
    urge_intensity: int | None = None
    frequency_description: str | None = None
    possible_reward: str | None = None
    urge_pattern: str | None = None
    clarifying_question: str | None = None


class OnboardingMessageOut(BaseModel):
    reply: str
    extracted: ExtractedBehavior
    ready_to_create_loop: bool
