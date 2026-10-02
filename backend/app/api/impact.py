from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List
from app.models.database import get_db
from app.models.models import ChangeLog
from app.schemas.schemas import ImpactAnalysisRequest, ImpactAnalysisResponse, MitigationApprovalRequest, ChangeLogResponse
from app.engines.impact_engine import ImpactIntelligenceEngine

router = APIRouter(prefix="/impact", tags=["impact"])

@router.post("/analyze", response_model=ImpactAnalysisResponse)
async def analyze_change_impact(payload: ImpactAnalysisRequest, db: DBSession = Depends(get_db)):
    engine = ImpactIntelligenceEngine(db, payload.event_id)
    result = await engine.analyze_change(
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        proposed_change=payload.proposed_change
    )
    return result

@router.post("/approve")
async def approve_mitigation_plan(payload: MitigationApprovalRequest, db: DBSession = Depends(get_db)):
    engine = ImpactIntelligenceEngine(db, payload.event_id)
    result = await engine.approve_and_commit_mitigation(
        analysis=payload.analysis,
        approved_by=payload.approved_by,
        sync_to_notion=payload.sync_to_notion
    )
    return result

@router.get("/changelogs", response_model=List[ChangeLogResponse])
def get_changelogs(event_id: str, db: DBSession = Depends(get_db)):
    return db.query(ChangeLog).filter(ChangeLog.event_id == event_id).order_by(ChangeLog.created_at.desc()).all()
