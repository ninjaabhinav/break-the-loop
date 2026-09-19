from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.event import Event
from app.models.intervention import Intervention
from app.models.loop import BehaviorLoop
from app.models.user import User
from app.schemas.analytics import AnalyticsOut, InterventionEffectiveness, TriggerFrequency

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

RECENT_WINDOW_DAYS = 7


@router.get("", response_model=AnalyticsOut)
def get_analytics(
    loop_id: int | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    events_query = db.query(Event).filter(Event.user_id == current_user.id)
    if loop_id is not None:
        events_query = events_query.filter(Event.loop_id == loop_id)
    events = events_query.all()

    loops_query = db.query(BehaviorLoop).filter(BehaviorLoop.user_id == current_user.id)
    if loop_id is not None:
        loops_query = loops_query.filter(BehaviorLoop.id == loop_id)
    loops = loops_query.all()
    baselines = [l.baseline_frequency_per_day for l in loops if l.baseline_frequency_per_day is not None]
    baseline_frequency = sum(baselines) / len(baselines) if baselines else None

    total_urges = len(events)
    resolved = [e for e in events if e.behavior_occurred is not None]
    attempted = [e for e in events if e.intervention_selected_id is not None]
    completed = [e for e in attempted if e.intervention_completed]
    successful = [e for e in resolved if e.behavior_occurred is False]

    cutoff = datetime.now(timezone.utc) - timedelta(days=RECENT_WINDOW_DAYS)
    recent_events = [e for e in events if e.created_at and e.created_at.replace(tzinfo=timezone.utc) >= cutoff]
    current_frequency = len(recent_events) / RECENT_WINDOW_DAYS if events else None

    urges_before = [e.urge_intensity for e in events if e.urge_intensity is not None]
    urges_after = [e.post_intervention_urge for e in events if e.post_intervention_urge is not None]
    delays = [e.delay_minutes for e in events if e.delay_minutes is not None]

    # Per-intervention effectiveness
    interventions_by_id = {i.id: i for i in db.query(Intervention).all()}
    usage_counter: Counter[int] = Counter()
    success_counter: defaultdict[int, int] = defaultdict(int)
    for e in resolved:
        if e.intervention_selected_id is None:
            continue
        usage_counter[e.intervention_selected_id] += 1
        if e.behavior_occurred is False:
            success_counter[e.intervention_selected_id] += 1

    breakdown = []
    for interv_id, count in usage_counter.items():
        interv = interventions_by_id.get(interv_id)
        if not interv:
            continue
        breakdown.append(
            InterventionEffectiveness(
                intervention_name=interv.name,
                times_used=count,
                success_rate=round(success_counter[interv_id] / count, 2) if count else 0.0,
            )
        )
    breakdown.sort(key=lambda b: (b.success_rate, b.times_used), reverse=True)
    most_effective = breakdown[0].intervention_name if breakdown else None

    trigger_counter = Counter(e.trigger for e in events if e.trigger)
    trigger_breakdown = [
        TriggerFrequency(trigger=t, count=c) for t, c in trigger_counter.most_common()
    ]

    return AnalyticsOut(
        baseline_frequency_per_day=round(baseline_frequency, 2) if baseline_frequency is not None else None,
        current_frequency_per_day=round(current_frequency, 2) if current_frequency is not None else None,
        total_urges_logged=total_urges,
        interventions_attempted=len(attempted),
        interventions_completed=len(completed),
        successful_interruptions=len(successful),
        interruption_rate=round(len(successful) / len(attempted), 2) if attempted else 0.0,
        average_urge_before=round(sum(urges_before) / len(urges_before), 2) if urges_before else None,
        average_urge_after=round(sum(urges_after) / len(urges_after), 2) if urges_after else None,
        average_delay_minutes=round(sum(delays) / len(delays), 2) if delays else None,
        most_effective_intervention=most_effective,
        intervention_breakdown=breakdown,
        trigger_breakdown=trigger_breakdown,
    )
