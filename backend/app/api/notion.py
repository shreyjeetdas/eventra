import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session as DBSession
from typing import List, Dict, Any, Optional
from app.models.database import get_db
from app.models.models import NotionSyncLog, Event, Task, Session as EventSession, KnowledgeRecord
from app.schemas.schemas import NotionSyncLogResponse
from app.integrations.notion_service import notion_service

router = APIRouter(prefix="/notion", tags=["notion"])

@router.get("/status")
def get_notion_status():
    return notion_service.get_status()

@router.post("/config")
def update_notion_config(
    api_key: Optional[str] = Body(None, embed=True),
    database_mapping: Optional[Dict[str, str]] = Body(None, embed=True)
):
    if api_key:
        notion_service.update_config(api_key, database_mapping)
    return notion_service.get_status()

@router.get("/logs", response_model=List[NotionSyncLogResponse])
def get_sync_logs(event_id: str, db: DBSession = Depends(get_db)):
    return db.query(NotionSyncLog).filter(NotionSyncLog.event_id == event_id).order_by(NotionSyncLog.last_synced_at.desc()).limit(50).all()

@router.post("/sync-all")
async def sync_all_records(event_id: str, db: DBSession = Depends(get_db)):
    """Triggers complete bi-directional synchronization of event entities to Notion."""
    results = []

    # 1. Sync Event overview
    event = db.query(Event).filter(Event.id == event_id).first()
    if event:
        res = await notion_service.sync_record(
            db=db,
            event_id=event_id,
            entity_type="EVENT",
            entity_id=event.id,
            title=event.name,
            properties={"Status": event.status, "Start": event.start_date.isoformat()},
            content_markdown=f"# {event.name}\n\n{event.description}"
        )
        results.append(res)

    # 2. Sync Active Tasks
    tasks = db.query(Task).filter(Task.event_id == event_id).limit(10).all()
    for t in tasks:
        res = await notion_service.sync_record(
            db=db,
            event_id=event_id,
            entity_type="TASK",
            entity_id=t.id,
            title=t.title,
            properties={"Status": t.status, "Priority": t.priority, "Owner": t.owner_name or "Unassigned"},
            content_markdown=t.description or "Operational task item."
        )
        results.append(res)

    # 3. Sync Post-Event Knowledge records
    k_records = db.query(KnowledgeRecord).filter(KnowledgeRecord.event_id == event_id).all()
    for kr in k_records:
        res = await notion_service.sync_record(
            db=db,
            event_id=event_id,
            entity_type="KNOWLEDGE",
            entity_id=kr.id,
            title=kr.title,
            properties={"Department": kr.department, "Problem": kr.problem[:80]},
            content_markdown=f"### Root Cause\n{kr.root_cause}\n\n### Resolution\n{kr.resolution}\n\n### Lessons Learned\n{kr.lessons_learned}"
        )
        results.append(res)

    return {
        "success": True,
        "mode": notion_service.get_status()["mode"],
        "records_synced": len(results),
        "results": results
    }

@router.post("/retry/{log_id}")
async def retry_failed_sync(log_id: str, db: DBSession = Depends(get_db)):
    log = db.query(NotionSyncLog).filter(NotionSyncLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Sync log not found")

    res = await notion_service.sync_record(
        db=db,
        event_id=log.event_id,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        title=f"Retried Sync: {log.entity_type} {log.entity_id}",
        properties={"Retry": True},
        content_markdown="Retry synchronization dispatch."
    )
    return res
