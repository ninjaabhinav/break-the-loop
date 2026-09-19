# Break the Loop

An AI/ML-assisted behavioral-intervention prototype: it helps someone notice
the **trigger → urge → automatic behavior → short-term reward → long-term
cost → repetition** loop behind a habit they want to change, and offers a
small, specific intervention in the moment instead of just telling them to
stop.

This is an experimental behavioral-support tool, not a medical treatment —
it does not diagnose or claim to cure anything.

## Architecture

```
React (Vite)  --->  FastAPI  --->  SQLite (swap to PostgreSQL later)
                       |
                       |--- Groq LLM: conversational onboarding,
                       |    turns free text into structured behavioral data
                       |
                       '--- Recommendation engine (app/services/ml_engine.py):
                            - rule-based tag matching (cold start)
                            - logistic regression, trained on real outcomes
                              once enough events exist, and used automatically
                              from then on
```

This corresponds to Phases 1–4 of the original project plan: schema +
intervention library, a complete end-to-end React/FastAPI/DB flow, the LLM
onboarding layer, and a working (if simple) ML recommendation model that
improves as real outcome data accumulates. Phases 5+ (pilot recruitment,
contextual bandits, personalization research) build on top of this
foundation later.

## Project layout

```
break-the-loop/
  backend/     FastAPI app, SQLAlchemy models, LLM service, ML engine
  frontend/    React (Vite) app
```

## Running it locally

You need two terminals — one for the backend, one for the frontend.

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

Open `backend/.env` and set:
- `SECRET_KEY` — any long random string
- `GROQ_API_KEY` — a free key from https://console.groq.com (the app still
  runs without one; onboarding just falls back to a plain message asking you
  to fill in details manually)

Then:

```bash
uvicorn app.main:app --reload --port 8000
```

Check it's up: http://localhost:8000/api/health should return `{"status":"ok"}`.
Interactive API docs: http://localhost:8000/docs

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

### 3. Try it

1. Register an account.
2. On the onboarding screen, describe a behavior (e.g. "I always start
   scrolling Instagram when I'm stressed while studying") or fill the fields
   manually, then save it as a behavior loop.
3. From the dashboard, click "I'm having an urge", log the trigger/context/
   emotion/intensity, and you'll get a ranked intervention recommendation.
4. Try the intervention, let the timer run (or mark it done early), and
   report the outcome.
5. Check Analytics and History to see the data accumulate. Once 30+ outcomes
   are logged (`ML_MIN_TRAINING_EVENTS` in `.env`), call
   `POST /api/interventions/retrain-model` (via the Swagger docs at `/docs`,
   or `curl`) to train the logistic-regression model — recommendations will
   then switch from `"rule_based"` to `"ml"` automatically.

## Deployment

Once you've got both sides running locally the way you want, let me know and
I'll walk you through free hosting options for the frontend (static hosting)
and backend (with a small always-on API tier) that fit this stack.
