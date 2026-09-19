"""
Seeds the intervention library with an initial, evidence-informed set of
candidate micro-interventions. Safe to run multiple times (skips if the
table already has rows).

Run with: python -m app.seed
"""

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.intervention import Intervention

SEED_INTERVENTIONS = [
    {
        "name": "Paced breathing",
        "description": "Breathe in for 4 counts, hold for 4, out for 6, for 5 minutes. Lowers physiological arousal that drives the urge.",
        "target_trigger": "stress,anxiety,anger",
        "target_emotion": "anxious,stressed,angry,overwhelmed",
        "target_behavior": "studying,work,anywhere",
        "duration_minutes": 5,
        "difficulty": "easy",
        "required_environment": "anywhere",
        "evidence_note": "Slow-paced breathing is associated with reduced sympathetic arousal (heart-rate variability literature).",
    },
    {
        "name": "Short walk",
        "description": "Step away and walk for 5 minutes, ideally outside or at least away from the trigger environment.",
        "target_trigger": "boredom,stress,craving",
        "target_emotion": "restless,bored,stressed",
        "target_behavior": "doomscrolling,gaming,smoking",
        "duration_minutes": 5,
        "difficulty": "easy",
        "required_environment": "space_to_walk",
        "evidence_note": "Brief physical activity is linked to reduced craving intensity in habit-change research.",
    },
    {
        "name": "Water + delay",
        "description": "Drink a full glass of water slowly and wait 10 minutes before deciding whether to act on the urge.",
        "target_trigger": "habit,boredom,craving",
        "target_emotion": "bored,neutral,craving",
        "target_behavior": "unhealthy_eating,smoking,snacking",
        "duration_minutes": 10,
        "difficulty": "easy",
        "required_environment": "anywhere",
        "evidence_note": "Urge-surfing / delay techniques let acute craving intensity subside before acting.",
    },
    {
        "name": "Two-minute task start",
        "description": "Commit to just two minutes of the task you're avoiding. Stop after two minutes if you want.",
        "target_trigger": "avoidance,overwhelm",
        "target_emotion": "anxious,overwhelmed,stuck",
        "target_behavior": "procrastination",
        "duration_minutes": 2,
        "difficulty": "medium",
        "required_environment": "at_task",
        "evidence_note": "The 'two-minute rule' reduces the activation barrier that keeps a task feeling unapproachable.",
    },
    {
        "name": "Structured journaling",
        "description": "Write down what you're feeling, what triggered it, and one thing you actually need right now.",
        "target_trigger": "overthinking,stress,emotional",
        "target_emotion": "overwhelmed,anxious,sad,angry",
        "target_behavior": "overthinking,doomscrolling",
        "duration_minutes": 7,
        "difficulty": "medium",
        "required_environment": "quiet_space",
        "evidence_note": "Expressive writing is associated with reduced rumination in cognitive-behavioral research.",
    },
    {
        "name": "Music reset",
        "description": "Put on one song you know well and just listen, without doing anything else at the same time.",
        "target_trigger": "boredom,stress",
        "target_emotion": "bored,stressed,restless",
        "target_behavior": "doomscrolling,gaming,smoking",
        "duration_minutes": 4,
        "difficulty": "easy",
        "required_environment": "headphones_or_speaker",
        "evidence_note": "Music listening is a low-effort attention shift that can interrupt automatic behavior chains.",
    },
    {
        "name": "5-4-3-2-1 grounding",
        "description": "Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste. Brings attention back to the present.",
        "target_trigger": "anxiety,overwhelm,craving",
        "target_emotion": "anxious,overwhelmed,panicked",
        "target_behavior": "overthinking,unhealthy_eating",
        "duration_minutes": 3,
        "difficulty": "easy",
        "required_environment": "anywhere",
        "evidence_note": "A standard grounding technique used in anxiety-management protocols to interrupt spiraling thought loops.",
    },
    {
        "name": "Environment change",
        "description": "Physically move to a different room or location for at least 5 minutes.",
        "target_trigger": "habit,boredom,craving",
        "target_emotion": "bored,restless,craving",
        "target_behavior": "smoking,doomscrolling,gaming",
        "duration_minutes": 5,
        "difficulty": "easy",
        "required_environment": "another_room_available",
        "evidence_note": "Removing situational/contextual cues is a core mechanism in habit-disruption literature.",
    },
    {
        "name": "Reach out to someone",
        "description": "Send a message or call someone you trust, even just to say what you're feeling right now.",
        "target_trigger": "loneliness,stress,craving",
        "target_emotion": "lonely,sad,stressed",
        "target_behavior": "unhealthy_eating,smoking,doomscrolling",
        "duration_minutes": 5,
        "difficulty": "medium",
        "required_environment": "phone_available",
        "evidence_note": "Social contact is a well-established buffer against high-risk urge moments in behavior-change research.",
    },
    {
        "name": "Hunger check-in",
        "description": "Pause and rate actual physical hunger 0-10 before eating. If below 4, try water or a short walk first.",
        "target_trigger": "boredom,emotional,habit",
        "target_emotion": "bored,neutral,stressed",
        "target_behavior": "unhealthy_eating",
        "duration_minutes": 2,
        "difficulty": "easy",
        "required_environment": "anywhere",
        "evidence_note": "Interoceptive check-ins are used in mindful-eating interventions to separate hunger from emotional triggers.",
    },
]


def run_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(Intervention).count()
        if existing > 0:
            print(f"Interventions table already has {existing} rows — skipping seed.")
            return
        for data in SEED_INTERVENTIONS:
            db.add(Intervention(**data))
        db.commit()
        print(f"Seeded {len(SEED_INTERVENTIONS)} interventions.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
