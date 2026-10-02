import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List, Optional
from app.models.database import get_db
from app.models.models import Task, Team
from app.schemas.schemas import TaskResponse, TaskCreate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("", response_model=List[TaskResponse])
def get_tasks(
    event_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    team_id: Optional[str] = None,
    escalation_min: Optional[int] = None,
    db: DBSession = Depends(get_db)
):
    query = db.query(Task).filter(Task.event_id == event_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if team_id:
        query = query.filter(Task.team_id == team_id)
    if escalation_min is not None:
        query = query.filter(Task.escalation_level >= escalation_min)
    return query.order_by(Task.escalation_level.desc(), Task.created_at.desc()).all()

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: DBSession = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("", response_model=TaskResponse)
def create_task(payload: TaskCreate, db: DBSession = Depends(get_db)):
    task_id = payload.id or f"task-{uuid.uuid4().hex[:8]}"
    task = Task(
        id=task_id,
        event_id=payload.event_id,
        title=payload.title,
        description=payload.description,
        owner_id=payload.owner_id,
        owner_name=payload.owner_name or "Operations Crew",
        team_id=payload.team_id,
        deadline=payload.deadline,
        priority=payload.priority or "MEDIUM",
        status=payload.status or "TODO",
        blocker=payload.blocker,
        escalation_level=payload.escalation_level or 0,
        comments=[]
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, payload: TaskUpdate, db: DBSession = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(task, field, val)

    task.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(task)
    return task

@router.post("/{task_id}/escalate", response_model=TaskResponse)
def escalate_task(task_id: str, reason: Optional[str] = "Critical blocker encountered", db: DBSession = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.escalation_level = min(3, (task.escalation_level or 0) + 1)
    task.priority = "CRITICAL"
    if reason and not task.blocker:
        task.blocker = reason

    existing_comments = list(task.comments or [])
    existing_comments.append({
        "author": "Control Room Escalation System",
        "text": f"Escalated to Level {task.escalation_level}: {reason}",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    })
    task.comments = existing_comments

    task.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(task)
    return task
