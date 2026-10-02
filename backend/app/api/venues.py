import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List
from app.models.database import get_db
from app.models.models import Venue
from app.schemas.schemas import VenueResponse, VenueCreate, VenueUpdate

router = APIRouter(prefix="/venues", tags=["venues"])

@router.get("", response_model=List[VenueResponse])
def get_venues(event_id: str, db: DBSession = Depends(get_db)):
    return db.query(Venue).filter(Venue.event_id == event_id).all()

@router.get("/{venue_id}", response_model=VenueResponse)
def get_venue(venue_id: str, db: DBSession = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue

@router.post("", response_model=VenueResponse)
def create_venue(payload: VenueCreate, db: DBSession = Depends(get_db)):
    venue_id = payload.id or f"ven-{uuid.uuid4().hex[:8]}"
    venue = Venue(
        id=venue_id,
        event_id=payload.event_id,
        name=payload.name,
        capacity=payload.capacity,
        location=payload.location,
        equipment=payload.equipment or [],
        availability=payload.availability if payload.availability is not None else True
    )
    db.add(venue)
    db.commit()
    db.refresh(venue)
    return venue

@router.patch("/{venue_id}", response_model=VenueResponse)
def update_venue(venue_id: str, payload: VenueUpdate, db: DBSession = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(venue, field, val)

    db.commit()
    db.refresh(venue)
    return venue
