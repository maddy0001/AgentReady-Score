# ── AgentReady Score · ml/features.py ─────────────────────────────
# Feature engineering — converts raw seller KPIs into ML-ready numbers
# Called by train.py and predict.py

import numpy as np
import pandas as pd
from typing import Dict, Any

# The 12 feature names — same order as the array returned below
FEATURE_NAMES = [
    "on_time_rate",
    "delay_norm",
    "cancel_rate",
    "return_rate",
    "review_norm",
    "price_consistency_inv",
    "volume_log",
    "freight_norm",
    "response_time_inv",
    "tenure_norm",
    "delivery_review_interaction",
    "reliability_index",
]


def engineer_features(seller: Dict[str, Any]) -> np.ndarray:
    """
    Convert one seller dict into a 12-element feature vector.
    All values scaled to 0-1 range for the Random Forest.
    """
    on_time   = float(seller.get("on_time_delivery_rate", 0.5))
    delay     = float(seller.get("avg_delay_days",        3.0))
    cancel    = float(seller.get("cancellation_rate",     0.05))
    ret       = float(seller.get("return_proxy_rate",     0.10))
    review    = float(seller.get("avg_review_score",      3.5))
    price_c   = float(seller.get("price_consistency",     0.3))
    volume    = float(seller.get("order_volume_30d",      50))
    freight   = float(seller.get("avg_freight_value",     20.0))
    resp_time = float(seller.get("response_time_proxy",   12.0))
    tenure    = float(seller.get("seller_tenure_days",    180))

    features = np.array([
        on_time,                                          # already 0-1
        np.clip(delay / 14.0, 0, 1),                     # normalise: 0-14 days → 0-1
        np.clip(cancel, 0, 1),                            # already 0-1
        np.clip(ret, 0, 1),                               # already 0-1
        np.clip((review - 1) / 4.0, 0, 1),               # 1-5 stars → 0-1
        np.clip(1.0 - price_c, 0, 1),                    # invert: low std = better
        np.clip(np.log1p(volume) / np.log1p(1000), 0, 1),# log-scale volume
        np.clip(freight / 50.0, 0, 1),                   # normalise freight
        np.clip(1.0 - resp_time / 48.0, 0, 1),           # invert: faster = better
        np.clip(tenure / 730.0, 0, 1),                   # normalise 0-2 years
        on_time * np.clip((review - 1) / 4.0, 0, 1),    # interaction feature
        (on_time + (1 - cancel) + np.clip((review - 1) / 4.0, 0, 1)) / 3.0,  # reliability
    ], dtype=np.float32)

    return features


def generate_label(seller: Dict[str, Any]) -> float:
    """
    Domain-rule formula that creates a training label for each seller.

    WHY: We have no ground-truth "agent readiness" scores in the wild.
    So we encode business knowledge into a formula, generate labels from it,
    then train the Random Forest to learn and GENERALISE this formula.
    This is standard practice for B2B ML where labels don't exist.

    The Random Forest learns patterns beyond this formula — it finds
    non-linear interactions between features that the formula misses.
    """
    on_time = float(seller.get("on_time_delivery_rate", 0.5))
    delay   = float(seller.get("avg_delay_days",        3.0))
    cancel  = float(seller.get("cancellation_rate",     0.05))
    ret     = float(seller.get("return_proxy_rate",     0.10))
    review  = float(seller.get("avg_review_score",      3.5))
    tenure  = float(seller.get("seller_tenure_days",    180))

    # Four dimensions mapped to score components
    delivery_component  = on_time * 100 * 0.30
    friction_component  = max(0.0, (1.0 - ret * 3.0) * 100) * 0.25
    api_component       = max(0.0, (1.0 - cancel * 5.0) * 100) * 0.25
    transp_component    = min(1.0, tenure / 365.0) * 100 * 0.20

    raw = delivery_component + friction_component + api_component + transp_component

    # Review modifier: +/- 6 pts based on satisfaction
    review_mod = (review - 3.0) * 3.0

    # Add realistic noise so the model learns to generalise, not memorise
    noise = np.random.normal(0, 2.5)

    return float(np.clip(raw + review_mod + noise, 5, 98))
