AI-Based Memory Forensics Analyzer - Backend
===========================================

This is the FastAPI backend for the AI-Based Memory Forensics Analyzer.

Project layout (required by spec):

- `app/main.py`
- `app/routes/`
- `app/volatility/`
- `app/ml/`
- `app/dl/`
- `app/utils/`
- `app/reports/`
- `app/schemas/`
- `app/db/`
- `app/models/`

Run locally (without Docker):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


