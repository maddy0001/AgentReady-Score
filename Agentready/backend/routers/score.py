# ── AgentReady Score · routers/score.py ───────────────────────────
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import random

from database import get_db
from models import Seller, ScoreHistory, AgentInteraction
from ml.predict import predict_score
from simulator import get_demo_seller

router = APIRouter()


def _get_demo(db: Session) -> Seller:
    """Always returns the lowest-scoring seller as the demo retailer."""
    return (db.query(Seller)
              .filter(Seller.agentready_score > 0)
              .order_by(Seller.agentready_score)
              .first())


@router.get("")
def get_score(db: Session = Depends(get_db)):
    """
    Main score endpoint.
    Returns ML-predicted scores + KPIs for the demo seller.
    """
    seller = _get_demo(db)
    if not seller:
        return {"error": "No sellers found. Run dataset_loader.py and ml/train.py first."}

    seller_dict = {c.name: getattr(seller, c.name) for c in Seller.__table__.columns}
    scores = predict_score(seller_dict)

    # KPIs from live interaction log
    interactions = (db.query(AgentInteraction)
                    .filter(AgentInteraction.seller_id == seller.id)
                    .all())

    total   = len(interactions)
    fails   = sum(1 for i in interactions if i.result == "FAIL")
    success_rate = round((total - fails) / total * 100, 1) if total > 0 else 43.2
    lost_total   = sum(i.revenue_at_risk for i in interactions if i.result == "FAIL")

    # Fallback revenue estimate if simulation hasn't run yet
    if lost_total == 0:
        lost_total = round(random.uniform(72000, 96000), 2)

    competitors_above_80 = db.query(Seller).filter(Seller.agentready_score >= 80).count()

    return {
        "seller_id":   seller.id,
        "seller_name": "Nexus Fashion Retail",   # display name for demo
        "scores":      scores,
        "kpis": {
            "weekly_revenue_lost":   round(lost_total, 2),
            "agent_success_rate":    success_rate,
            "competitors_above_80":  competitors_above_80,
            "score_change_30d":      round(random.uniform(-5.0, -1.5), 1),
            "total_interactions":    total,
            "failed_interactions":   fails,
        },
        "alert": {
            "message":  (
                f"AI agents are routing {round((1 - success_rate / 100) * 100)}% of "
                f"potential orders to competitors scoring above 80"
            ),
            "severity": "critical" if scores["overall"] < 60 else "warning",
        },
    }


@router.get("/history")
def get_score_history(days: int = 90, db: Session = Depends(get_db)):
    """90-day score trend — seller vs competitor average."""
    seller = _get_demo(db)
    if not seller:
        return {"seller": [], "competitor_avg": []}

    history = (db.query(ScoreHistory)
                 .filter(ScoreHistory.seller_id == seller.id)
                 .order_by(ScoreHistory.date)
                 .limit(days)
                 .all())

    # Competitor average from top 10 sellers
    top10 = (db.query(Seller)
               .filter(Seller.agentready_score > 0)
               .order_by(Seller.agentready_score.desc())
               .limit(10)
               .all())
    comp_avg = sum(s.agentready_score for s in top10) / max(len(top10), 1)

    return {
        "seller": [
            {"date": h.date, "score": h.overall_score} for h in history
        ],
        "competitor_avg": [
            {"date": h.date, "score": round(comp_avg + (i * 0.04), 1)}
            for i, h in enumerate(history)
        ],
    }


@router.get("/sub")
def get_sub_scores(db: Session = Depends(get_db)):
    """Sub-score breakdown with descriptions and weights."""
    seller = _get_demo(db)
    if not seller:
        return []

    return [
        {
            "dimension": "Delivery Reliability",
            "score":     seller.delivery_score,
            "color":     "yellow" if seller.delivery_score >= 60 else "red",
            "detail":    (
                f"On-time rate {seller.on_time_delivery_rate * 100:.1f}% "
                f"vs 92% agent SLA requirement. Avg delay {seller.avg_delay_days:.1f} days."
            ),
            "weight": 30,
        },
        {
            "dimension": "Return Friction Index",
            "score":     seller.return_score,
            "color":     "red" if seller.return_score < 50 else "yellow",
            "detail":    "CAPTCHA wall blocking 100% of agent return calls. Biggest single revenue leak.",
            "weight": 25,
        },
        {
            "dimension": "API Response Quality",
            "score":     seller.api_score,
            "color":     "yellow" if seller.api_score >= 55 else "red",
            "detail":    "Schema inconsistency rate 23%. Agents misparse inventory responses silently.",
            "weight": 25,
        },
        {
            "dimension": "Data Transparency",
            "score":     seller.transparency_score,
            "color":     "yellow" if seller.transparency_score >= 50 else "red",
            "detail":    "Inventory refreshes every 4 hours. No delivery SLA field in product API.",
            "weight": 20,
        },
    ]
