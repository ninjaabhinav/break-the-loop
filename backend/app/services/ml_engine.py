"""
Recommendation engine for Break the Loop.

Two layers, matching the spec:

1. Rule-based scorer (always available, used from day one / cold start).
   Scores each intervention in the library against the current urge's
   trigger / context / emotion using simple weighted tag overlap, then
   converts the scores into pseudo-probabilities.

2. Logistic regression model (scikit-learn), trained on accumulated
   `Event` rows once there is enough labeled outcome data
   (see settings.ml_min_training_events). Predicts
   P(intervention produces a useful outcome | trigger, context, emotion,
   urge_intensity, intervention). Retrains on demand via `train_model`.

`recommend()` picks whichever layer is available and returns a ranked
list of interventions plus which method produced it, so this is
transparent/explainable rather than a black box.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.event import Event
from app.models.intervention import Intervention

settings = get_settings()

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
MODEL_PATH = os.path.join(MODEL_DIR, "recommendation_model.joblib")

FEATURE_COLUMNS = ["trigger", "context", "emotion", "intervention_id"]


@dataclass
class ScoredIntervention:
    intervention: Intervention
    score: float


def _tag_overlap_score(intervention_tags: str, value: str) -> float:
    """Rewards exact or partial matches between a free-text value and a
    comma-separated tag field on the intervention."""
    if not intervention_tags or not value:
        return 0.0
    tags = [t.strip().lower() for t in intervention_tags.split(",") if t.strip()]
    value = value.strip().lower()
    if value in tags:
        return 1.0
    # partial / substring credit, e.g. "stress" matches "high_stress"
    for tag in tags:
        if tag in value or value in tag:
            return 0.5
    return 0.0


def rule_based_scores(
    interventions: list[Intervention], trigger: str, context: str, emotion: str, urge_intensity: int
) -> list[ScoredIntervention]:
    raw_scores = []
    for interv in interventions:
        score = (
            2.0 * _tag_overlap_score(interv.target_trigger, trigger)
            + 1.5 * _tag_overlap_score(interv.target_emotion, emotion)
            + 1.0 * _tag_overlap_score(interv.target_behavior, context)
        )
        # High urge intensity: mildly favor quicker, easier interventions.
        if urge_intensity >= 7:
            if interv.duration_minutes <= 5:
                score += 0.4
            if interv.difficulty == "easy":
                score += 0.3
        raw_scores.append((interv, score))

    # Convert to pseudo-probabilities with a softmax-like squashing so the
    # output shape matches the spec example (e.g. Breathing 0.78, Walking 0.64).
    values = np.array([s for _, s in raw_scores], dtype=float)
    if values.max() <= 0:
        # No signal at all: fall back to a mild uniform-ish distribution
        # favoring shorter, easier interventions so cold start is still sane.
        base = np.array(
            [1.0 / (1 + interv.duration_minutes) + (0.3 if interv.difficulty == "easy" else 0.0) for interv, _ in raw_scores]
        )
        values = base
    exp_scores = np.exp(values - values.max())
    probs = exp_scores / exp_scores.sum()
    # Rescale into a believable 0.30-0.85 band rather than a strict distribution
    # that sums to 1, since these are independent "would this help" estimates.
    rescaled = 0.30 + probs * (0.85 - 0.30) * len(probs)
    rescaled = np.clip(rescaled, 0.05, 0.95)

    scored = [ScoredIntervention(interv, float(p)) for (interv, _), p in zip(raw_scores, rescaled)]
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored


def _build_training_frame(db: Session) -> pd.DataFrame:
    rows = (
        db.query(Event)
        .filter(
            Event.intervention_selected_id.isnot(None),
            Event.behavior_occurred.isnot(None),
        )
        .all()
    )
    records = []
    for e in rows:
        records.append(
            {
                "trigger": e.trigger,
                "context": e.context,
                "emotion": e.emotion,
                "urge_intensity": e.urge_intensity,
                "intervention_id": str(e.intervention_selected_id),
                # success = the intervention interrupted the unwanted behavior
                "label": 0 if e.behavior_occurred else 1,
            }
        )
    return pd.DataFrame.from_records(records)


def train_model(db: Session) -> dict:
    """Trains (or retrains) the logistic regression model on all labeled
    events so far. Returns a small metrics dict. Safe to call repeatedly."""
    df = _build_training_frame(db)
    if len(df) < settings.ml_min_training_events:
        return {
            "trained": False,
            "reason": f"Only {len(df)} labeled events so far; need {settings.ml_min_training_events}.",
            "n_samples": len(df),
        }

    encoder = OneHotEncoder(handle_unknown="ignore")
    X_cat = encoder.fit_transform(df[FEATURE_COLUMNS]).toarray()
    X = np.hstack([X_cat, df[["urge_intensity"]].to_numpy()])
    y = df["label"].to_numpy()

    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    train_accuracy = float(model.score(X, y))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump({"model": model, "encoder": encoder}, MODEL_PATH)

    return {"trained": True, "n_samples": len(df), "train_accuracy": round(train_accuracy, 3)}


def _load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return None


def ml_scores(
    interventions: list[Intervention], trigger: str, context: str, emotion: str, urge_intensity: int
) -> list[ScoredIntervention] | None:
    bundle = _load_model()
    if bundle is None:
        return None
    model: LogisticRegression = bundle["model"]
    encoder: OneHotEncoder = bundle["encoder"]

    rows = pd.DataFrame(
        [
            {
                "trigger": trigger,
                "context": context,
                "emotion": emotion,
                "intervention_id": str(interv.id),
            }
            for interv in interventions
        ]
    )
    X_cat = encoder.transform(rows[FEATURE_COLUMNS]).toarray()
    X = np.hstack([X_cat, np.full((len(interventions), 1), urge_intensity)])
    probs = model.predict_proba(X)[:, 1]

    scored = [ScoredIntervention(interv, float(p)) for interv, p in zip(interventions, probs)]
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored


def recommend(
    interventions: list[Intervention], trigger: str, context: str, emotion: str, urge_intensity: int
) -> tuple[list[ScoredIntervention], str]:
    """Returns (ranked interventions, method used)."""
    ml_result = ml_scores(interventions, trigger, context, emotion, urge_intensity)
    if ml_result is not None:
        return ml_result, "ml"
    return rule_based_scores(interventions, trigger, context, emotion, urge_intensity), "rule_based"
