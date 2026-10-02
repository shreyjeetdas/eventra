import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List
from app.models.database import get_db
from app.models.models import Dependency
from app.schemas.schemas import DependencyResponse, DependencyCreate, DependencyGraphResponse
from app.engines.graph_engine import DependencyGraphEngine

router = APIRouter(prefix="/dependencies", tags=["dependencies"])

@router.get("", response_model=List[DependencyResponse])
def get_dependencies(event_id: str, db: DBSession = Depends(get_db)):
    return db.query(Dependency).filter(Dependency.event_id == event_id).all()

@router.get("/graph", response_model=DependencyGraphResponse)
def get_dependency_graph(event_id: str, db: DBSession = Depends(get_db)):
    engine = DependencyGraphEngine(db, event_id)
    return engine.export_graph_for_visualization()

@router.get("/downstream/{node_id}")
def get_downstream_impact(event_id: str, node_id: str, db: DBSession = Depends(get_db)):
    engine = DependencyGraphEngine(db, event_id)
    return engine.get_downstream_impact(node_id)

@router.post("", response_model=DependencyResponse)
def create_dependency(payload: DependencyCreate, db: DBSession = Depends(get_db)):
    dep_id = payload.id or f"dep-{uuid.uuid4().hex[:8]}"
    dep = Dependency(
        id=dep_id,
        event_id=payload.event_id,
        source_type=payload.source_type,
        source_id=payload.source_id,
        target_type=payload.target_type,
        target_id=payload.target_id,
        dependency_type=payload.dependency_type or "REQUIRES",
        criticality=payload.criticality or "HIGH"
    )
    db.add(dep)
    db.commit()
    db.refresh(dep)
    return dep

@router.delete("/{dep_id}")
def delete_dependency(dep_id: str, db: DBSession = Depends(get_db)):
    dep = db.query(Dependency).filter(Dependency.id == dep_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Dependency not found")
    db.delete(dep)
    db.commit()
    return {"success": True, "deleted_id": dep_id}
