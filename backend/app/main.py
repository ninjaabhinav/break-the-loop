import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.routers import analytics, auth, events, interventions, loops, onboarding
from app.seed import run_seed

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(
    title="Break the Loop API",
    description="Behavioral loop interruption backend: LLM-assisted onboarding, "
    "a rule-based/ML intervention recommendation engine, event tracking, and analytics.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(loops.router)
app.include_router(onboarding.router)
app.include_router(interventions.router)
app.include_router(events.router)
app.include_router(analytics.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    run_seed()


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
