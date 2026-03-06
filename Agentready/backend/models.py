# ── AgentReady Score · models.py ──────────────────────────────────
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Seller(Base):
    __tablename__ = "sellers"

    id                    = Column(String,  primary_key=True)
    name                  = Column(String,  default="Unknown Seller")
    category              = Column(String,  default="general")
    on_time_delivery_rate = Column(Float,   default=0.0)
    avg_delay_days        = Column(Float,   default=0.0)
    cancellation_rate     = Column(Float,   default=0.0)
    return_proxy_rate     = Column(Float,   default=0.0)
    avg_review_score      = Column(Float,   default=3.0)
    price_consistency     = Column(Float,   default=0.0)
    order_volume_30d      = Column(Integer, default=0)
    avg_freight_value     = Column(Float,   default=0.0)
    response_time_proxy   = Column(Float,   default=0.0)
    seller_tenure_days    = Column(Integer, default=0)
    agentready_score      = Column(Float,   default=0.0)
    delivery_score        = Column(Float,   default=0.0)
    return_score          = Column(Float,   default=0.0)
    api_score             = Column(Float,   default=0.0)
    transparency_score    = Column(Float,   default=0.0)
    created_at            = Column(DateTime, server_default=func.now())


class Order(Base):
    __tablename__ = "orders"

    id                      = Column(String,  primary_key=True)
    seller_id               = Column(String)
    status                  = Column(String)
    purchase_timestamp      = Column(DateTime)
    approved_at             = Column(DateTime, nullable=True)
    delivered_at            = Column(DateTime, nullable=True)
    estimated_delivery_date = Column(DateTime, nullable=True)
    price                   = Column(Float,   default=0.0)
    freight_value           = Column(Float,   default=0.0)
    review_score            = Column(Integer, nullable=True)
    is_late                 = Column(Boolean, default=False)


class AgentInteraction(Base):
    __tablename__ = "agent_interactions"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    timestamp       = Column(DateTime, server_default=func.now())
    agent_id        = Column(String)
    agent_name      = Column(String)
    action          = Column(String)
    action_type     = Column(String)
    result          = Column(String)
    revenue_at_risk = Column(Float,   default=0.0)
    root_cause      = Column(String,  nullable=True)
    fraud_score     = Column(Float,   default=0.0)
    is_fraud_risk   = Column(Boolean, default=False)
    seller_id       = Column(String,  nullable=True)


class ScoreHistory(Base):
    __tablename__ = "score_history"

    id                 = Column(Integer, primary_key=True, autoincrement=True)
    date               = Column(String)
    seller_id          = Column(String)
    overall_score      = Column(Float)
    delivery_score     = Column(Float)
    return_score       = Column(Float)
    api_score          = Column(Float)
    transparency_score = Column(Float)
