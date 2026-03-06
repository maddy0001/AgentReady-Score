# ── AgentReady Score · simulator.py ───────────────────────────────
# Simulates AI shopping agents hitting a retailer's API.
# Generates realistic FAIL/SUCCESS interactions based on friction config.
# No LLM API key needed — rule-based with realistic randomness.
#
# Test standalone: python simulator.py

import asyncio
import random
from datetime import datetime
from typing import AsyncGenerator, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import AGENT_PROFILES, REVENUE_AT_RISK
from database import SessionLocal
from models import AgentInteraction, Seller
from ml.predict import predict_fraud_score

random.seed()  # new seed each run for variety

# ── Retailer friction config ────────────────────────────────────────
# These are the "broken things" our platform has diagnosed.
# Each one maps to an action template failure below.
FRICTION_CONFIG = {
    "captcha_on_returns":        True,   # blocks ALL agent return calls
    "inventory_stale_hours":     4,      # 4h stale = agents flag unreliable
    "exchange_requires_human":   True,   # agents can't make phone calls
    "missing_sla_field":         True,   # no delivery guarantee in API
    "avg_api_response_ms":       2800,   # slow
    "schema_inconsistency_rate": 0.23,   # 23% of responses misparse
}

# ── Items and sizes for realistic action text ───────────────────────
ITEMS = [
    "Jacket (M)", "Sneakers (42)", "Dress (S)", "Shirt (L)",
    "Jeans (32)", "Coat (XL)", "Hoodie (M)", "Watch",
    "Handbag", "Sunglasses", "Boots (38)", "Sweater (L)",
]
SIZES = ["XS", "S", "M", "L", "XL", "XXL"]


def _order_id(): return str(random.randint(4000, 7999))
def _sku():      return str(random.randint(1000, 9999))
def _item():     return random.choice(ITEMS)
def _size():     return random.choice(SIZES)


# ── Action templates ───────────────────────────────────────────────
# Each template defines:
#   - what action the agent tries
#   - whether it fails given the current friction config
#   - what error to report if it fails
#   - whether the action is fraud-relevant
ACTION_TEMPLATES = [
    {
        "type":       "return_initiation",
        "template":   "Initiate return — Order #{order_id} · {item}",
        "fails_when": lambda f: f["captcha_on_returns"],
        "fail_cause": "captcha_block",
        "root_cause": "Return API requires CAPTCHA — agent blocked (HTTP 403). Revenue lost silently.",
        "fraud_relevant": True,
    },
    {
        "type":       "delivery_eta_check",
        "template":   "Check delivery ETA — SKU-{sku} · {item}",
        "fails_when": lambda f: f["missing_sla_field"],
        "fail_cause": "missing_sla_field",
        "root_cause": "No guaranteed_delivery_days field in API response — agent cannot compare SLAs.",
        "fraud_relevant": False,
    },
    {
        "type":       "inventory_verify",
        "template":   "Verify live stock — SKU-{sku} · {item}",
        "fails_when": lambda f: f["inventory_stale_hours"] > 2,
        "fail_cause": "stale_inventory",
        "root_cause": f"Inventory data {FRICTION_CONFIG['inventory_stale_hours']}h stale — agent flagged as unreliable source.",
        "fraud_relevant": False,
    },
    {
        "type":       "exchange_request",
        "template":   "Process exchange — Order #{order_id} → size {size}",
        "fails_when": lambda f: f["exchange_requires_human"],
        "fail_cause": "exchange_human_only",
        "root_cause": "Exchange portal redirects to phone call — agent cannot proceed autonomously.",
        "fraud_relevant": True,
    },
    {
        "type":       "price_check",
        "template":   "Compare price — {item} across vendors",
        "fails_when": lambda f: False,
        "fail_cause": None,
        "root_cause": None,
        "fraud_relevant": False,
    },
    {
        "type":       "refund_status",
        "template":   "Check refund status — Order #{order_id}",
        "fails_when": lambda f: False,
        "fail_cause": None,
        "root_cause": None,
        "fraud_relevant": False,
    },
    {
        "type":       "schema_parse",
        "template":   "Parse catalog API — SKU-{sku} product details",
        "fails_when": lambda f: random.random() < f["schema_inconsistency_rate"],
        "fail_cause": "schema_mismatch",
        "root_cause": "API schema inconsistency — agent received unexpected field types (null vs string).",
        "fraud_relevant": False,
    },
    {
        "type":       "reorder",
        "template":   "Place reorder — SKU-{sku} · {item}",
        "fails_when": lambda f: False,
        "fail_cause": None,
        "root_cause": None,
        "fraud_relevant": False,
    },
]


def generate_interaction(seller: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate one realistic agent interaction dict."""
    agent    = random.choice(AGENT_PROFILES)
    template = random.choice(ACTION_TEMPLATES)

    # Build action text
    action = (template["template"]
              .replace("{order_id}", _order_id())
              .replace("{sku}", _sku())
              .replace("{item}", _item())
              .replace("{size}", _size()))

    is_fail = template["fails_when"](FRICTION_CONFIG)
    result  = "FAIL" if is_fail else "SUCCESS"

    # Calculate revenue at risk for failures
    revenue = 0.0
    if is_fail and template["fail_cause"]:
        lo, hi = REVENUE_AT_RISK.get(template["fail_cause"], (50, 200))
        revenue = round(random.uniform(lo, hi), 2)

    # Success root cause (response time)
    response_ms = random.randint(380, 1400)
    success_msg = f"API responded in {response_ms}ms — parsed successfully ✓"

    # Fraud scoring (only for fraud-relevant actions)
    fraud_score   = 0.0
    is_fraud_risk = False

    if template["fraud_relevant"] and seller:
        fraud_score = predict_fraud_score({
            "return_rate":   seller.get("return_proxy_rate",  0.1),
            "review_score":  seller.get("avg_review_score",   3.5),
            "cancel_rate":   seller.get("cancellation_rate",  0.05),
            "order_volume":  seller.get("order_volume_30d",   50),
        })
        # Only flag as fraud risk if score > 0.7 AND action actually failed
        is_fraud_risk = (fraud_score > 0.7) and is_fail

    return {
        "timestamp":     datetime.now().isoformat(),
        "agent_id":      agent["id"],
        "agent_name":    agent["name"],
        "agent_vendor":  agent["vendor"],
        "action":        action,
        "action_type":   template["type"],
        "result":        result,
        "revenue_at_risk": revenue,
        "root_cause":    template["root_cause"] if is_fail else success_msg,
        "fraud_score":   round(fraud_score, 3),
        "is_fraud_risk": is_fraud_risk,
    }


async def stream_interactions(
    seller: Dict[str, Any] = None,
    interval_seconds: float = 2.0,
    max_events: int = 500,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Async generator — yields one interaction every interval_seconds.
    Used by the SSE endpoint in routers/simulation.py.
    Persists each interaction to the DB as it's generated.
    """
    db = SessionLocal()
    count = 0
    try:
        while count < max_events:
            ix = generate_interaction(seller)

            db.add(AgentInteraction(
                agent_id=ix["agent_id"],
                agent_name=ix["agent_name"],
                action=ix["action"],
                action_type=ix["action_type"],
                result=ix["result"],
                revenue_at_risk=ix["revenue_at_risk"],
                root_cause=ix["root_cause"],
                fraud_score=ix["fraud_score"],
                is_fraud_risk=ix["is_fraud_risk"],
                seller_id=seller.get("id") if seller else None,
            ))
            db.commit()

            yield ix
            count += 1
            await asyncio.sleep(interval_seconds)
    finally:
        db.close()


def get_demo_seller() -> Dict[str, Any]:
    """Returns the lowest-scoring seller for the demo (most dramatic effect)."""
    db = SessionLocal()
    seller = (db.query(Seller)
               .filter(Seller.agentready_score > 0)
               .order_by(Seller.agentready_score)
               .first())
    db.close()
    if not seller:
        return {}
    return {c.name: getattr(seller, c.name) for c in Seller.__table__.columns}


# ── Standalone test ────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  AgentReady Score — Simulator Test (5 interactions)")
    print("=" * 60)

    seller = get_demo_seller()
    print(f"  Demo seller score: {seller.get('agentready_score', '?')}\n")

    for i in range(5):
        ix = generate_interaction(seller)
        status = "❌ FAIL" if ix["result"] == "FAIL" else "✅ OK  "
        fraud  = f" ⚠ FRAUD {ix['fraud_score']:.2f}" if ix["is_fraud_risk"] else ""
        rev    = f"  ${ix['revenue_at_risk']:.0f} lost" if ix["revenue_at_risk"] > 0 else ""
        print(f"  {status} | {ix['agent_name']:<22} | {ix['action'][:45]:<45}{rev}{fraud}")

    print("\n[SIMULATOR] ✅ Test complete.")
    print("=" * 60)
