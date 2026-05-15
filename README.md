# Woodruff Engineering Opportunities Dashboard

Run locally:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Set env vars:

- `SAM_API_KEY` for SAM.gov API access
- `DATABASE_URL` optional (default `sqlite:///app/data/opportunities.db`)
