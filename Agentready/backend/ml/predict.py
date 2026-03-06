# ── AgentReady Score · ml/predict.py ──────────────────────────────
# Loads saved models and runs inference.
# Called by the FastAPI routers in Segment 4.
#
# Test standalone: python ml/predict.py

import sys
import numpy as np
import joblib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MODELS_DIR
from ml.features import engineer_features, FEATURE_NAMES

# ── Module-level model cache (load once, reuse forever) ────────────
_scoring_model = None
_fraud_model   = None


def _load_models():
    global _scoring_model, _fraud_model

    sm_path = MODELS_DIR / "scoring_model.pkl"
    fm_path = MODELS_DIR / "fraud_model.pkl"

    if not sm_path.exists():
        raise FileNotFoundError(
            f"Model not found: {sm_path}\n"
            "Run:  python ml/train.py"
        )

    if _scoring_model is None:
        _scoring_model = joblib.load(sm_path)

    if _fraud_model is None and fm_path.exists():
        _fraud_model = joblib.load(fm_path)


def predict_score(seller: dict) -> dict:
    """
    Run the Random Forest on one seller dict.
    Returns overall score, 4 sub-scores, top drivers, and label.
    """
    _load_models()

    feats   = engineer_features(seller).reshape(1, -1)
    overall = float(np.clip(_scoring_model.predict(feats)[0], 5, 98))

    # Sub-scores (fast, interpretable — same formula as train.py)
    delivery = float(np.clip(seller.get("on_time_delivery_rate", 0.5) * 100, 10, 99))
    ret_fric = float(np.clip((1.0 - seller.get("return_proxy_rate", 0.1) * 3.0) * 100, 10, 99))
    api_q    = float(np.clip((1.0 - seller.get("cancellation_rate", 0.05) * 5.0) * 100, 10, 99))
    transp   = float(np.clip(min(seller.get("seller_tenure_days", 180), 365) / 365.0 * 100, 15, 99))

    # Feature importance for explainability ("why this score?")
    importances = _scoring_model.feature_importances_
    top_drivers = sorted(
        zip(FEATURE_NAMES, importances),
        key=lambda x: x[1], reverse=True
    )[:5]

    return {
        "overall":      round(overall, 1),
        "delivery":     round(delivery, 1),
        "return":       round(ret_fric, 1),
        "api":          round(api_q, 1),
        "transparency": round(transp, 1),
        "label":        "AGENT-PREFERRED" if overall >= 70 else "AGENT-INVISIBLE",
        "top_drivers": [
            {"feature": f, "importance": round(float(i), 4)}
            for f, i in top_drivers
        ],
    }


def predict_fraud_score(interaction: dict) -> float:
    """
    Run the Isolation Forest on one interaction's features.
    Returns a fraud probability 0.0 – 1.0.
    Higher = more suspicious.

    Features expected:
      return_rate   float 0-1
      review_score  float 1-5
      cancel_rate   float 0-1
      order_volume  int
    """
    _load_models()

    if _fraud_model is None:
        return 0.0

    feat = np.array([[
        float(interaction.get("return_rate",   0.1)),
        float(interaction.get("review_score",  3.5)),
        float(interaction.get("cancel_rate",   0.05)),
        float(interaction.get("order_volume",  50)),
    ]], dtype=np.float32)

    # score_samples: more negative = more anomalous
    raw_score  = float(_fraud_model.score_samples(feat)[0])
    fraud_prob = float(np.clip((-raw_score - 0.3) / 0.4, 0, 1))
    return round(fraud_prob, 3)


# ── Standalone test ────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  AgentReady Score — Prediction Test")
    print("=" * 60)

    # Test 1: a bad seller
    bad_seller = {
        "on_time_delivery_rate": 0.61,
        "avg_delay_days":        4.2,
        "cancellation_rate":     0.08,
        "return_proxy_rate":     0.22,
        "avg_review_score":      2.9,
        "price_consistency":     0.6,
        "order_volume_30d":      30,
        "avg_freight_value":     28.0,
        "response_time_proxy":   18.0,
        "seller_tenure_days":    120,
    }

    # Test 2: a good seller
    good_seller = {
        "on_time_delivery_rate": 0.94,
        "avg_delay_days":        0.4,
        "cancellation_rate":     0.01,
        "return_proxy_rate":     0.04,
        "avg_review_score":      4.7,
        "price_consistency":     0.1,
        "order_volume_30d":      200,
        "avg_freight_value":     15.0,
        "response_time_proxy":   3.0,
        "seller_tenure_days":    600,
    }

    for label, seller in [("BAD SELLER", bad_seller), ("GOOD SELLER", good_seller)]:
        result = predict_score(seller)
        print(f"\n  {label}")
        print(f"    Overall:      {result['overall']} / 100  [{result['label']}]")
        print(f"    Delivery:     {result['delivery']}")
        print(f"    Return:       {result['return']}")
        print(f"    API Quality:  {result['api']}")
        print(f"    Transparency: {result['transparency']}")
        print(f"    Top driver:   {result['top_drivers'][0]['feature']}")

    # Fraud test
    fraud_interaction = {"return_rate": 0.45, "review_score": 1.2, "cancel_rate": 0.18, "order_volume": 5}
    normal_interaction = {"return_rate": 0.05, "review_score": 4.2, "cancel_rate": 0.01, "order_volume": 150}

    print(f"\n  FRAUD TEST")
    print(f"    Suspicious interaction fraud score: {predict_fraud_score(fraud_interaction):.3f}")
    print(f"    Normal interaction fraud score:     {predict_fraud_score(normal_interaction):.3f}")

    print("\n[PREDICT] ✅ All tests passed.")
    print("=" * 60)
