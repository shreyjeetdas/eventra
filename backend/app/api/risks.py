import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List, Optional
from app.models.database import get_db
from app.models.models import Risk
from app.schemas.schemas import RiskResponse, RiskCreate

router = APIRouter(prefix="/risks", tags=["risks"])

@router.get("", response_model=List[RiskResponse])
def get_risks(
    event_id: str,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: DBSession = Depends(get_db)
):
    query = db.query(Risk).filter(Risk.event_id == event_id)
    if severity:
        query = query.filter(Risk.severity == severity)
    if status:
        query = query.filter(Risk.status == status)
    return query.all()

@router.post("", response_model=RiskResponse)
def create_risk(payload: RiskCreate, db: DBSession = Depends(get_db)):
    risk_id = payload.id or f"rsk-{uuid.uuid4().hex[:8]}"
    risk = Risk(
        id=risk_id,
        event_id=payload.event_id,
        title=payload.title,
        severity=payload.severity or "MEDIUM",
        probability=payload.probability or "MEDIUM",
        impact=payload.impact,
        mitigation=payload.mitigation,
        status=payload.status or "OPEN"
    )
    db.add(risk)
    db.commit()
    db.refresh(risk)
    return risk

@router.patch("/{risk_id}", response_model=RiskResponse)
def update_risk_status(risk_id: str, status: str, db: DBSession = Depends(get_db)):
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    risk.status = status
    db.commit()
    db.refresh(risk)
    return risk
