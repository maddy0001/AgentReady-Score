# Complete Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+

## Step 1: Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/agentready-score.git
cd agentready-score
```

## Step 2: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Load dataset (creates agentready.db)
python dataset_loader.py

# Expected output:
# [LOADER] Loaded 3,095 sellers from database.
# [LOADER] ✅ Complete!

# Optional: Retrain models
python ml/train.py

# Expected output:
# [TRAIN] Scoring model — MAE: 2.1 pts  R²: 0.94
# [TRAIN] ✅ All done!

# Start backend server
uvicorn main:app --reload --port 8000
```

Backend will be running at: http://localhost:8000

## Step 3: Frontend Setup

Open a new terminal:
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be running at: http://localhost:5173

## Step 4: Verify Setup

1. Backend health check:
```bash
   curl http://localhost:8000/api/health
```

2. Get score:
```bash
   curl http://localhost:8000/api/score
```

3. Open frontend: http://localhost:5173

You should see:
- Sidebar with score
- Dashboard with charts
- Real-time simulation (auto-starts)

## Troubleshooting

### Backend Issues

**Error: "No module named 'fastapi'"**
```bash
pip install -r requirements.txt
```

**Error: "No such file or directory: agentready.db"**
```bash
python dataset_loader.py
```

**Error: "File not found: olist_orders_dataset.csv"**
- Download dataset from: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Place CSVs in: `data/olist/`

### Frontend Issues

**Error: "Cannot find module 'react'"**
```bash
cd frontend
rm -rf node_modules
npm install
```

**Error: "Failed to fetch"**
- Make sure backend is running on port 8000
- Check CORS configuration in main.py

## Next Steps

1. Review README.md for architecture
2. Test all 4 screens (dashboard, simulation, actions, benchmark)
3. Customize for your use case
4. Deploy to production (see DEPLOYMENT.md)