# ── AgentReady Score · routers/benchmark.py ───────────────────────
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Seller

router = APIRouter()

FAKE_NAMES = [
    "FabricHub", "StyleNow", "ZenWear", "ModaPlus", "SilkRoute",
    "UrbanThread", "WeaveCo", "LoftStyle", "CraftWear", "PureThread",
    "AquaMode", "BoldFit", "TrendZen", "NovaTex", "PrimeFab",
    "EliteWear", "LuxStitch", "VogueHub", "SnapStyle", "FlowWear",
    "NeatFit", "CoolThread", "BasicMode",
]


@router.get("")
def get_benchmark(db: Session = Depends(get_db)):
    """
    Competitive benchmarking.
    Top 23 real Olist sellers (by ML score) become anonymous competitors.
    Demo seller (lowest score) is highlighted in red.
    """
    # Demo seller
    demo = (db.query(Seller)
              .filter(Seller.agentready_score > 0)
              .order_by(Seller.agentready_score)
              .first())

    # Top 23 competitors
    top_sellers = (db.query(Seller)
                   .filter(Seller.agentready_score > 0)
                   .order_by(Seller.agentready_score.desc())
                   .limit(23)
                   .all())

    if not top_sellers or not demo:
        return {"competitors": [], "vertical_stats": {}, "projection": []}

    competitors = []
    for i, seller in enumerate(top_sellers):
        competitors.append({
            "name":         FAKE_NAMES[i] if i < len(FAKE_NAMES) else f"Retailer{i+1}",
            "score":        round(seller.agentready_score, 1),
            "is_demo":      False,
            "delivery":     round(seller.delivery_score, 1),
            "returns":      round(seller.return_score, 1),
            "api":          round(seller.api_score, 1),
            "transparency": round(seller.transparency_score, 1),
        })

    # Add demo seller
    competitors.append({
        "name":         "Nexus Fashion (You)",
        "score":        round(demo.agentready_score, 1),
        "is_demo":      True,
        "delivery":     round(demo.delivery_score, 1),
        "returns":      round(demo.return_score, 1),
        "api":          round(demo.api_score, 1),
        "transparency": round(demo.transparency_score, 1),
    })

    # Sort by score descending
    competitors.sort(key=lambda x: x["score"], reverse=True)

    scores    = [c["score"] for c in competitors]
    vert_avg  = round(sum(scores) / len(scores), 1)
    demo_rank = next((i + 1 for i, c in enumerate(competitors) if c["is_demo"]), len(competitors))
    demo_score = demo.agentready_score

    top5 = competitors[:5]
    top5_avg_sub = {
        "delivery":     round(sum(c["delivery"] for c in top5) / 5, 1),
        "returns":      round(sum(c["returns"] for c in top5) / 5, 1),
        "api":          round(sum(c["api"] for c in top5) / 5, 1),
        "transparency": round(sum(c["transparency"] for c in top5) / 5, 1),
    }

    # 90-day projection (fixing all 4 issues)
    projection = [
        {"week": "Now",   "score": round(demo_score, 1)},
        {"week": "Wk 2",  "score": round(demo_score + 5, 1)},
        {"week": "Wk 4",  "score": round(demo_score + 10, 1)},
        {"week": "Wk 6",  "score": round(demo_score + 15, 1)},
        {"week": "Wk 8",  "score": round(demo_score + 19, 1)},
        {"week": "Wk 10", "score": round(demo_score + 22, 1)},
        {"week": "Wk 12", "score": round(demo_score + 26, 1)},
    ]

    return {
        "competitors":    competitors,
        "vertical_stats": {
            "average_score":   vert_avg,
            "demo_rank":       demo_rank,
            "total_count":     len(competitors),
            "score_to_top5":   round(top5[4]["score"] - demo_score, 1) if len(top5) >= 5 else 0,
            "top5_avg_sub":    top5_avg_sub,
        },
        "projection": projection,
    }
