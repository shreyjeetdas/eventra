import uuid
import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session as DBSession
from app.models.models import (
    Venue, Session as EventSession, Task, Resource, VolunteerShift, Team, ChangeLog
)
from app.engines.graph_engine import DependencyGraphEngine
from app.integrations.ai_provider import ai_service
from app.integrations.notion_service import notion_service
from app.schemas.schemas import ImpactAnalysisResponse, ProposedAction

class ImpactIntelligenceEngine:
    def __init__(self, db: DBSession, event_id: str):
        self.db = db
        self.event_id = event_id
        self.graph_engine = DependencyGraphEngine(db, event_id)

    async def analyze_change(
        self,
        entity_type: str,
        entity_id: str,
        proposed_change: Dict[str, Any]
    ) -> ImpactAnalysisResponse:
        """Performs rigorous deterministic dependency traversal and AI synthesis of change impact."""
        # 1. Fetch source entity
        entity_name = entity_id
        current_entity_data = {}
        if entity_type == "VENUE":
            v = self.db.query(Venue).filter(Venue.id == entity_id).first()
            if v:
                entity_name = v.name
                current_entity_data = {"capacity": v.capacity, "location": v.location, "equipment": v.equipment}
        elif entity_type == "SESSION":
            s = self.db.query(EventSession).filter(EventSession.id == entity_id).first()
            if s:
                entity_name = s.title
                current_entity_data = {"venue_id": s.venue_id, "start_time": s.start_time.isoformat()}

        # 2. Query Downstream Affected Records via Directed Graph Traversal
        downstream = self.graph_engine.get_downstream_impact(entity_id)
        blast_radius = len(downstream)

        # 3. Detect Affected Sessions & Capacity Clashes
        affected_sessions = []
        resource_conflicts = []
        affected_people = []
        volunteer_gaps = []
        comm_tasks = []

        if entity_type == "VENUE":
            # Find all sessions hosted in this venue
            hosted_sessions = self.db.query(EventSession).filter(
                EventSession.event_id == self.event_id,
                EventSession.venue_id == entity_id
            ).all()

            new_capacity = proposed_change.get("capacity")
            new_venue_name = proposed_change.get("name", "Target Alternate Hall")

            for s in hosted_sessions:
                is_capacity_conflict = False
                clash_details = None
                if new_capacity and s.expected_attendees > new_capacity:
                    is_capacity_conflict = True
                    deficit = s.expected_attendees - new_capacity
                    clash_details = f"Capacity deficit: {s.expected_attendees} registered vs {new_capacity} max seats in {new_venue_name} (-{deficit} seats)"

                affected_sessions.append({
                    "session_id": s.id,
                    "title": s.title,
                    "speaker": s.speaker_name,
                    "expected_attendees": s.expected_attendees,
                    "start_time": s.start_time.isoformat(),
                    "capacity_clash": is_capacity_conflict,
                    "clash_details": clash_details
                })

                if s.speaker_name:
                    affected_people.append({
                        "name": s.speaker_name,
                        "role": "Keynote Speaker",
                        "impact": f"Room change for '{s.title}' requires speaker escort reassignment."
                    })

                # Check volunteer shifts for this session
                shifts = self.db.query(VolunteerShift).filter(VolunteerShift.session_id == s.id).all()
                for sh in shifts:
                    volunteer_gaps.append({
                        "shift_id": sh.id,
                        "role": sh.role_required,
                        "assigned_volunteer_id": sh.volunteer_id,
                        "action_needed": f"Re-route shift to {new_venue_name}"
                    })

            # Check equipment assigned to this venue
            resources = self.db.query(Resource).filter(
                Resource.event_id == self.event_id,
                Resource.assigned_venue_id == entity_id
            ).all()

            for r in resources:
                resource_conflicts.append({
                    "resource_id": r.id,
                    "name": r.name,
                    "category": r.category,
                    "description": f"Dedicated gear '{r.name}' currently deployed at {entity_name} needs physical transfer."
                })

        # Build communication requirements
        comm_tasks.append("Send push notification to all registered attendees regarding venue/room adjustment.")
        comm_tasks.append("Update digital signage and wayfinding screens across Campus 6 / Convention Center.")
        comm_tasks.append("Notify speaker logistics liaison to re-route VIP convoy.")
        comm_tasks.append("Issue emergency operational dispatch to volunteer coordinators.")

        # Determine Risk Level
        has_major_clash = any(s.get("capacity_clash") for s in affected_sessions)
        if blast_radius > 6 or has_major_clash or proposed_change.get("availability") is False:
            risk_level = "CRITICAL"
        elif blast_radius > 2:
            risk_level = "HIGH"
        else:
            risk_level = "MEDIUM"

        # 4. Generate AI Executive Narrative
        ai_narrative = await ai_service.generate_impact_narrative(
            event_name="KIIT Technical Fest 2026",
            entity_name=entity_name,
            entity_type=entity_type,
            proposed_change=proposed_change,
            affected_sessions=affected_sessions,
            resource_conflicts=resource_conflicts,
            volunteer_gaps=volunteer_gaps
        )

        # 5. Formulate Structured Action Plan with Department Owners
        recommended_actions = [
            ProposedAction(
                id=f"act-{uuid.uuid4().hex[:6]}",
                title="Reroute AV & Stage Wiring to New Hall",
                department="Tech & AV",
                priority="CRITICAL",
                deadline_offset_minutes=30,
                description="Move wireless mic receiver banks, stage monitors, and calibrate projection system in alternate venue."
            ),
            ProposedAction(
                id=f"act-{uuid.uuid4().hex[:6]}",
                title="Broadcast In-App & SMS Venue Relocation Alert",
                department="Marketing & Comms",
                priority="CRITICAL",
                deadline_offset_minutes=15,
                description="Trigger high-priority notification to registered attendees and display flash banner on event portal."
            ),
            ProposedAction(
                id=f"act-{uuid.uuid4().hex[:6]}",
                title="Deploy 6 Volunteers to Wayfinding Chokepoints",
                department="Volunteer Ops",
                priority="HIGH",
                deadline_offset_minutes=20,
                description="Station volunteer marshals outside original hall with directional signs to guide participant flow."
            ),
            ProposedAction(
                id=f"act-{uuid.uuid4().hex[:6]}",
                title="Brief Keynote Speaker & VIP Escort Team",
                department="Hospitality & Registration",
                priority="HIGH",
                deadline_offset_minutes=25,
                description="Inform speaker liaison of the greenroom location shift and adjust soundcheck schedule."
            )
        ]

        change_summary = f"{entity_type} '{entity_name}' modified: {proposed_change.get('reason', 'Operational change detected')}."

        return ImpactAnalysisResponse(
            change_summary=change_summary,
            risk_level=risk_level,
            affected_sessions=affected_sessions,
            affected_people=affected_people,
            resource_conflicts=resource_conflicts,
            communication_tasks=comm_tasks,
            ai_narrative=ai_narrative,
            recommended_actions=recommended_actions,
            approval_required=True,
            deterministic_blast_radius=blast_radius
        )

    async def approve_and_commit_mitigation(
        self,
        analysis: ImpactAnalysisResponse,
        approved_by: str = "Admin Lead",
        sync_to_notion: bool = True
    ) -> Dict[str, Any]:
        """Commits the approved mitigation plan: creates follow-up tasks, records changelog, and syncs to Notion."""
        # 1. Fetch team mappings
        teams = self.db.query(Team).filter(Team.event_id == self.event_id).all()
        team_map = {t.department: t.id for t in teams}

        created_tasks = []
        for action in analysis.recommended_actions:
            team_id = team_map.get(action.department)
            task_id = f"task-{uuid.uuid4().hex[:8]}"
            deadline = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=action.deadline_offset_minutes)

            new_task = Task(
                id=task_id,
                event_id=self.event_id,
                title=f"[MITIGATION] {action.title}",
                description=action.description,
                owner_id=None,
                owner_name=f"{action.department} Lead",
                team_id=team_id,
                deadline=deadline,
                priority=action.priority,
                status="TODO",
                blocker=None,
                escalation_level=2 if action.priority == "CRITICAL" else 1,
                comments=[{
                    "author": approved_by,
                    "text": f"Auto-generated from approved Impact Mitigation Plan for: {analysis.change_summary}",
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }]
            )
            self.db.add(new_task)
            created_tasks.append(task_id)

        # 2. Record ChangeLog
        log_id = f"log-{uuid.uuid4().hex[:8]}"
        chg = ChangeLog(
            id=log_id,
            event_id=self.event_id,
            entity_type="IMPACT_MITIGATION",
            entity_id=log_id,
            previous_value={"risk_level": analysis.risk_level},
            new_value={"actions_created": len(created_tasks), "status": "APPROVED"},
            impact_summary=f"{analysis.change_summary} -> Approved by {approved_by}. {len(created_tasks)} mitigation tasks deployed.",
            approved=True,
            created_at=datetime.datetime.now(datetime.timezone.utc)
        )
        self.db.add(chg)
        self.db.commit()

        # 3. Synchronize to Notion
        notion_result = None
        if sync_to_notion:
            notion_result = await notion_service.sync_record(
                db=self.db,
                event_id=self.event_id,
                entity_type="CHANGELOG",
                entity_id=log_id,
                title=f"🚨 Approved Mitigation: {analysis.change_summary}",
                properties={
                    "Risk Level": analysis.risk_level,
                    "Mitigation Tasks": len(created_tasks),
                    "Approved By": approved_by
                },
                content_markdown=f"{analysis.ai_narrative}\n\n**Generated Tasks:**\n" + "\n".join([f"- {a.title} ({a.department})" for a in analysis.recommended_actions])
            )

        return {
            "success": True,
            "created_tasks_count": len(created_tasks),
            "created_tasks": created_tasks,
            "changelog_id": log_id,
            "notion_sync": notion_result
        }
