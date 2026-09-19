# Break the Loop

### AI-Assisted Behavioral Intervention Prototype

> What if we could help someone interrupt an unwanted behavioral pattern at the moment the urge occurs — rather than only tracking what happened afterward?

Break the Loop is an early full-stack prototype exploring how AI-assisted, context-aware interventions could help people interrupt recurring behavioral patterns they want to reduce, stop, or gain more control over.

---

## Live Demo

**Live application:** https://break-the-loop-rouge.vercel.app
**GitHub repository:** https://github.com/ninjaabhinav/break-the-loop

---

## The Idea

Many unwanted behaviors follow a recurring loop:

```
Trigger → Urge → Automatic Behavior → Short-Term Reward → Long-Term Cost → Repetition
```

Most habit-tracking approaches focus on recording what happened after the fact. **Break the Loop focuses on the moment between the urge and the action.** The prototype inserts a pause and a small intervention into that sequence:

```
Trigger → Urge → Pause → Intervention → Reassess → Outcome → Learning
```

The goal is to create a small moment of conscious choice before an automatic behavior takes over.

---

## What Break the Loop Does

The current prototype lets a user:

- Define a behavioral loop they want to understand or change
- Log an urge when it occurs, with trigger, context, emotion, and intensity
- Receive a context-aware intervention recommendation
- Choose from alternative interventions instead of a single fixed suggestion
- Record what happened afterward
- Review behavioral history and basic analytics

The system does not treat an interaction as simply a "success" or "failure." If an intervention reduces an urge from 9/10 to 6/10, delays the behavior, or just helps the user pause before acting, that's still useful signal for future personalization.

---

## V1 Features

**Behavioral loop management** — define recurring behaviors to understand, reduce, or gain more control over.

**Urge logging** — record behavior, trigger, context, emotional state, and urge intensity in the moment.

**AI-assisted behavioral understanding** — free-text descriptions are interpreted into structured behavioral context (trigger, context, emotion) via an LLM.

**Context-aware interventions** — a recommendation engine ranks interventions against the logged trigger/context/emotion, starting rule-based and shifting to a trained model as outcome data accumulates.

**Alternative interventions** — users can pick a backup option instead of only the top recommendation.

**Outcome tracking** — what was tried, whether it was completed, the urge level afterward, and whether the original behavior still happened.

**Behavioral history & analytics** — past interactions, interruption rate, and which interventions have worked best so far.

---

## Example Interaction

```
Behavior:  Doomscrolling
Trigger:   Boredom
Context:   Free time
Emotion:   Bored
Urge:      9/10

→ Recommended intervention: short walk

Urge before:  9/10
Urge after:   6/10
Behavior:     delayed, not repeated
```

The objective isn't to mark this a "win" or "loss" — the interaction itself is useful behavioral data, regardless of outcome.

---

## Architecture

```
                         USER
                          │
                          ▼
                ┌───────────────────┐
                │   React Frontend  │
                │                   │
                │  Dashboard        │
                │  Urge logging     │
                │  Intervention flow│
                │  History          │
                │  Analytics        │
                └─────────┬─────────┘
                          │ REST API (JWT auth)
                          ▼
                ┌───────────────────┐
                │  FastAPI Backend  │
                │                   │
                │  Auth & loops     │
                │  Recommendation   │
                │    engine         │
                │  Event tracking   │
                │  Analytics        │
                └─────────┬─────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
    ┌───────────────────┐   ┌───────────────────┐
    │   PostgreSQL /     │   │   Groq LLM API    │
    │   SQLite database  │   │  (onboarding NLU) │
    └───────────────────┘   └───────────────────┘
```

The recommendation engine starts with a rule-based scorer (tag matching between an urge's trigger/context/emotion and the intervention library) and switches to a trained logistic regression model once enough labeled outcomes exist.

---

## Tech Stack

**Frontend:** React, Vite, JavaScript, hand-written CSS design system (no UI framework)

**Backend:** Python, FastAPI, SQLAlchemy

**AI / ML:** Groq-hosted LLM for conversational behavioral extraction; scikit-learn (logistic regression) for the recommendation engine

**Database:** PostgreSQL in production (Neon), SQLite for local development

**Deployment:** Vercel (frontend), Render (backend), Neon (database)

---

## Project Structure

```
break-the-loop/
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── core/        # config, security, auth dependency
│   │   ├── db/           # SQLAlchemy engine/session
│   │   ├── models/       # ORM tables
│   │   ├── schemas/      # Pydantic request/response models
│   │   ├── services/     # LLM service, ML recommendation engine
│   │   ├── routers/      # API endpoints
│   │   ├── seed.py       # intervention library seed data
│   │   └── main.py
│   └── requirements.txt
├── .gitignore
└── README.md
```

---

## Run Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/ninjaabhinav/break-the-loop.git
cd break-the-loop
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install dependencies and configure environment variables:

```bash
pip install -r requirements.txt
cp .env.example .env      # Windows: copy .env.example .env
```

Open `.env` and set `SECRET_KEY` (any random string) and optionally `GROQ_API_KEY` (see [Environment Variables](#environment-variables) below).

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

The SQLite database and intervention library are created and seeded automatically on first run.

### 3. Frontend setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173

---

## Environment Variables

Backend (`backend/.env`, based on `backend/.env.example`):

```env
SECRET_KEY=any-long-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=10080

DATABASE_URL=sqlite:///./data/app.db
# or, in production: postgresql+psycopg2://user:password@host/dbname

GROQ_API_KEY=your-groq-api-key      # optional — free tier at console.groq.com
GROQ_MODEL=llama-3.1-8b-instant

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

ML_MIN_TRAINING_EVENTS=30
```

Frontend (`frontend/.env`, optional):

```env
VITE_API_URL=http://localhost:8000
```

Without `GROQ_API_KEY`, the app still runs — the conversational onboarding step falls back to a manual entry form instead of calling the LLM.

**Never commit:** API keys, database credentials, the `SECRET_KEY` value, or any real `.env` file. `.gitignore` already excludes these — double-check before pushing.

---

## Behavioral Data

V1 uses a small seed intervention library and no real user data yet. The long-term objective is to learn from repeated real behavioral interactions rather than one-time survey responses. A future interaction record looks like:

```
user_id, behavior, timestamp, trigger, context, emotion, urge_intensity,
intervention_offered, intervention_selected, intervention_completed,
post_intervention_urge, behavior_occurred, delay_minutes, user_rating
```

Repeated interactions like this are what the recommendation model trains on as usage grows.

---

## Research Direction

```
Behavioral Context → Intervention → User Outcome → Behavioral Data
        → Model Learning → Personalized Recommendation → Improved Intervention
```

Future directions being explored (not implemented in V1):

- Personalized, per-user intervention ranking
- Intervention effectiveness prediction
- Adaptive intervention timing
- Sequential decision-making / contextual bandits
- Longitudinal behavioral modeling

These are research directions, not claims about the current prototype's effectiveness.

---

## Roadmap

**Phase 1 — V1 prototype** ✅
Behavioral loop creation · urge logging · trigger/context capture · intervention recommendations · alternative interventions · outcome tracking · history · basic analytics · web deployment

**Phase 2 — Early pilot**
Recruit early users · collect longitudinal interaction data · analyze intervention outcomes · identify recurring patterns · evaluate recommendation quality

**Phase 3 — Personalization**
User-specific recommendation models · context-aware personalization · intervention effectiveness modeling · improved ranking

**Longer-term research**
Sequential behavioral modeling · contextual decision-making · adaptive intervention policies · larger longitudinal datasets · rigorous effectiveness evaluation

---

## Current Limitations

Break the Loop is an early experimental prototype. It:

- Uses a limited seed dataset, not real-world behavioral data
- Has not been clinically validated
- Does not establish that any intervention is medically effective
- Does not diagnose or treat addiction or mental-health conditions
- Is not a replacement for professional care
- Needs substantially more real-world data before any claims about personalization or effectiveness would be warranted

The purpose of V1 is to validate the product flow, gather feedback, and build the foundation for future experimentation — not to demonstrate proven behavioral outcomes.

---

## Privacy

Behavioral information can be sensitive. The project is designed around:

- Data minimization
- Avoiding collection of unnecessary personal information
- Secure handling of credentials and API keys
- Clear communication about how data is used

Users should avoid submitting highly sensitive personal information beyond what the prototype needs.

---

## Project Status

**V1 — working prototype**, deployed and functional. Next stage: moving from a functional prototype toward an early pilot with real users and longitudinal interaction data.

---

## Author

**Abhinav Mishra**
B.Tech — Computer Science & Engineering (AI/ML)
GitHub: [github.com/ninjaabhinav](https://github.com/ninjaabhinav)

---

## Feedback

This is an evolving research and product prototype. Feedback is welcome on user experience, intervention design, behavioral modeling, AI/ML architecture, privacy, and personalization.

---

## License

This project is currently an independent experimental prototype. A formal open-source license may be added as the project develops.