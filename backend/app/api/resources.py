import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List, Optional
from app.models.database import get_db
from app.models.models import Resource
from app.schemas.schemas import ResourceResponse, ResourceCreate, ResourceUpdate

router = APIRouter(prefix="/resources", tags=["resources"])

@router.get("", response_model=List[ResourceResponse])
def get_resources(event_id: str, category: Optional[str] = None, db: DBSession = Depends(get_db)):
    query = db.query(Resource).filter(Resource.event_id == event_id)
    if category:
        query = query.filter(Resource.category == category)
    return query.all()

@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: str, db: DBSession = Depends(get_db)):
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resource not found")
    return res

@router.post("", response_model=ResourceResponse)
def create_resource(payload: ResourceCreate, db: DBSession = Depends(get_db)):
    res_id = payload.id or f"res-{uuid.uuid4().hex[:8]}"
    res = Resource(
        id=res_id,
        event_id=payload.event_id,
        name=payload.name,
        category=payload.category,
        quantity=payload.quantity,
        availability=payload.availability,
        assigned_venue_id=payload.assigned_venue_id
    )
    db.add(res)
    db.commit()
    db.refresh(res)
    return res

@router.patch("/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: str, payload: ResourceUpdate, db: DBSession = Depends(get_db)):
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resource not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(res, field, val)

    db.commit()
    db.refresh(res)
    return res
