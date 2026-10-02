import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List, Optional
from app.models.database import get_db
from app.models.models import Session as EventSession, Venue
from app.schemas.schemas import SessionResponse, SessionCreate, SessionUpdate

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("", response_model=List[SessionResponse])
def get_sessions(event_id: str, venue_id: Optional[str] = None, db: DBSession = Depends(get_db)):
    query = db.query(EventSession).filter(EventSession.event_id == event_id)
    if venue_id:
        query = query.filter(EventSession.venue_id == venue_id)
    return query.order_by(EventSession.start_time.asc()).all()

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(EventSession).filter(EventSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("", response_model=SessionResponse)
def create_session(payload: SessionCreate, db: DBSession = Depends(get_db)):
    session_id = payload.id or f"sess-{uuid.uuid4().hex[:8]}"
    session = EventSession(
        id=session_id,
        event_id=payload.event_id,
        title=payload.title,
        description=payload.description,
        start_time=payload.start_time,
        end_time=payload.end_time,
        venue_id=payload.venue_id,
        speaker_id=payload.speaker_id,
        speaker_name=payload.speaker_name,
        expected_attendees=payload.expected_attendees or 150,
        status=payload.status or "SCHEDULED"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(session_id: str, payload: SessionUpdate, db: DBSession = Depends(get_db)):
    session = db.query(EventSession).filter(EventSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(session, field, val)

    db.commit()
    db.refresh(session)
    return session
