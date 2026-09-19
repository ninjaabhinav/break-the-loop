# Break the Loop — Backend

FastAPI backend: auth, behavior loops, LLM-assisted onboarding (Groq), a
rule-based + logistic-regression intervention recommendation engine, event
tracking, and analytics.

## Setup

Requires Python 3.11+.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# open .env and set GROQ_API_KEY (free key at https://console.groq.com)
# and SECRET_KEY to a random string
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

- API docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

On first startup, the SQLite database is created automatically at
`backend/data/app.db` and the intervention library is seeded.

## Notes on the ML layer

- Until enough labeled events exist (`ML_MIN_TRAINING_EVENTS` in `.env`,
  default 30), recommendations come from the rule-based scorer in
  `app/services/ml_engine.py`, which matches an urge's trigger/context/emotion
  against each intervention's tags.
- Once enough events with a reported outcome (`behavior_occurred`) exist,
  call `POST /api/interventions/retrain-model` to train a logistic regression
  model. Future recommendations automatically switch to `"method": "ml"`.
- The model is saved to `backend/data/recommendation_model.joblib` and
  reloaded on each request — no restart needed after retraining.

## Switching to PostgreSQL later

Change `DATABASE_URL` in `.env`, e.g.:

```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/break_the_loop
```

and add `psycopg2-binary` to `requirements.txt`. No other code changes needed
— SQLAlchemy handles both.
