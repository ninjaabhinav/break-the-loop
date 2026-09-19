# Break the Loop

### AI-assisted behavioral intervention prototype

**Break the Loop** explores a simple question:

> What if we could help someone interrupt an unwanted behavioral pattern at the moment the urge occurs — rather than only tracking what happened afterward?

The project is an early full-stack prototype for exploring personalized, context-aware behavioral interventions.

**Live Demo:**  
https://break-the-loop-rouge.vercel.app

**Repository:**  
https://github.com/ninjaabhinav/break-the-loop

---

## The Idea

Many unwanted behaviors follow a recurring pattern:

**Trigger → Urge → Automatic Behavior → Short-term Reward → Long-term Cost → Repetition**

Break the Loop focuses on the point between the **urge and the action**.

The prototype allows a user to:

1. Define a behavioral loop they want to understand or change.
2. Describe what is happening when an urge occurs.
3. Receive a context-aware intervention.
4. Try the intervention or choose an alternative.
5. Record what happened afterward.
6. Review their behavioral patterns and outcomes over time.

The goal is not to label an interaction simply as a "success" or "failure."

A reduction in urge intensity, a delay in the behavior, or a successful interruption can all provide useful information for future personalization.

---

## V1 Prototype

The current version demonstrates the complete core interaction flow:

**Behavior → Trigger → Context → Urge → Intervention → Outcome → History**

V1 includes:

- Behavioral loop creation
- Natural-language behavioral input
- AI-assisted context understanding
- Urge logging
- Context-aware intervention recommendations
- Alternative intervention options
- Intervention outcome tracking
- Behavioral history
- Basic analytics
- Persistent backend data
- Full React + FastAPI application flow

---

## Screenshots

### Dashboard

The dashboard provides an overview of active behavioral loops and recent interaction data.

### Log an Urge

Users can record the behavioral situation they are experiencing, including the trigger, context, emotional state, and urge intensity.

### Intervention

The system provides a small intervention intended to create a pause between the urge and the automatic behavior.

### Analytics

Recorded interactions can be reviewed to understand patterns and intervention outcomes over time.

---

## Technology

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- SQLAlchemy

### AI / ML

- LLM-assisted behavioral understanding
- Recommendation logic
- Scikit-learn-based experimentation

### Data

- SQLite for the current prototype
- Structured behavioral event data
- Designed to evolve toward a larger longitudinal dataset

---

## Architecture

```text
User
  │
  ▼
React Frontend
  │
  ▼
FastAPI Backend
  │
  ├── AI / Behavioral Understanding
  │
  ├── Intervention Recommendation
  │
  └── Behavioral Data
          │
          ▼
       Database