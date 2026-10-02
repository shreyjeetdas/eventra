import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List
from app.models.database import get_db
from app.models.models import KnowledgeRecord
from app.schemas.schemas import KnowledgeRecordResponse, KnowledgeRecordCreate
from app.integrations.notion_service import notion_service

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@router.get("", response_model=List[KnowledgeRecordResponse])
def get_knowledge_records(event_id: str, db: DBSession = Depends(get_db)):
    return db.query(KnowledgeRecord).filter(KnowledgeRecord.event_id == event_id).order_by(KnowledgeRecord.created_at.desc()).all()

@router.post("", response_model=KnowledgeRecordResponse)
async def create_knowledge_record(payload: KnowledgeRecordCreate, db: DBSession = Depends(get_db)):
    k_id = payload.id or f"knw-{uuid.uuid4().hex[:8]}"
    record = KnowledgeRecord(
        id=k_id,
        event_id=payload.event_id,
        title=payload.title,
        department=payload.department,
        problem=payload.problem,
        root_cause=payload.root_cause,
        resolution=payload.resolution,
        lessons_learned=payload.lessons_learned,
        recommended_future_action=payload.recommended_future_action,
        tags=payload.tags or [],
        source_references=payload.source_references or []
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Sync to Notion
    try:
        notion_res = await notion_service.sync_record(
            db=db,
            event_id=payload.event_id,
            entity_type="KNOWLEDGE",
            entity_id=record.id,
            title=f"Incident Post-Mortem: {record.title}",
            properties={"Department": record.department, "Tags": ", ".join(record.tags)},
            content_markdown=f"**Problem:** {record.problem}\n\n**Root Cause:** {record.root_cause}\n\n**Resolution:** {record.resolution}\n\n**Lessons Learned:** {record.lessons_learned}\n\n**Future Action:** {record.recommended_future_action}"
        )
        if notion_res.get("notion_page_id"):
            record.notion_page_id = notion_res["notion_page_id"]
            db.commit()
    except Exception:
        pass

    return record

@router.post("/{record_id}/export-notion")
async def export_to_notion(record_id: str, db: DBSession = Depends(get_db)):
    record = db.query(KnowledgeRecord).filter(KnowledgeRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Knowledge record not found")

    res = await notion_service.sync_record(
        db=db,
        event_id=record.event_id,
        entity_type="KNOWLEDGE",
        entity_id=record.id,
        title=f"Incident Post-Mortem: {record.title}",
        properties={"Department": record.department, "Tags": ", ".join(record.tags)},
        content_markdown=f"**Problem:** {record.problem}\n\n**Root Cause:** {record.root_cause}\n\n**Resolution:** {record.resolution}\n\n**Lessons Learned:** {record.lessons_learned}\n\n**Future Action:** {record.recommended_future_action}"
    )
    if res.get("notion_page_id"):
        record.notion_page_id = res["notion_page_id"]
        db.commit()
    return res
