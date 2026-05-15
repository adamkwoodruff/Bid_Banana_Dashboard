from datetime import date, timedelta
import csv
import io

from fastapi import FastAPI, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Opportunity
from .scoring import score_opportunity
from .dedupe import make_dedupe_key
from .sources.sam_gov import fetch_sam_opportunities
from .sources.bid_banana import parse_bid_banana_csv

app = FastAPI(title="Woodruff Opportunities Dashboard")
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

STATUSES = ["New", "Reviewing", "Interested", "Not relevant", "Bid submitted", "Archived"]


def upsert_opportunity(db: Session, payload: dict):
    key = make_dedupe_key(payload.get("title", ""), payload.get("buyer", ""), payload.get("deadline", ""))
    existing = db.query(Opportunity).filter(Opportunity.dedupe_key == key).first()
    combined_text = f"{payload.get('title','')} {payload.get('description','')} {payload.get('requirements','')}"
    score, rec, why, risks = score_opportunity(combined_text)

    if existing:
        for k, v in payload.items():
            if v is not None and v != "":
                setattr(existing, k, v)
        existing.fit_score = existing.manual_score_override if existing.manual_score_override is not None else score
        existing.recommendation = rec
        existing.why_match = why
        existing.risks = risks
        db.add(existing)
        return existing

    opp = Opportunity(**payload)
    opp.dedupe_key = key
    opp.fit_score = score
    opp.recommendation = rec
    opp.why_match = why
    opp.risks = risks
    db.add(opp)
    return opp


@app.get("/")
def index(
    request: Request,
    source: str = "",
    status: str = "",
    buyer: str = "",
    q: str = "",
    deadline_before: str = "",
    min_score: float = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Opportunity)
    if source:
        query = query.filter(Opportunity.source == source)
    if status:
        query = query.filter(Opportunity.status == status)
    if buyer:
        query = query.filter(Opportunity.buyer.ilike(f"%{buyer}%"))
    if q:
        query = query.filter(
            or_(
                Opportunity.title.ilike(f"%{q}%"),
                Opportunity.buyer.ilike(f"%{q}%"),
                Opportunity.description.ilike(f"%{q}%"),
            )
        )
    if deadline_before:
        query = query.filter(Opportunity.deadline <= deadline_before)

    query = query.filter(Opportunity.fit_score >= min_score)
    opportunities = query.order_by(Opportunity.priority.desc(), Opportunity.fit_score.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "opportunities": opportunities,
            "statuses": STATUSES,
            "filters": {
                "source": source,
                "status": status,
                "buyer": buyer,
                "q": q,
                "deadline_before": deadline_before,
                "min_score": min_score,
            },
        },
    )


@app.get("/opportunities/{opp_id}")
def detail(opp_id: int, request: Request, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return templates.TemplateResponse(
    request=request,
    name="detail.html",
    context={
        "opp": opp,
        "statuses": STATUSES,
    },
)


@app.post("/opportunities/{opp_id}/update")
def update_opp(
    opp_id: int,
    status: str = Form(None),
    notes: str = Form(""),
    manual_score_override: str = Form(""),
    priority: str = Form("off"),
    next_action: str = Form(""),
    db: Session = Depends(get_db),
):
    opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not opp:
        return RedirectResponse("/", status_code=303)
    opp.status = status or opp.status
    opp.notes = notes
    opp.next_action = next_action
    opp.priority = priority == "on"
    opp.manual_score_override = float(manual_score_override) if manual_score_override else None
    if opp.manual_score_override is not None:
        opp.fit_score = opp.manual_score_override
    db.add(opp)
    db.commit()
    return RedirectResponse(f"/opportunities/{opp_id}", status_code=303)


@app.post("/refresh/sam")
def refresh_sam(db: Session = Depends(get_db)):
    for item in fetch_sam_opportunities(limit=50, posted_from=(date.today() - timedelta(days=365)).strftime("%m/%d/%Y")):
        payload = {
            "external_id": item.get("noticeId"),
            "title": item.get("title") or "Untitled",
            "source": "SAM.gov",
            "buyer": item.get("fullParentPathName") or item.get("organizationType"),
            "agency": item.get("departmentIndAgency"),
            "deadline": item.get("responseDeadLine"),
            "posted_date": item.get("postedDate"),
            "contract_value": str(item.get("award", {}).get("amount")) if isinstance(item.get("award"), dict) and item.get("award", {}).get("amount") is not None else None,
            "location": item.get("placeOfPerformance", {}).get("city", "") if isinstance(item.get("placeOfPerformance"), dict) else None,
            "description": item.get("description"),
            "original_link": f"https://sam.gov/opp/{item.get('noticeId')}/view",
        }
        upsert_opportunity(db, payload)
    db.commit()
    return RedirectResponse("/", status_code=303)


@app.post("/import/bid-banana")
async def import_bid_banana(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8", errors="ignore")
    for row in parse_bid_banana_csv(content):
        upsert_opportunity(db, row)
    db.commit()
    return RedirectResponse("/", status_code=303)


@app.get("/export.csv")
def export_csv(db: Session = Depends(get_db)):
    rows = db.query(Opportunity).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "title", "source", "buyer", "deadline", "fit_score", "recommendation", "status", "link"])
    for r in rows:
        writer.writerow([r.id, r.title, r.source, r.buyer, r.deadline, r.fit_score, r.recommendation, r.status, r.original_link])
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=opportunities.csv"})
