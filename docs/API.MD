# API Documentation

Base URL: `http://localhost:8000`

## Endpoints

### 1. Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "AgentReady Score API",
  "version": "1.0.0"
}
```

---

### 2. Get Overall Score
```http
GET /api/score
```

**Response:**
```json
{
  "seller_id": "abc123",
  "seller_name": "Nexus Fashion Retail",
  "scores": {
    "overall": 72.3,
    "delivery": 68.5,
    "return": 54.2,
    "api": 75.8,
    "transparency": 67.1,
    "label": "AGENT-INVISIBLE",
    "top_drivers": [
      {"feature": "on_time_rate", "importance": 0.28}
    ]
  },
  "kpis": {
    "weekly_revenue_lost": 18234.56,
    "agent_success_rate": 43.2,
    "competitors_above_80": 15,
    "score_change_30d": -3.2,
    "total_interactions": 847,
    "failed_interactions": 481
  },
  "alert": {
    "message": "AI agents are routing 57% of orders to competitors",
    "severity": "critical"
  }
}
```

---

### 3. Get Sub-Scores
```http
GET /api/score/sub
```

**Response:**
```json
[
  {
    "dimension": "Delivery Reliability",
    "score": 68.5,
    "color": "yellow",
    "detail": "On-time rate 68.5% vs 92% agent SLA requirement",
    "weight": 30
  }
]
```

---

### 4. Get Score History
```http
GET /api/score/history?days=90
```

**Response:**
```json
{
  "seller": [
    {"date": "2026-01-01", "score": 65.2},
    {"date": "2026-01-02", "score": 64.8}
  ],
  "competitor_avg": [
    {"date": "2026-01-01", "score": 76.8},
    {"date": "2026-01-02", "score": 77.1}
  ]
}
```

---

### 5. Stream Simulation (SSE)
```http
GET /api/simulate/stream
```

**Response:** Server-Sent Events
```
data: {"timestamp":"2026-03-03T10:30:15.123Z","agent_id":"chatgpt-5","agent_name":"ChatGPT-5 Agent","action":"Initiate return — Order #4523","action_type":"return_initiation","result":"FAIL","revenue_at_risk":325.00,"root_cause":"Return API requires CAPTCHA","fraud_score":0.234,"is_fraud_risk":false}

data: {"timestamp":"2026-03-03T10:30:17.456Z","agent_id":"gemini-shop","agent_name":"Gemini Shop","action":"Check delivery ETA — SKU-7834","action_type":"delivery_eta_check","result":"SUCCESS","revenue_at_risk":0,"root_cause":"API responded in 482ms","fraud_score":0.0,"is_fraud_risk":false}
```

---

### 6. Get Simulation Log
```http
GET /api/simulate/log?limit=50
```

**Response:**
```json
[
  {
    "id": 1,
    "timestamp": "2026-03-03T10:30:15.123Z",
    "agent_name": "ChatGPT-5 Agent",
    "action": "Initiate return",
    "result": "FAIL",
    "revenue_at_risk": 325.00,
    "root_cause": "CAPTCHA block",
    "fraud_score": 0.234,
    "is_fraud_risk": false
  }
]
```

---

### 7. Get Simulation Stats
```http
GET /api/simulate/stats
```

**Response:**
```json
{
  "total_interactions": 847,
  "total_failed": 481,
  "total_succeeded": 366,
  "success_rate": 43.2,
  "total_revenue_lost": 156234.56,
  "fraud_flags": 23,
  "top_failure_causes": [
    {"type": "return_initiation", "count": 178},
    {"type": "inventory_verify", "count": 142}
  ]
}
```

---

### 8. Get Action Plan
```http
GET /api/actions
```

**Response:**
```json
{
  "actions": [
    {
      "rank": 1,
      "priority": "CRITICAL",
      "effort": "LOW",
      "weeks": 2,
      "title": "Return API Blocks All AI Agents via CAPTCHA",
      "description": "Your return portal uses CAPTCHA...",
      "fix": "Remove CAPTCHA from /api/returns...",
      "failure_type": "return_initiation",
      "sap_component": "SAP Integration Suite",
      "annual_recovery": 2100000,
      "gap_answered": "Gap 7: fraud covered by ML",
      "live_failure_count": 178,
      "daily_loss_estimate": 5753
    }
  ],
  "roi_summary": {
    "total_annual_recovery": 3950000,
    "platform_cost_annual": 24000,
    "net_impact_year1": 3926000,
    "roi_multiplier": 165,
    "payback_days": 2
  }
}
```

---

### 9. Get Competitor Benchmark
```http
GET /api/benchmark
```

**Response:**
```json
{
  "competitors": [
    {
      "name": "FabricHub",
      "score": 94.2,
      "is_demo": false,
      "delivery": 96.1,
      "returns": 92.3,
      "api": 93.5,
      "transparency": 91.8
    },
    {
      "name": "Nexus Fashion (You)",
      "score": 58.1,
      "is_demo": true,
      "delivery": 68.5,
      "returns": 54.2,
      "api": 75.8,
      "transparency": 67.1
    }
  ],
  "vertical_stats": {
    "average_score": 76.8,
    "demo_rank": 18,
    "total_count": 23,
    "score_to_top5": 26.3,
    "top5_avg_sub": {
      "delivery": 93.2,
      "returns": 89.4,
      "api": 91.7,
      "transparency": 88.9
    }
  },
  "projection": [
    {"week": "Now", "score": 58.1},
    {"week": "Wk 2", "score": 63.1},
    {"week": "Wk 12", "score": 84.1}
  ]
}
```