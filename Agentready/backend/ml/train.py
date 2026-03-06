# ── AgentReady Score · ml/train.py ────────────────────────────────
# Trains two ML models and saves them to models/
#
# Model 1: Random Forest Regressor  — predicts AgentReady Score 0-100
# Model 2: Isolation Forest         — detects return fraud anomalies
#
# Run: python ml/train.py

import sys
import numpy as np
import joblib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from config import MODELS_DIR
from database import SessionLocal
from models import Seller
from ml.features import engineer_features, generate_label, FEATURE_NAMES


# ──────────────────────────────────────────────────────────────────
# STEP 1 — Load sellers from DB
# ──────────────────────────────────────────────────────────────────
def load_sellers():
    db = SessionLocal()
    sellers = db.query(Seller).all()
    db.close()
    result = [
        {c.name: getattr(s, c.name) for c in Seller.__table__.columns}
        for s in sellers
    ]
    print(f"[TRAIN] Loaded {len(result):,} sellers from database.")
    return result


# ──────────────────────────────────────────────────────────────────
# STEP 2 — Build feature matrix + labels
# ──────────────────────────────────────────────────────────────────
def build_training_data(sellers):
    print("[TRAIN] Engineering features and generating labels...")
    np.random.seed(42)

    X, y = [], []
    for s in sellers:
        X.append(engineer_features(s))
        y.append(generate_label(s))

    X = np.vstack(X)
    y = np.array(y, dtype=np.float32)

    print(f"[TRAIN] Feature matrix: {X.shape}  "
          f"Labels range: {y.min():.1f} – {y.max():.1f}")
    return X, y


# ──────────────────────────────────────────────────────────────────
# STEP 3 — Train Random Forest (scoring model)
# ──────────────────────────────────────────────────────────────────
def train_scoring_model(X, y):
    print("[TRAIN] Training Random Forest Regressor...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1       # use all CPU cores
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae    = mean_absolute_error(y_test, y_pred)
    r2     = r2_score(y_test, y_pred)
    print(f"[TRAIN] Scoring model — MAE: {mae:.2f} pts  R²: {r2:.4f}")

    # Print top feature importances
    importances = sorted(
        zip(FEATURE_NAMES, model.feature_importances_),
        key=lambda x: x[1], reverse=True
    )
    print("[TRAIN] Top 5 feature importances:")
    for name, imp in importances[:5]:
        print(f"         {name:<30} {imp:.4f}")

    path = MODELS_DIR / "scoring_model.pkl"
    joblib.dump(model, path)
    print(f"[TRAIN] Saved → {path}")
    return model


# ──────────────────────────────────────────────────────────────────
# STEP 4 — Train Isolation Forest (fraud detection)
# ──────────────────────────────────────────────────────────────────
def train_fraud_model(sellers):
    """
    Unsupervised anomaly detection on return-related features.
    Learns what 'normal' return behaviour looks like, then flags outliers.

    Answers Gap 7: "What about return fraud after you remove CAPTCHA?"
    → We replace CAPTCHA with ML-based fraud detection.
    """
    print("[TRAIN] Training Isolation Forest (fraud detection)...")

    fraud_features = np.array([
        [
            float(s.get("return_proxy_rate",  0.1)),
            float(s.get("avg_review_score",   3.5)),
            float(s.get("cancellation_rate",  0.05)),
            float(s.get("order_volume_30d",   50)),
        ]
        for s in sellers
    ], dtype=np.float32)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,   # expect ~5% anomalies
        random_state=42
    )
    model.fit(fraud_features)

    # Quick sanity check
    preds = model.predict(fraud_features)
    anomaly_count = (preds == -1).sum()
    print(f"[TRAIN] Fraud model — flagged {anomaly_count} anomalies "
          f"({anomaly_count/len(sellers)*100:.1f}% of sellers)")

    path = MODELS_DIR / "fraud_model.pkl"
    joblib.dump(model, path)
    print(f"[TRAIN] Saved → {path}")
    return model


# ──────────────────────────────────────────────────────────────────
# STEP 5 — Write ML scores back to database
# ──────────────────────────────────────────────────────────────────
def update_seller_scores(sellers, scoring_model):
    """
    Runs inference on every seller and saves scores to DB.
    After this, every API call returns real ML-predicted scores.
    """
    print("[TRAIN] Writing ML scores back to database...")
    db = SessionLocal()

    for s in sellers:
        feats   = engineer_features(s).reshape(1, -1)
        overall = float(np.clip(scoring_model.predict(feats)[0], 5, 98))

        # Sub-scores derived from raw KPIs (interpretable + fast)
        delivery = float(np.clip(s.get("on_time_delivery_rate", 0.5) * 100, 10, 99))
        ret_fric = float(np.clip((1.0 - s.get("return_proxy_rate", 0.1) * 3.0) * 100, 10, 99))
        api_q    = float(np.clip((1.0 - s.get("cancellation_rate", 0.05) * 5.0) * 100, 10, 99))
        transp   = float(np.clip(min(s.get("seller_tenure_days", 180), 365) / 365.0 * 100, 15, 99))

        db.query(Seller).filter(Seller.id == s["id"]).update({
            "agentready_score":   round(overall, 1),
            "delivery_score":     round(delivery, 1),
            "return_score":       round(ret_fric, 1),
            "api_score":          round(api_q, 1),
            "transparency_score": round(transp, 1),
        })

    db.commit()
    db.close()
    print(f"[TRAIN] Scores written for {len(sellers):,} sellers.")


# ──────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  AgentReady Score — ML Training Pipeline")
    print("  Model 1: Random Forest  (AgentReady Score)")
    print("  Model 2: Isolation Forest (Fraud Detection)")
    print("=" * 60)

    sellers = load_sellers()
    if not sellers:
        print("[ERROR] No sellers found. Run dataset_loader.py first.")
        sys.exit(1)

    X, y = build_training_data(sellers)

    scoring_model = train_scoring_model(X, y)
    fraud_model   = train_fraud_model(sellers)

    update_seller_scores(sellers, scoring_model)

    print("\n[TRAIN] ✅ All done!")
    print("[TRAIN] Models saved to:  agentready/models/")
    print("[TRAIN]   scoring_model.pkl  — Random Forest")
    print("[TRAIN]   fraud_model.pkl    — Isolation Forest")
    print("[TRAIN] Next step → run:  python ml/predict.py  (test it)")
    print("=" * 60)
