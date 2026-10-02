from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from app.models.database import get_db
from app.schemas.schemas import SimulationScenarioRequest, SimulationResponse
from app.engines.simulation_engine import SimulationEngine

router = APIRouter(prefix="/simulation", tags=["simulation"])

@router.post("/run", response_model=SimulationResponse)
def run_simulation_scenario(payload: SimulationScenarioRequest, db: DBSession = Depends(get_db)):
    engine = SimulationEngine(db, payload.event_id)
    return engine.run_simulation(
        scenario_name=payload.scenario_name,
        description=payload.description,
        changes=payload.changes
    )
