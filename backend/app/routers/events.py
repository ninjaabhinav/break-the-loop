from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.event import Event
from app.models.intervention import Intervention
from app.models.user import User
from app.schemas.event import EventOut, InterventionSelection, OutcomeReport, UrgeCreate
from app.schemas.intervention import InterventionOut, RankedIntervention, RecommendationOut
from app.services.ml_engine import recommend

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("/urge", response_model=RecommendationOut, status_code=201)
def log_urge(payload: UrgeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interventions = db.query(Intervention).all()
    if not interventions:
        raise HTTPException(status_code=500, detail="No interventions are seeded in the database yet.")

    ranked, method = recommend(
        interventions, payload.trigger, payload.context, payload.emotion, payload.urge_intensity
    )

    event = Event(
        user_id=current_user.id,
        loop_id=payload.loop_id,
        trigger=payload.trigger,
        context=payload.context,
        emotion=payload.emotion,
        urge_intensity=payload.urge_intensity,
        raw_text=payload.raw_text,
        intervention_offered_id=ranked[0].intervention.id,
        recommendation_method=method,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    primary = ranked[0]
    backups = ranked[1:4]  # up to 3 backups

    return RecommendationOut(
        event_id=event.id,
        method=method,
        primary=RankedIntervention(intervention=InterventionOut.model_validate(primary.intervention), score=round(primary.score, 2)),
        backups=[
            RankedIntervention(intervention=InterventionOut.model_validate(b.intervention), score=round(b.score, 2))
            for b in backups
        ],
    )


@router.patch("/{event_id}/select", response_model=EventOut)
def select_intervention(
    event_id: int,
    payload: InterventionSelection,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = _get_owned_event(event_id, current_user, db)
    event.intervention_selected_id = payload.intervention_selected_id
    db.commit()
    db.refresh(event)
    return event


@router.patch("/{event_id}/outcome", response_model=EventOut)
def report_outcome(
    event_id: int,
    payload: OutcomeReport,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = _get_owned_event(event_id, current_user, db)
    event.intervention_completed = payload.intervention_completed
    event.post_intervention_urge = payload.post_intervention_urge
    event.behavior_occurred = payload.behavior_occurred
    event.delay_minutes = payload.delay_minutes
    event.user_rating = payload.user_rating
    event.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[EventOut])
def list_events(
    loop_id: int | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    query = db.query(Event).filter(Event.user_id == current_user.id)
    if loop_id is not None:
        query = query.filter(Event.loop_id == loop_id)
    return query.order_by(Event.created_at.desc()).all()


def _get_owned_event(event_id: int, current_user: User, db: Session) -> Event:
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return event
