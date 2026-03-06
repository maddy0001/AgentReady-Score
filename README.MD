# 🤖 AgentReady Score

> **AI-Powered Diagnostic Platform for Retail API Excellence**  
> SAP × Great Lakes MBA HackFest 2026 | Theme 2: The Loyalty Paradox

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org/)
[![ML](https://img.shields.io/badge/ML-RandomForest-orange)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📖 Table of Contents

- [The Problem](#-the-problem)
- [Our Solution](#-our-solution)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Dataset](#-dataset)
- [ML Models](#-ml-models)
- [API Documentation](#-api-documentation)
- [Demo](#-demo)
- [Team](#-team)

---

## 🎯 The Problem

AI shopping agents (ChatGPT Shopping, Google Gemini Buy, Perplexity Commerce) are beginning to shop autonomously. Unlike humans, **AI agents don't see brands** — they evaluate APIs based on:

- ⚡ **Response speed** (< 1 second)
- 📋 **Data structure** (clean JSON)
- 📦 **Delivery SLAs** (clear commitments)
- 🔄 **Returns accessibility** (no CAPTCHAs)

### The Revenue Impact

A mid-market retailer loses **$750K annually** to API friction that blocks AI agents:
- $45 per API timeout
- $125 per blocked return request
- 40% conversion drop without delivery SLA
- 3-5x redundant queries due to inconsistent data

**They lose customers they never knew existed.**

---

## 💡 Our Solution

**AgentReady Score** is an ML-powered diagnostic platform that:

1. **Tests** retailer APIs like an AI agent would (5 core dimensions)
2. **Scores** operational quality 0-100 using Random Forest ML
3. **Prescribes** fixes ranked by revenue impact
4. **Simulates** AI agent behavior in real-time
5. **Benchmarks** against competitors

### The Key Insight

> *"In traditional search, Google taught retailers they need SEO to be found by humans. AgentReady Score is the SEO audit tool for AI shopping agents."*

---

## 🛠 Tech Stack

### **Backend**
- 🐍 **Python 3.11**
- ⚡ **FastAPI** - Modern async web framework
- 🗄️ **SQLAlchemy** - ORM with SQLite
- 🤖 **scikit-learn** - Random Forest + Isolation Forest
- 📊 **pandas + numpy** - Data processing

### **Machine Learning**
- **Random Forest Regressor** (scoring model)
  - Trained on 100K real orders
  - R² = 0.94, MAE = 2.1 points
  - 12 engineered features
- **Isolation Forest** (fraud detection)
  - Unsupervised anomaly detection
  - Flags suspicious return patterns

### **Frontend**
- ⚛️ **React 18** + Vite
- 🎨 **Tailwind CSS**
- 📊 **Recharts** (data visualization)
- 🔄 **Server-Sent Events** (real-time log)

### **Data Source**
- 📦 **Olist Brazilian E-Commerce Dataset**
- 100,000 real orders (2016-2018)
- 3,095 sellers
- Kaggle: [Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

---

## 📁 Project Structure

```
agentready-score/
├── backend/
│   ├── main.py                    # FastAPI application entry
│   ├── config.py                  # Configuration constants
│   ├── database.py                # SQLAlchemy setup
│   ├── models.py                  # Database models
│   ├── simulator.py               # AI agent simulator
│   ├── dataset_loader.py          # Olist data loader
│   │
│   ├── ml/
│   │   ├── features.py            # Feature engineering (12 features)
│   │   ├── train.py               # Model training pipeline
│   │   └── predict.py             # Inference engine
│   │
│   └── routers/
│       ├── score.py               # GET /api/score (main scoring)
│       ├── simulation.py          # GET /api/simulate/stream (SSE)
│       ├── actions.py             # GET /api/actions (action plan)
│       └── benchmark.py           # GET /api/benchmark (competitors)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main application
│   │   ├── main.jsx               # Entry point
│   │   ├── index.css              # Global styles
│   │   │
│   │   └── components/
│   │       ├── Sidebar.jsx        # Navigation + mini score
│   │       ├── ScoreDashboard.jsx # Score display (Screen 1)
│   │       ├── SimulationLog.jsx  # Live SSE feed (Screen 2)
│   │       ├── ActionPlan.jsx     # Ranked fixes (Screen 3)
│   │       └── BenchmarkIndex.jsx # Competitor charts (Screen 4)
│   │
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
│
├── models/
│   ├── scoring_model.pkl          # Random Forest (trained)
│   └── fraud_model.pkl            # Isolation Forest (trained)
│
├── data/
│   └── olist/
│       ├── olist_orders_dataset.csv
│       ├── olist_order_items_dataset.csv
│       └── olist_order_reviews_dataset.csv
│
├── agentready.db                  # SQLite database (auto-created)
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── .gitignore
```

---

## 🚀 Quick Start

### **Prerequisites**

- Python 3.11+
- Node.js 18+
- npm or yarn

### **Step 1: Clone Repository**

```bash
git clone https://github.com/maddy0001/AgentReady-Score.git
cd agentready-score
```

### **Step 2: Setup Backend**

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Load dataset into database
python dataset_loader.py

# Train ML models (optional - models are pre-trained)
python ml/train.py

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

Backend will be running at: **http://localhost:8000**

### **Step 3: Setup Frontend**

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be running at: **http://localhost:5173**

### **Step 4: Open Application**

Open your browser and go to: **http://localhost:5173**

---

## 📊 Dataset

### **Olist Brazilian E-Commerce Dataset**

- **Source:** [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Period:** September 2016 - August 2018
- **Scale:** 100,000 orders from 3,095 sellers
- **Real data:** Actual Brazilian retail transactions

### **Why This Dataset?**

1. **Real-world messiness** - Perfect for demonstrating API friction
2. **Rich features** - Delivery delays, reviews, cancellations
3. **Scale** - Large enough for meaningful ML training
4. **Public** - Judges can verify authenticity

### **Data Processing Pipeline**

```python
# 1. Load CSVs
dataset_loader.py

# 2. Compute seller KPIs
- on_time_delivery_rate
- avg_delay_days
- cancellation_rate
- return_proxy_rate (from bad reviews)
- avg_review_score
- price_consistency
- order_volume_30d
- avg_freight_value
- response_time_proxy
- seller_tenure_days

# 3. Generate training labels
ml/features.py → generate_label()

# 4. Train Random Forest
ml/train.py

# 5. Write scores back to DB
models.Seller.agentready_score
```

---

## 🤖 ML Models

### **Model 1: Random Forest Regressor (Scoring)**

**Purpose:** Predict AgentReady Score (0-100) for each seller

**Architecture:**
```python
RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    min_samples_leaf=4,
    random_state=42
)
```

**Performance:**
- **MAE:** 2.1 points
- **R²:** 0.94
- **Training data:** 3,095 sellers
- **Features:** 12 engineered features

**Top 5 Feature Importances:**
1. `on_time_rate` (0.28) - Most predictive
2. `reliability_index` (0.19) - Composite metric
3. `review_norm` (0.14) - Customer satisfaction
4. `delivery_review_interaction` (0.11) - Combined signal
5. `cancel_rate` (0.08) - Operational quality

**Why Random Forest?**
- Handles non-linear relationships
- Robust to outliers
- Interpretable (feature importances)
- No hyperparameter tuning needed for demo

---

### **Model 2: Isolation Forest (Fraud Detection)**

**Purpose:** Flag suspicious return patterns

**Architecture:**
```python
IsolationForest(
    n_estimators=100,
    contamination=0.05,  # Expect ~5% anomalies
    random_state=42
)
```

**Features:**
- `return_rate` - Frequency of returns
- `review_score` - Customer satisfaction
- `cancel_rate` - Order cancellations
- `order_volume` - Transaction count

**Use Case:**
Answers Gap 7: *"What about return fraud after removing CAPTCHA?"*
→ We replace CAPTCHA with ML-based fraud detection.

---

## 🌐 API Documentation

### **Base URL**
```
http://localhost:8000
```

### **Endpoints**

#### **1. Get Score**
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
    "label": "AGENT-INVISIBLE"
  },
  "kpis": {
    "weekly_revenue_lost": 18234.56,
    "agent_success_rate": 43.2,
    "competitors_above_80": 15
  }
}
```

#### **2. Get Action Plan**
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
      "title": "Return API Blocks All AI Agents via CAPTCHA",
      "annual_recovery": 2100000,
      "effort": "LOW",
      "weeks": 2
    }
  ],
  "roi_summary": {
    "total_annual_recovery": 3950000,
    "platform_cost_annual": 24000,
    "roi_multiplier": 165
  }
}
```

#### **3. Stream Simulation (SSE)**
```http
GET /api/simulate/stream
```

**Response:** Server-Sent Events
```
data: {"timestamp":"2026-03-03T10:30:15","agent_name":"ChatGPT-5 Agent","action":"Initiate return — Order #4523","result":"FAIL","revenue_at_risk":325.00}

data: {"timestamp":"2026-03-03T10:30:17","agent_name":"Gemini Shop","action":"Check delivery ETA — SKU-7834","result":"SUCCESS","revenue_at_risk":0}
```

#### **4. Get Benchmark**
```http
GET /api/benchmark
```

**Response:**
```json
{
  "competitors": [
    {"name": "FabricHub", "score": 94.2, "is_demo": false},
    {"name": "Nexus Fashion (You)", "score": 58.1, "is_demo": true}
  ],
  "vertical_stats": {
    "average_score": 76.8,
    "demo_rank": 18,
    "total_count": 23
  }
}
```

---

## 🎥 Demo

### **Live Demo**
👉 **[agentready-score.vercel.app](https://agentready-score.vercel.app)** *(coming soon)*

### **Demo Video**
📹 **[Watch 3-minute walkthrough](https://youtube.com/...)** *(coming soon)*

### **Screenshots**

#### 1. Score Dashboard
- Overall AgentReady Score (circular gauge)
- 4 sub-scores with color coding
- 90-day trend chart
- Radar chart vs competitors

#### 2. Live Simulation
- Real-time SSE feed
- Agent-by-agent breakdown
- Revenue lost counter
- Fraud detection alerts

#### 3. Action Plan
- Ranked by annual recovery
- ROI calculator (165x return)
- SAP component mapping
- Live failure counts

#### 4. Competitor Index
- All 23 real sellers
- ML-scored rankings
- 90-day projection chart
- Sub-score gap analysis

---

## 🧪 Testing

### **Run All Tests**

```bash
# Test ML pipeline
python ml/predict.py

# Test simulator
python simulator.py

# Test dataset loader
python dataset_loader.py

# Test API endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/score
```

### **Expected Output**

```
[PREDICT] ✅ All tests passed.
[SIMULATOR] ✅ Test complete.
[LOADER] ✅ Complete!
{"status":"ok","service":"AgentReady Score API","version":"1.0.0"}
```

---

## 🏗 Architecture

### **System Flow**

```
┌─────────────────────────────────────────────────────┐
│  React Frontend (Vite + Tailwind)                   │
│  ├─ ScoreDashboard: Recharts + ML predictions       │
│  ├─ SimulationLog: EventSource (SSE) real-time      │
│  ├─ ActionPlan: Ranked fixes by revenue             │
│  └─ BenchmarkIndex: Competitor analysis             │
└────────────────┬────────────────────────────────────┘
                 │ HTTP + SSE
                 ▼
┌─────────────────────────────────────────────────────┐
│  FastAPI Backend (Python)                           │
│  ├─ /api/score → ML inference (Random Forest)       │
│  ├─ /api/simulate/stream → SSE generator            │
│  ├─ /api/actions → Domain-rule action plan          │
│  └─ /api/benchmark → Competitor SQL queries         │
└────────────────┬────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐  ┌──────────────────┐
│  SQLite DB   │  │  ML Models       │
│  (3K sellers)│  │  scoring_model.pkl│
│  Orders      │  │  fraud_model.pkl  │
│  Reviews     │  └──────────────────┘
└──────────────┘
```

### **ML Training Pipeline**

```
1. dataset_loader.py
   └─> Load 100K orders from Olist CSVs
   └─> Compute seller KPIs (10 metrics)
   └─> Write to SQLite (sellers table)

2. ml/train.py
   └─> Load sellers from DB
   └─> Engineer 12 features (ml/features.py)
   └─> Generate labels (domain-rule formula)
   └─> Train Random Forest (n=200, depth=10)
   └─> Train Isolation Forest (fraud)
   └─> Save models → models/*.pkl
   └─> Write scores back to DB

3. ml/predict.py
   └─> Load models from disk
   └─> Run inference on new seller
   └─> Return 4 sub-scores + overall
```

---

## 👥 Team

Built with ❤️ at SAP × Great Lakes MBA HackFest 2026

| Name | Role |
|---|---|
| **Madhusuthanan G** | ML Engineering, Backend (FastAPI), System Architecture |
| **Shri Harsan M** | Business Strategy, Pitch & Product Vision |
| **Rohith A** | Frontend (React + Vite), UI/UX Design |
| **Kishore Kumar B N** | Frontend Components, Data Visualisation (Recharts) |
| **Melwin Davis Raj J** | Data Engineering, Olist Pipeline & Feature Engineering |

**University:** SRM Institute of Science and Technology
**Hackathon:** SAP × Great Lakes MBA HackFest 2026

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **SAP** for hosting an incredible hackathon
- **Great Lakes Institute** for the opportunity
- **Olist** for the Brazilian E-Commerce dataset
- **scikit-learn** for the ML framework
- **FastAPI** for the modern web framework

---

## 📞 Contact

**Project Repository:** [github.com/maddy0001/AgentReady-Score](https://github.com/maddy0001/AgentReady-Score)

**Live Demo:** [agentready-score.vercel.app](https://agentready-score.vercel.app)

**Email:** madhusudhanan0001@gmail.com

---

<div align="center">

### 🏆 Built for SAP × Great Lakes MBA HackFest 2026

**Theme 2: The Loyalty Paradox**

*"The retailers who optimize for AI agents first will capture the $1 trillion agentic commerce market."*

-----

Made with ❤️ using Python, React, and scikit-learn

[![Star this repo](https://img.shields.io/github/stars/maddy0001/AgentReady-Score?style=social)](https://github.com/maddy0001/AgentReady-Score)

</div>
