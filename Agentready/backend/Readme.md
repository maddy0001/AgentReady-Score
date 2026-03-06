# AgentReady Score - Backend

## Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Load dataset
python dataset_loader.py

# Train models (optional - pre-trained models included)
python ml/train.py

# Start server
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/score` - Get AgentReady Score
- `GET /api/score/sub` - Get sub-scores
- `GET /api/score/history` - Get 90-day trend
- `GET /api/simulate/stream` - SSE simulation stream
- `GET /api/simulate/log` - Get simulation log
- `GET /api/actions` - Get action plan
- `GET /api/benchmark` - Get competitor benchmark

## Testing
```bash
# Test ML models
python ml/predict.py

# Test simulator
python simulator.py

# Test dataset loader
python dataset_loader.py
```