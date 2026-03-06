# ── AgentReady Score · main.py ─────────────────────────────────────
# FastAPI application entry point.
# Run: uvicorn main:app --reload --port 8000

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import score, simulation, actions, benchmark


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup — ensures DB tables exist."""
    init_db()
    yield


app = FastAPI(
    title="AgentReady Score API",
    description="ML-powered diagnostic platform — AI agent readiness for retail",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow React dev server to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers
app.include_router(score.router,      prefix="/api/score",    tags=["Score"])
app.include_router(simulation.router, prefix="/api/simulate", tags=["Simulation"])
app.include_router(actions.router,    prefix="/api/actions",  tags=["Actions"])
app.include_router(benchmark.router,  prefix="/api/benchmark",tags=["Benchmark"])


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AgentReady Score API", "version": "1.0.0"}
