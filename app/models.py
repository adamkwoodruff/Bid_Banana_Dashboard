from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, index=True, nullable=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    buyer = Column(String, nullable=True)
    agency = Column(String, nullable=True)
    deadline = Column(String, nullable=True)
    posted_date = Column(String, nullable=True)
    contract_value = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    why_match = Column(Text, nullable=True)
    risks = Column(Text, nullable=True)
    documents = Column(Text, nullable=True)
    contact = Column(Text, nullable=True)
    fit_score = Column(Float, default=0.0)
    recommendation = Column(String, default="No Bid")
    status = Column(String, default="New")
    notes = Column(Text, default="")
    next_action = Column(Text, nullable=True)
    priority = Column(Boolean, default=False)
    manual_score_override = Column(Float, nullable=True)
    original_link = Column(String, nullable=True)
    dedupe_key = Column(String, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
