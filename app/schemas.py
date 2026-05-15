from pydantic import BaseModel
from typing import Optional


class OpportunityUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    manual_score_override: Optional[float] = None
    priority: Optional[bool] = None
    next_action: Optional[str] = None


class OpportunityOut(BaseModel):
    id: int
    title: str
    source: str
    buyer: Optional[str] = None
    deadline: Optional[str] = None
    posted_date: Optional[str] = None
    contract_value: Optional[str] = None
    location: Optional[str] = None
    fit_score: float
    recommendation: str
    status: str
    original_link: Optional[str] = None

    class Config:
        from_attributes = True
