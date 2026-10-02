import copy
from typing import Dict, Any, List
from sqlalchemy.orm import Session as DBSession
from app.models.models import Venue, Session as EventSession, Resource, VolunteerShift, Task
from app.schemas.schemas import SimulationResponse

class SimulationEngine:
    def __init__(self, db: DBSession, event_id: str):
        self.db = db
        self.event_id = event_id

    def run_simulation(
        self,
        scenario_name: str,
        description: str,
        changes: List[Dict[str, Any]]
    ) -> SimulationResponse:
        """Runs a safe, in-memory clone what-if simulation without mutating the live database."""
        # 1. Fetch live snapshot
        live_venues = self.db.query(Venue).filter(Venue.event_id == self.event_id).all()
        live_sessions = self.db.query(EventSession).filter(EventSession.event_id == self.event_id).all()
        live_resources = self.db.query(Resource).filter(Resource.event_id == self.event_id).all()
        live_shifts = self.db.query(VolunteerShift).filter(VolunteerShift.event_id == self.event_id).all()

        # In-memory copies
        sim_venues = {v.id: {"id": v.id, "name": v.name, "capacity": v.capacity, "available": v.availability} for v in live_venues}
        sim_sessions = {s.id: {
            "id": s.id, "title": s.title, "venue_id": s.venue_id, "start_time": s.start_time,
            "end_time": s.end_time, "attendees": s.expected_attendees, "speaker": s.speaker_name
        } for s in live_sessions}
        sim_resources = {r.id: {"id": r.id, "name": r.name, "venue_id": r.assigned_venue_id, "available": r.availability} for r in live_resources}

        # 2. Apply hypothetical changes to in-memory state
        for change in changes:
            target_type = change.get("type")
            target_id = change.get("id")
            field = change.get("field")
            val = change.get("value")

            if target_type == "VENUE" and target_id in sim_venues:
                sim_venues[target_id][field] = val
            elif target_type == "SESSION" and target_id in sim_sessions:
                sim_sessions[target_id][field] = val
            elif target_type == "RESOURCE" and target_id in sim_resources:
                sim_resources[target_id][field] = val

        # 3. Analyze conflicts in simulated state
        capacity_violations = []
        equipment_shortages = []
        volunteer_shortages = []
        timeline_clashes = []
        recommended_mitigations = []

        # Check capacity & venue availability
        for s_id, s in sim_sessions.items():
            venue = sim_venues.get(s["venue_id"])
            if venue:
                if not venue.get("available", True):
                    capacity_violations.append({
                        "session": s["title"],
                        "venue": venue["name"],
                        "issue": f"Venue '{venue['name']}' marked unavailable/closed under this scenario.",
                        "deficit": s["attendees"]
                    })
                elif s["attendees"] > venue.get("capacity", 0):
                    deficit = s["attendees"] - venue["capacity"]
                    capacity_violations.append({
                        "session": s["title"],
                        "venue": venue["name"],
                        "issue": f"Over-capacity by {deficit} attendees ({s['attendees']} registered vs {venue['capacity']} seats).",
                        "deficit": deficit
                    })

        # Check equipment availability
        for r_id, r in sim_resources.items():
            if not r.get("available", True):
                venue_name = sim_venues.get(r.get("venue_id"), {}).get("name", "Unassigned")
                equipment_shortages.append({
                    "resource": r["name"],
                    "venue": venue_name,
                    "issue": f"Critical gear '{r['name']}' offline or unavailable."
                })

        # Check volunteer shortage scenarios
        if "volunteer" in scenario_name.lower() or any(c.get("type") == "VOLUNTEERS" for c in changes):
            drop_count = next((c.get("value") for c in changes if c.get("type") == "VOLUNTEERS"), 8)
            volunteer_shortages.append({
                "role": "Crowd Flow & Wayfinding",
                "shortfall": drop_count,
                "impact": f"Projected delay of 15-20 mins at entry turnstiles."
            })
            recommended_mitigations.append("Consolidate registration desks from 4 gates to 2 priority gates.")

        # Mitigations
        if capacity_violations:
            recommended_mitigations.append("Overflow livestream relay to Convention Centre Hall A foyer.")
            recommended_mitigations.append("Split attendee badge check into staggered cohort entry.")

        if equipment_shortages:
            recommended_mitigations.append("Deploy backup AV rack from Tech Hub Lab 3.")

        total_conflicts = len(capacity_violations) + len(equipment_shortages) + len(volunteer_shortages) + len(timeline_clashes)
        severity_score = min(100, total_conflicts * 25)
        is_safe = total_conflicts == 0

        return SimulationResponse(
            scenario_name=scenario_name,
            total_conflicts_detected=total_conflicts,
            capacity_violations=capacity_violations,
            equipment_shortages=equipment_shortages,
            volunteer_shortages=volunteer_shortages,
            timeline_clashes=timeline_clashes,
            recommended_mitigations=recommended_mitigations,
            severity_score=severity_score,
            is_safe_to_promote=is_safe
        )
