import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List
from app.models.database import get_db
from app.models.models import Event, Task, Session as EventSession, Resource, VolunteerShift, Risk, ChangeLog, Dependency
from app.schemas.schemas import EventResponse, EventCreate, EventUpdate, OperationalPulseResponse
from app.integrations.notion_service import notion_service

router = APIRouter(prefix="/events", tags=["events"])

@router.get("", response_model=List[EventResponse])
def get_events(db: DBSession = Depends(get_db)):
    return db.query(Event).all()

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: DBSession = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.post("", response_model=EventResponse)
def create_event(payload: EventCreate, db: DBSession = Depends(get_db)):
    event_id = payload.id or f"evt-{payload.name.lower().replace(' ', '-')[:20]}"
    event = Event(
        id=event_id,
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=payload.status or "ACTIVE",
        organizer_id=payload.organizer_id,
        notion_page_id=payload.notion_page_id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.get("/{event_id}/pulse", response_model=OperationalPulseResponse)
def get_operational_pulse(event_id: str, db: DBSession = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    now = datetime.datetime.now()

    def is_overdue(deadline):
        if not deadline:
            return False
        dl = deadline.replace(tzinfo=None) if deadline.tzinfo else deadline
        return dl < now

    tasks = db.query(Task).filter(Task.event_id == event_id).all()
    active_tasks = [t for t in tasks if t.status != "COMPLETED"]
    overdue_tasks = [t for t in tasks if is_overdue(t.deadline) and t.status != "COMPLETED"]
    blocked_tasks = [t for t in tasks if t.status == "BLOCKED" or t.blocker]
    unresolved_blockers = [t.blocker for t in blocked_tasks if t.blocker]

    shifts = db.query(VolunteerShift).filter(VolunteerShift.event_id == event_id).all()
    confirmed_shifts = [s for s in shifts if s.assignment_status == "CONFIRMED"]
    deployment_rate = int((len(confirmed_shifts) / len(shifts) * 100)) if shifts else 100

    resources = db.query(Resource).filter(Resource.event_id == event_id).all()
    assigned_res = [r for r in resources if r.assigned_venue_id]
    res_utilization = int((len(assigned_res) / len(resources) * 100)) if resources else 100

    crit_deps = db.query(Dependency).filter(
        Dependency.event_id == event_id,
        Dependency.criticality == "CRITICAL"
    ).count()

    recent_changes = db.query(ChangeLog).filter(ChangeLog.event_id == event_id).count()

    sessions = db.query(EventSession).filter(EventSession.event_id == event_id).order_by(EventSession.start_time.asc()).limit(5).all()
    upcoming_sessions_data = [{
        "id": s.id,
        "title": s.title,
        "speaker": s.speaker_name,
        "start_time": s.start_time.isoformat(),
        "venue_id": s.venue_id,
        "status": s.status,
        "attendees": s.expected_attendees
    } for s in sessions]

    risks = db.query(Risk).filter(Risk.event_id == event_id, Risk.severity.in_(["HIGH", "CRITICAL"])).all()
    risks_data = [{
        "id": r.id,
        "title": r.title,
        "severity": r.severity,
        "mitigation": r.mitigation
    } for r in risks]

    # Calculate real dynamic health score
    health_score = max(35, 100 - (len(blocked_tasks) * 12) - (len(overdue_tasks) * 8) - (len(risks) * 5))

    pulse_text = f"Systems nominal across 6 departments. {len(active_tasks)} operations in flight. "
    if blocked_tasks:
        pulse_text = f"ATTENTION REQUIRED: {len(blocked_tasks)} active blockers detected in Tech & Stage pipelines."

    notion_stat = notion_service.get_status()

    return OperationalPulseResponse(
        event_id=event.id,
        event_name=event.name,
        event_status=event.status,
        health_score=health_score,
        pulse_summary=pulse_text,
        active_tasks_count=len(active_tasks),
        overdue_tasks_count=len(overdue_tasks),
        blocked_tasks_count=len(blocked_tasks),
        unresolved_blockers=unresolved_blockers,
        volunteer_deployment_rate=deployment_rate,
        resource_utilization_rate=res_utilization,
        critical_dependencies_count=crit_deps,
        recent_changes_count=recent_changes,
        upcoming_sessions=upcoming_sessions_data,
        high_priority_risks=risks_data,
        notion_connected=True,
        mock_notion=not notion_stat["configured"]
    )

@router.post("/{event_id}/reset-seed")
def reset_event_seed_data(event_id: str, db: DBSession = Depends(get_db)):
    """Resets the event demonstration data back to initial seed state."""
    from scripts.seed import run_seed
    try:
        run_seed()
        return {"success": True, "message": "Demo data successfully reset to initial festival state."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset seed: {str(e)}")

