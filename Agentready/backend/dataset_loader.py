# ── AgentReady Score · dataset_loader.py ──────────────────────────
import sys, random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import DATA_DIR
from models import Base, Seller, Order, ScoreHistory
from database import engine, SessionLocal, init_db


def load_olist():
    print("[LOADER] Reading Olist CSVs...")
    orders_path  = DATA_DIR / "olist_orders_dataset.csv"
    items_path   = DATA_DIR / "olist_order_items_dataset.csv"
    reviews_path = DATA_DIR / "olist_order_reviews_dataset.csv"

    for p in [orders_path, items_path, reviews_path]:
        if not p.exists():
            print(f"\n[ERROR] File not found: {p}")
            print("  Download: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce")
            print(f"  Place CSVs in: {DATA_DIR}\n")
            sys.exit(1)

    df_orders  = pd.read_csv(orders_path, parse_dates=[
        "order_purchase_timestamp","order_approved_at",
        "order_delivered_customer_date","order_estimated_delivery_date"])
    df_items   = pd.read_csv(items_path)
    df_reviews = pd.read_csv(reviews_path)

    print(f"[LOADER] Orders: {len(df_orders):,}  Items: {len(df_items):,}  Reviews: {len(df_reviews):,}")

    df_items_agg = (df_items.groupby("order_id")
                    .agg(seller_id=("seller_id","first"),
                         price=("price","sum"),
                         freight_value=("freight_value","sum"))
                    .reset_index())

    df = df_orders.merge(df_items_agg, on="order_id", how="left")
    df_rev = df_reviews.groupby("order_id")["review_score"].mean().reset_index()
    df = df.merge(df_rev, on="order_id", how="left")

    df["is_late"] = (
        df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]
    ).fillna(False)

    return df


def compute_seller_kpis(df):
    print("[LOADER] Computing seller KPIs...")
    sellers = []

    for seller_id, grp in df.groupby("seller_id"):
        # skip NaN seller IDs
        if pd.isna(seller_id) or str(seller_id) == "nan":
            continue

        delivered = grp[grp["order_status"] == "delivered"]
        if len(delivered) < 5:
            continue

        on_time_rate  = len(delivered[~delivered["is_late"]]) / len(delivered)
        delays        = (delivered["order_delivered_customer_date"] - delivered["order_estimated_delivery_date"]).dt.days.clip(lower=0).fillna(0)
        avg_delay     = float(delays.mean())
        cancel_rate   = len(grp[grp["order_status"] == "canceled"]) / len(grp)
        return_proxy  = len(grp[grp["review_score"] <= 2]) / len(grp)
        avg_review    = float(grp["review_score"].mean()) if grp["review_score"].notna().any() else 3.0
        prices        = grp["price"].dropna()
        price_cons    = float(prices.std() / prices.mean()) if prices.mean() > 0 else 0.5
        resp_times    = (grp["order_approved_at"] - grp["order_purchase_timestamp"]).dt.total_seconds().div(3600).dropna()
        resp_time     = float(resp_times.median()) if len(resp_times) > 0 else 24.0
        first_order   = grp["order_purchase_timestamp"].min()
        tenure        = int((datetime(2018, 10, 1) - first_order).days) if pd.notna(first_order) else 0
        vol_30d       = max(int(len(grp) / max(tenure / 30, 1)), 1)

        sellers.append({
            "id":                    str(seller_id),
            "name":                  f"Retailer_{str(seller_id)[:8]}",
            "category":              "ecommerce",
            "on_time_delivery_rate": round(on_time_rate, 4),
            "avg_delay_days":        round(avg_delay, 2),
            "cancellation_rate":     round(cancel_rate, 4),
            "return_proxy_rate":     round(return_proxy, 4),
            "avg_review_score":      round(avg_review, 2),
            "price_consistency":     round(min(price_cons, 2.0), 4),
            "order_volume_30d":      vol_30d,
            "avg_freight_value":     round(float(grp["freight_value"].mean()), 2),
            "response_time_proxy":   round(resp_time, 2),
            "seller_tenure_days":    tenure,
        })

    print(f"[LOADER] Computed KPIs for {len(sellers):,} sellers.")
    return sellers


def seed_database(df, sellers):
    print("[LOADER] Seeding database...")
    init_db()
    db = SessionLocal()

    db.query(Seller).delete()
    db.query(Order).delete()
    db.query(ScoreHistory).delete()
    db.commit()

    # Insert sellers
    for s in sellers:
        db.add(Seller(**s))
    db.commit()
    print(f"[LOADER] Inserted {len(sellers):,} sellers.")

    # Insert orders — clean NaN values before inserting
    sample = df.sample(min(20_000, len(df)), random_state=42)
    inserted = 0
    for _, row in sample.iterrows():
        # Skip rows with NaN seller_id or price
        if pd.isna(row.get("seller_id")) or pd.isna(row.get("price")):
            continue

        # Safe review_score: must be int or None, never NaN
        rs = row.get("review_score")
        review_score = int(rs) if pd.notna(rs) else None

        # Safe freight_value
        fv = row.get("freight_value")
        freight = float(fv) if pd.notna(fv) else 0.0

        db.add(Order(
            id=str(row["order_id"]),
            seller_id=str(row["seller_id"]),
            status=str(row.get("order_status", "unknown")),
            purchase_timestamp=row.get("order_purchase_timestamp"),
            approved_at=row.get("order_approved_at") if pd.notna(row.get("order_approved_at")) else None,
            delivered_at=row.get("order_delivered_customer_date") if pd.notna(row.get("order_delivered_customer_date")) else None,
            estimated_delivery_date=row.get("order_estimated_delivery_date") if pd.notna(row.get("order_estimated_delivery_date")) else None,
            price=float(row.get("price", 0)),
            freight_value=freight,
            review_score=review_score,
            is_late=bool(row.get("is_late", False)),
        ))
        inserted += 1

    db.commit()
    db.close()
    print(f"[LOADER] Inserted {inserted:,} orders.")


def generate_score_history(sellers):
    print("[LOADER] Generating 90-day score history...")
    db = SessionLocal()
    db.query(ScoreHistory).delete()
    db.commit()

    random.seed(42)
    today = datetime.now()

    for seller in sellers[:50]:
        base = seller["on_time_delivery_rate"] * 60 + seller["avg_review_score"] * 8
        base = min(max(base, 20), 95)

        for day_offset in range(90, -1, -1):
            date  = today - timedelta(days=day_offset)
            noise = random.gauss(0, 1.5)
            score = round(min(max(base + (-day_offset * 0.02) + noise, 15), 98), 1)
            db.add(ScoreHistory(
                date=date.strftime("%Y-%m-%d"),
                seller_id=seller["id"],
                overall_score=score,
                delivery_score=round(min(score + random.gauss(0, 3), 100), 1),
                return_score=round(max(score - 20 + random.gauss(0, 4), 5), 1),
                api_score=round(min(score + random.gauss(0, 5), 100), 1),
                transparency_score=round(min(score - 5 + random.gauss(0, 3), 100), 1),
            ))

    db.commit()
    db.close()
    print("[LOADER] Score history generated.")


if __name__ == "__main__":
    print("=" * 60)
    print("  AgentReady Score — Dataset Loader")
    print("  Source: Olist Brazilian E-Commerce (100K real orders)")
    print("=" * 60)
    df      = load_olist()
    sellers = compute_seller_kpis(df)
    seed_database(df, sellers)
    generate_score_history(sellers)
    print("\n[LOADER] ✅ Complete!")
    print("[LOADER] Next step → run:  python ml/train.py")
    print("=" * 60)
