import os
import requests

SAM_API_URL = "https://api.sam.gov/prod/opportunities/v2/search"


def fetch_sam_opportunities(limit: int = 25, posted_from: str = "01/01/2025"):
    api_key = os.getenv("SAM_API_KEY")
    if not api_key:
        return []

    params = {
        "api_key": api_key,
        "limit": limit,
        "offset": 0,
        "postedFrom": posted_from,
    }
    r = requests.get(SAM_API_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("opportunitiesData", [])
