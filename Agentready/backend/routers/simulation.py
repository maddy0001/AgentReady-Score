# ── AgentReady Score · routers/simulation.py ──────────────────────
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from collections import Counter

from database import get_db
from models import AgentInteraction, Seller
from simulator import stream_interactions, generate_interaction

router = APIRouter()


def _get_demo_dict(db: Session) -> dict:
    seller = (db.query(Seller)
               .filter(Seller.agentready_score > 0)
               .order_by(Seller.agentready_score)
               .first())
    if not seller:
        return {}
    return {c.name: getattr(seller, c.name) for c in Seller.__table__.columns}


@router.get("/stream")
async def stream(db: Session = Depends(get_db)):
    """
    SSE endpoint — pushes one agent interaction every ~2 seconds.
    Frontend connects with:  new EventSource('/api/simulate/stream')
    Each event is JSON with: agent_name, action, result, revenue_at_risk, etc.
    """
    seller_dict = _get_demo_dict(db)

    async def event_generator():
        async for ix in stream_interactions(seller=seller_dict, interval_seconds=2.2):
            yield f"data: {json.dumps(ix)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering": "no",
            "Connection":       "keep-alive",
        },
    )


@router.get("/run")
def run_batch(count: int = 10, db: Session = Depends(get_db)):
    """Generate N interactions synchronously. Good for testing."""
    seller_dict = _get_demo_dict(db)
    results = [generate_interaction(seller_dict) for _ in range(count)]

    fails      = [r for r in results if r["result"] == "FAIL"]
    total_lost = sum(r["revenue_at_risk"] for r in fails)

    return {
        "count":        len(results),
        "interactions": results,
        "summary": {
            "failed":       len(fails),
            "succeeded":    len(results) - len(fails),
            "total_lost":   round(total_lost, 2),
            "fraud_flags":  sum(1 for r in results if r["is_fraud_risk"]),
        },
    }


@router.get("/log")
def get_log(limit: int = 50, db: Session = Depends(get_db)):
    """Returns the most recent interactions from the DB."""
    interactions = (db.query(AgentInteraction)
                    .order_by(AgentInteraction.id.desc())
                    .limit(limit)
                    .all())
    return [
        {
            "id":              i.id,
            "timestamp":       i.timestamp.isoformat() if i.timestamp else None,
            "agent_name":      i.agent_name,
            "action":          i.action,
            "result":          i.result,
            "revenue_at_risk": i.revenue_at_risk,
            "root_cause":      i.root_cause,
            "fraud_score":     i.fraud_score,
            "is_fraud_risk":   i.is_fraud_risk,
        }
        for i in interactions
    ]


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Aggregated statistics across all logged interactions."""
    all_ix = db.query(AgentInteraction).all()
    fails  = [i for i in all_ix if i.result == "FAIL"]
    total  = len(all_ix)

    causes = Counter(i.action_type for i in fails)
    top_causes = [{"type": k, "count": v} for k, v in causes.most_common(5)]

    return {
        "total_interactions":  total,
        "total_failed":        len(fails),
        "total_succeeded":     total - len(fails),
        "success_rate":        round((total - len(fails)) / total * 100, 1) if total > 0 else 0,
        "total_revenue_lost":  round(sum(i.revenue_at_risk for i in fails), 2),
        "fraud_flags":         sum(1 for i in all_ix if i.is_fraud_risk),
        "top_failure_causes":  top_causes,
    }
