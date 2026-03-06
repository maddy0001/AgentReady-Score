# ── AgentReady Score · config.py ──────────────────────────────────
# All constants in one place. Change values here, everything updates.

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────
ROOT_DIR   = Path(__file__).parent.parent   # agentready/
DATA_DIR   = ROOT_DIR / "data" / "olist"    # drop CSVs here
MODELS_DIR = ROOT_DIR / "models"            # trained .pkl files
DB_PATH    = ROOT_DIR / "agentready.db"     # SQLite database

MODELS_DIR.mkdir(parents=True, exist_ok=True)

# ── Scoring weights (must sum to 1.0) ──────────────────────────────
SCORE_WEIGHTS = {
    "delivery_reliability": 0.30,
    "return_friction":      0.25,
    "api_quality":          0.25,
    "data_transparency":    0.20,
}

# ── Thresholds ─────────────────────────────────────────────────────
AGENT_PREFERRED_THRESHOLD    = 70    # score >= 70 = agent-preferred
FRAUD_RETURN_RATE_MULTIPLIER = 3.0   # >3x category avg = suspicious
FRAUD_FAST_RETURN_HOURS      = 2     # return within 2hrs = suspicious
STALE_DATA_HOURS             = 4     # inventory older than 4hrs = penalty

# ── Revenue at risk per failure type (USD range) ───────────────────
REVENUE_AT_RISK = {
    "captcha_block":       (180, 580),
    "stale_inventory":     (90,  320),
    "null_api_field":      (200, 490),
    "exchange_human_only": (300, 620),
    "schema_mismatch":     (50,  180),
    "missing_sla_field":   (60,  200),
}

# ── Simulated agent identities ─────────────────────────────────────
AGENT_PROFILES = [
    {"id": "chatgpt-5",          "name": "ChatGPT-5 Agent",    "vendor": "OpenAI"},
    {"id": "gemini-shop",        "name": "Gemini Shop",         "vendor": "Google"},
    {"id": "perplexity-buy",     "name": "Perplexity Buy",      "vendor": "Perplexity"},
    {"id": "alexa-plus",         "name": "Amazon Alexa+",       "vendor": "Amazon"},
    {"id": "apple-intelligence", "name": "Apple Intelligence",  "vendor": "Apple"},
]

# ── SAP integration config (mock endpoints for demo) ───────────────
SAP_CONFIG = {
    "s4hana_base_url":    "https://mock-s4hana.agentready.io/api/v1",
    "emarsys_base_url":   "https://mock-emarsys.agentready.io/api/v2",
    "odata_version":      "V4",
    "auth_method":        "OAuth2_ClientCredentials",
    "inventory_endpoint": "/Products?$select=ProductID,Stock,LastUpdated",
    "orders_endpoint":    "/SalesOrders?$select=OrderID,Status,DeliveryDate",
}
