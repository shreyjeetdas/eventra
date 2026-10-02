from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List
from app.models.database import get_db
from app.models.models import VolunteerShift, Member
from app.schemas.schemas import VolunteerShiftResponse, VolunteerAllocationProposal
from app.engines.volunteer_engine import VolunteerAllocationEngine

router = APIRouter(prefix="/volunteers", tags=["volunteers"])

@router.get("/shifts", response_model=List[VolunteerShiftResponse])
def get_volunteer_shifts(event_id: str, db: DBSession = Depends(get_db)):
    return db.query(VolunteerShift).filter(VolunteerShift.event_id == event_id).all()

@router.post("/allocate/proposals", response_model=List[VolunteerAllocationProposal])
def generate_allocation_proposals(event_id: str, db: DBSession = Depends(get_db)):
    engine = VolunteerAllocationEngine(db, event_id)
    return engine.compute_proposals()

@router.post("/allocate/approve")
def approve_allocations(event_id: str, proposals: List[VolunteerAllocationProposal], db: DBSession = Depends(get_db)):
    engine = VolunteerAllocationEngine(db, event_id)
    committed_count = engine.apply_proposals(proposals)
    return {
        "success": True,
        "committed_shifts_count": committed_count,
        "message": f"Successfully allocated and confirmed {committed_count} volunteer shifts."
    }

@router.patch("/shifts/{shift_id}")
def update_shift_assignment(
    shift_id: str,
    volunteer_id: str,
    status: str = "CONFIRMED",
    db: DBSession = Depends(get_db)
):
    shift = db.query(VolunteerShift).filter(VolunteerShift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    shift.volunteer_id = volunteer_id
    shift.assignment_status = status
    db.commit()
    return {"success": True, "shift_id": shift_id, "volunteer_id": volunteer_id, "status": status}
