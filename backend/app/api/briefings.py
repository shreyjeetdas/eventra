from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List
from app.models.database import get_db
from app.models.models import BriefingRecord
from app.schemas.schemas import BriefingResponse
from app.engines.briefing_engine import BriefingEngine

router = APIRouter(prefix="/briefings", tags=["briefings"])

@router.get("", response_model=List[BriefingResponse])
def get_briefings(event_id: str, db: DBSession = Depends(get_db)):
    return db.query(BriefingRecord).filter(BriefingRecord.event_id == event_id).order_by(BriefingRecord.generated_at.desc()).all()

@router.post("/generate", response_model=BriefingResponse)
async def generate_briefing(event_id: str, briefing_type: str = "MORNING", db: DBSession = Depends(get_db)):
    engine = BriefingEngine(db, event_id)
    record = await engine.generate_briefing(briefing_type)
    return record

@router.post("/{briefing_id}/notion")
async def save_briefing_to_notion(event_id: str, briefing_id: str, db: DBSession = Depends(get_db)):
    engine = BriefingEngine(db, event_id)
    result = await engine.save_to_notion(briefing_id)
    return result
