import json
import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are the onboarding assistant inside "Break the Loop", an app that \
helps people interrupt unwanted recurring behavioral loops (Trigger -> Urge -> Automatic \
Behavior -> Short-Term Reward -> Long-Term Cost -> Repetition).

Your job in every turn is to:
1. Read the user's free-text message describing a behavior they want to change.
2. Extract whatever structured fields you can confidently infer.
3. Write ONE short, warm, non-clinical reply. If key fields are still missing, ask exactly
   one focused clarifying question to get the most useful missing piece of information
   (in priority order: behavior, trigger, context, emotion, urge_intensity).
4. Never diagnose, and never claim this app treats or cures anything. If the user
   describes something clinical (e.g. addiction, self-harm, an eating disorder), gently
   suggest that a professional could help alongside using this app.

Respond with ONLY a single JSON object, no markdown fences, no commentary, matching
exactly this shape:
{
  "reply": "<your one short message to the user>",
  "extracted": {
    "behavior": "<short slug like 'social_media_scrolling', or null>",
    "behavior_category": "<one of: smoking, doomscrolling, gaming, procrastination, overthinking, unhealthy_eating, other, or null>",
    "trigger": "<short slug like 'stress', or null>",
    "context": "<short slug like 'studying', or null>",
    "emotion": "<short slug like 'anxious', or null>",
    "urge_intensity": <integer 1-10 or null>,
    "frequency_description": "<free text like 'several times a day', or null>",
    "possible_reward": "<short slug like 'distraction', or null>",
    "urge_pattern": "<one of: automatic, deliberate, mixed, or null>"
  },
  "ready_to_create_loop": <true only once behavior, trigger, context and emotion are all known>
}
"""


async def extract_behavioral_info(message: str, conversation_history: list[dict] | None = None) -> dict:
    """
    Calls Groq's chat completion API (OpenAI-compatible) to turn a free-text
    message into structured behavioral data plus a conversational reply.

    Falls back to a safe, minimal structured response if the API key is
    missing or the call fails, so the rest of the app keeps working.
    """
    if not settings.groq_api_key:
        return _fallback_response(
            "I couldn't reach the language model (no GROQ_API_KEY is configured), but I've "
            "saved your message. You can still fill in the details manually below."
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": message})

    payload = {
        "model": settings.groq_model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 500,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(settings.groq_api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return _normalize(parsed)
    except Exception:
        logger.exception("Groq LLM call failed")
        return _fallback_response(
            "I had trouble reaching the language model just now. Could you describe the "
            "behavior, what usually triggers it, and how it makes you feel?"
        )


def _normalize(parsed: dict) -> dict:
    extracted = parsed.get("extracted", {}) or {}
    return {
        "reply": parsed.get("reply", "Tell me a bit more about this behavior."),
        "extracted": {
            "behavior": extracted.get("behavior"),
            "behavior_category": extracted.get("behavior_category"),
            "trigger": extracted.get("trigger"),
            "context": extracted.get("context"),
            "emotion": extracted.get("emotion"),
            "urge_intensity": extracted.get("urge_intensity"),
            "frequency_description": extracted.get("frequency_description"),
            "possible_reward": extracted.get("possible_reward"),
            "urge_pattern": extracted.get("urge_pattern"),
        },
        "ready_to_create_loop": bool(parsed.get("ready_to_create_loop", False)),
    }


def _fallback_response(reply: str) -> dict:
    return {
        "reply": reply,
        "extracted": {
            "behavior": None,
            "behavior_category": None,
            "trigger": None,
            "context": None,
            "emotion": None,
            "urge_intensity": None,
            "frequency_description": None,
            "possible_reward": None,
            "urge_pattern": None,
        },
        "ready_to_create_loop": False,
    }
