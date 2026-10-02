from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List, Optional
from app.models.database import get_db
from app.models.models import Team, Member
from app.schemas.schemas import TeamResponse, MemberResponse

router = APIRouter(prefix="/teams", tags=["teams"])

@router.get("", response_model=List[TeamResponse])
def get_teams(event_id: str, db: DBSession = Depends(get_db)):
    return db.query(Team).filter(Team.event_id == event_id).all()

@router.get("/members", response_model=List[MemberResponse])
def get_members(role: Optional[str] = None, db: DBSession = Depends(get_db)):
    query = db.query(Member)
    if role:
        query = query.filter(Member.role == role)
    return query.all()

@router.get("/members/{member_id}", response_model=MemberResponse)
def get_member(member_id: str, db: DBSession = Depends(get_db)):
    mem = db.query(Member).filter(Member.id == member_id).first()
    if not mem:
        raise HTTPException(status_code=404, detail="Member not found")
    return mem
