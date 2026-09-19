from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.intervention import Intervention
from app.models.user import User
from app.schemas.intervention import InterventionOut
from app.services.ml_engine import train_model

router = APIRouter(prefix="/api/interventions", tags=["interventions"])


@router.get("", response_model=list[InterventionOut])
def list_interventions(db: Session = Depends(get_db)):
    return db.query(Intervention).all()


@router.post("/retrain-model")
def retrain_model(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Triggers a retrain of the logistic regression recommendation model on
    all labeled events collected so far. Available to any authenticated
    user for this prototype; gate behind an admin role in production.
    """
    return train_model(db)
