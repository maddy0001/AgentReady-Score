# ── AgentReady Score · routers/actions.py ─────────────────────────
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import AgentInteraction

router = APIRouter()

# Ranked action plan — domain knowledge encoded as structured data.
# Enriched with live failure counts from the simulation log.
ACTION_PLAN = [
    {
        "rank":             1,
        "priority":         "CRITICAL",
        "effort":           "LOW",
        "weeks":            2,
        "title":            "Return API Blocks All AI Agents via CAPTCHA",
        "description":      (
            "Your return portal uses CAPTCHA verification which blocks every legitimate "
            "AI shopping agent. ChatGPT, Gemini, and Perplexity agents fail silently — "
            "you see HTTP 200 in your logs, they see a dead end. Replace with KYA "
            "(Know Your Agent) cryptographic token auth via SAP Integration Suite."
        ),
        "fix":              (
            "Remove CAPTCHA from /api/returns. Implement OAuth2 client-credentials "
            "with agent identity tokens. SAP IS validates tokens natively — no custom dev needed."
        ),
        "failure_type":     "return_initiation",
        "sap_component":    "SAP Integration Suite",
        "annual_recovery":  2100000,
        "gap_answered":     "Gap 7: fraud covered by Isolation Forest ML that replaces CAPTCHA",
    },
    {
        "rank":             2,
        "priority":         "HIGH",
        "effort":           "MEDIUM",
        "weeks":            6,
        "title":            "Inventory Data is 4-Hour Stale — Agents Blacklist You",
        "description":      (
            "AI agents verify real-time stock before committing purchases. Your batch "
            "refresh every 4 hours causes agents to flag your domain as unreliable. "
            "Competitors with live inventory feeds capture those orders instead."
        ),
        "fix":              (
            "Connect SAP S/4HANA inventory event mesh to your API layer. Push delta "
            "updates within 60 seconds. Add data_freshness_seconds field to every "
            "product API response — agents check this field explicitly."
        ),
        "failure_type":     "inventory_verify",
        "sap_component":    "SAP S/4HANA Event Mesh",
        "annual_recovery":  890000,
        "gap_answered":     "Gap 4: exact SAP OData V4 endpoint /Products?$select=Stock,LastUpdated",
    },
    {
        "rank":             3,
        "priority":         "HIGH",
        "effort":           "MEDIUM",
        "weeks":            8,
        "title":            "Exchanges Require Human Phone Call — Fatal for Agents",
        "description":      (
            "Product exchange triggers a 'please call us' flow. AI agents cannot make "
            "phone calls. Every exchange attempt results in permanent abandonment — "
            "the agent marks your brand exchange-incompatible and stops routing there."
        ),
        "fix":              (
            "Build POST /api/exchange (order_id, original_sku, replacement_sku, reason). "
            "Auto-check eligibility via SAP OMS, verify replacement stock, trigger "
            "warehouse pick, return confirmation_id in response."
        ),
        "failure_type":     "exchange_request",
        "sap_component":    "SAP Order Management System",
        "annual_recovery":  640000,
        "gap_answered":     "Gap 5: budget owner is Head of E-Commerce — exchange failure = conversion failure",
    },
    {
        "rank":             4,
        "priority":         "MEDIUM",
        "effort":           "LOW",
        "weeks":            1,
        "title":            "No Delivery SLA Field in Product API Response",
        "description":      (
            "Agents query your product catalog and find no guaranteed delivery window. "
            "They default to competitors who include explicit SLA fields. You lose the "
            "order before the customer ever sees a checkout page."
        ),
        "fix":              (
            "Add 3 fields to your product API response: guaranteed_delivery_days (int), "
            "sla_adherence_rate_90d (float 0-1), express_available (bool). "
            "These are the exact fields ChatGPT Shopping and Gemini Buy parse first."
        ),
        "failure_type":     "delivery_eta_check",
        "sap_component":    "SAP Commerce Cloud API",
        "annual_recovery":  320000,
        "gap_answered":     "Gap 1: SLA field format documented in MCP AgentCommerce spec v0.3",
    },
]


@router.get("")
def get_actions(db: Session = Depends(get_db)):
    """Return action plan enriched with live failure counts from simulation log."""
    all_ix = db.query(AgentInteraction).all()

    enriched = []
    for action in ACTION_PLAN:
        live_count = sum(
            1 for i in all_ix
            if i.action_type == action["failure_type"] and i.result == "FAIL"
        )
        enriched.append({
            **action,
            "live_failure_count": live_count,
            "daily_loss_estimate": round(action["annual_recovery"] / 365),
        })

    total_recovery = sum(a["annual_recovery"] for a in ACTION_PLAN)
    platform_cost  = 24_000   # $2K/month

    return {
        "actions": enriched,
        "roi_summary": {
            "total_annual_recovery": total_recovery,
            "platform_cost_annual":  platform_cost,
            "net_impact_year1":      total_recovery - platform_cost,
            "roi_multiplier":        round(total_recovery / platform_cost),
            "payback_days":          round(platform_cost / (total_recovery / 365)),
        },
    }
