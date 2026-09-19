# Break the Loop — Frontend

Plain React + Vite app (no UI framework, no Tailwind CDN) with a hand-built
design system in `src/styles/global.css`. Talks to the FastAPI backend over
REST.

## Setup

Requires Node.js 18+.

```bash
cd frontend
npm install
```

By default the app calls the API at `http://localhost:8000`. To point at a
different backend URL, create `frontend/.env` with:

```
VITE_API_URL=http://localhost:8000
```

## Run

```bash
npm run dev
```

Open http://localhost:5173. Make sure the backend (see `../backend/README.md`)
is running first.

## Build for production

```bash
npm run build
```

Outputs static files to `frontend/dist/` — this is what you deploy (see the
root README for free hosting options once you're ready).

## Pages

- `/` — landing page (public)
- `/login`, `/register` — auth
- `/onboarding` — conversational LLM-assisted behavior setup
- `/dashboard` — list of behavior loops
- `/urge` — the core urge → recommendation → timer → outcome flow
- `/analytics` — aggregate stats
- `/history` — full event log
- `/profile` — account info, sign out
