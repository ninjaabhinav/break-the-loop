import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.loop import OnboardingMessage
from app.models.user import User
from app.schemas.onboarding import ExtractedBehavior, OnboardingMessageIn, OnboardingMessageOut
from app.services.llm_service import extract_behavioral_info

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


@router.get("/history")
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    messages = (
        db.query(OnboardingMessage)
        .filter(OnboardingMessage.user_id == current_user.id)
        .order_by(OnboardingMessage.created_at.asc())
        .all()
    )
    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in messages
    ]


@router.post("/message", response_model=OnboardingMessageOut)
async def send_message(
    payload: OnboardingMessageIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    # Build short rolling history for context (last 6 messages)
    history_rows = (
        db.query(OnboardingMessage)
        .filter(OnboardingMessage.user_id == current_user.id)
        .order_by(OnboardingMessage.created_at.desc())
        .limit(6)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in reversed(history_rows)]

    result = await extract_behavioral_info(payload.message, conversation_history=history)

    user_msg = OnboardingMessage(user_id=current_user.id, role="user", content=payload.message)
    assistant_msg = OnboardingMessage(
        user_id=current_user.id,
        role="assistant",
        content=result["reply"],
        extracted_json=json.dumps(result["extracted"]),
    )
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()

    return OnboardingMessageOut(
        reply=result["reply"],
        extracted=ExtractedBehavior(**result["extracted"]),
        ready_to_create_loop=result["ready_to_create_loop"],
    )
