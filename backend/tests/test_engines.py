import pytest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal
from app.engines.graph_engine import DependencyGraphEngine
from app.engines.impact_engine import ImpactIntelligenceEngine
from app.engines.volunteer_engine import VolunteerAllocationEngine
from app.engines.simulation_engine import SimulationEngine

@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_graph_engine(db):
    engine = DependencyGraphEngine(db, "evt-kiit-techfest-2026")
    graph_data = engine.export_graph_for_visualization()
    assert graph_data["total_nodes"] > 0
    assert graph_data["total_edges"] > 0
    assert "has_cycles" in graph_data

    # Downstream impact of Auditorium 1
    downstream = engine.get_downstream_impact("ven-aud-1")
    assert len(downstream) > 0

def test_volunteer_engine(db):
    engine = VolunteerAllocationEngine(db, "evt-kiit-techfest-2026")
    proposals = engine.compute_proposals()
    assert len(proposals) > 0
    for p in proposals:
        assert p.role_required is not None
        assert p.score >= 0

def test_simulation_engine(db):
    engine = SimulationEngine(db, "evt-kiit-techfest-2026")
    res = engine.run_simulation(
        scenario_name="Test Auditorium Closure",
        description="Auditorium 1 undergoes emergency inspection",
        changes=[{"type": "VENUE", "id": "ven-aud-1", "field": "available", "value": False}]
    )
    assert res.total_conflicts_detected > 0
    assert len(res.capacity_violations) > 0
    assert res.severity_score > 0

@pytest.mark.asyncio
async def test_impact_engine(db):
    engine = ImpactIntelligenceEngine(db, "evt-kiit-techfest-2026")
    impact = await engine.analyze_change(
        entity_type="VENUE",
        entity_id="ven-aud-1",
        proposed_change={"capacity": 200, "name": "Convention Centre Hall A", "reason": "HVAC failure"}
    )
    assert impact.risk_level in ["CRITICAL", "HIGH"]
    assert len(impact.affected_sessions) > 0
    assert len(impact.recommended_actions) > 0
    assert len(impact.communication_tasks) > 0
