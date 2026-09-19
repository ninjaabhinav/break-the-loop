from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.loop import BehaviorLoop
from app.models.user import User
from app.schemas.loop import BehaviorLoopCreate, BehaviorLoopOut, BehaviorLoopUpdate

router = APIRouter(prefix="/api/loops", tags=["behavior loops"])


@router.get("", response_model=list[BehaviorLoopOut])
def list_loops(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(BehaviorLoop)
        .filter(BehaviorLoop.user_id == current_user.id)
        .order_by(BehaviorLoop.created_at.desc())
        .all()
    )


@router.post("", response_model=BehaviorLoopOut, status_code=201)
def create_loop(
    payload: BehaviorLoopCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    loop = BehaviorLoop(user_id=current_user.id, **payload.model_dump())
    db.add(loop)
    db.commit()
    db.refresh(loop)
    return loop


@router.patch("/{loop_id}", response_model=BehaviorLoopOut)
def update_loop(
    loop_id: int,
    payload: BehaviorLoopUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loop = db.query(BehaviorLoop).filter(BehaviorLoop.id == loop_id, BehaviorLoop.user_id == current_user.id).first()
    if not loop:
        raise HTTPException(status_code=404, detail="Behavior loop not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(loop, field, value)
    db.commit()
    db.refresh(loop)
    return loop


@router.delete("/{loop_id}", status_code=204)
def delete_loop(loop_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loop = db.query(BehaviorLoop).filter(BehaviorLoop.id == loop_id, BehaviorLoop.user_id == current_user.id).first()
    if not loop:
        raise HTTPException(status_code=404, detail="Behavior loop not found.")
    db.delete(loop)
    db.commit()
    return None
