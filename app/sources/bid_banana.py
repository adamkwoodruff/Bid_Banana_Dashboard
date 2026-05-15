import csv
from io import StringIO


def parse_bid_banana_csv(content: str):
    rows = []
    reader = csv.DictReader(StringIO(content))
    for row in reader:
        rows.append({
            "external_id": row.get("id") or row.get("opportunity_id"),
            "title": row.get("title") or "Untitled",
            "source": "Bid Banana",
            "buyer": row.get("buyer") or row.get("agency"),
            "agency": row.get("agency"),
            "deadline": row.get("deadline"),
            "posted_date": row.get("posted_date"),
            "contract_value": row.get("contract_value") or row.get("value"),
            "location": row.get("location"),
            "description": row.get("description") or row.get("summary"),
            "original_link": row.get("link") or row.get("url"),
        })
    return rows
