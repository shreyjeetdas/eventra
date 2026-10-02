import uuid
import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session as DBSession
from app.models.models import (
    Event, Session as EventSession, Task, Resource, VolunteerShift, BriefingRecord, Dependency
)
from app.integrations.ai_provider import ai_service
from app.integrations.notion_service import notion_service

class BriefingEngine:
    def __init__(self, db: DBSession, event_id: str):
        self.db = db
        self.event_id = event_id

    async def generate_briefing(self, briefing_type: str = "MORNING") -> BriefingRecord:
        """Gathers real database records and generates a structured operational briefing."""
        now = datetime.datetime.now()

        def is_overdue(deadline):
            if not deadline:
                return False
            dl = deadline.replace(tzinfo=None) if deadline.tzinfo else deadline
            return dl < now

        # 1. Fetch live metrics from DB
        tasks = self.db.query(Task).filter(Task.event_id == self.event_id).all()
        completed_tasks = [t for t in tasks if t.status == "COMPLETED"]
        blocked_tasks = [t for t in tasks if t.status == "BLOCKED" or t.blocker]
        overdue_tasks = [t for t in tasks if is_overdue(t.deadline) and t.status != "COMPLETED"]
        urgent_tasks = [t for t in tasks if t.priority in ["HIGH", "CRITICAL"] and t.status != "COMPLETED"]

        shifts = self.db.query(VolunteerShift).filter(VolunteerShift.event_id == self.event_id).all()
        confirmed_shifts = [s for s in shifts if s.assignment_status == "CONFIRMED"]
        deployment_rate = int((len(confirmed_shifts) / len(shifts) * 100)) if shifts else 100

        sessions = self.db.query(EventSession).filter(EventSession.event_id == self.event_id).all()
        upcoming_sessions = [s for s in sessions if s.status in ["SCHEDULED", "LIVE"]]

        deps = self.db.query(Dependency).filter(
            Dependency.event_id == self.event_id,
            Dependency.criticality == "CRITICAL"
        ).all()

        metrics_snapshot = {
            "total_tasks": len(tasks),
            "completed_tasks_count": len(completed_tasks),
            "active_tasks_count": len(tasks) - len(completed_tasks),
            "blocked_tasks_count": len(blocked_tasks),
            "overdue_tasks_count": len(overdue_tasks),
            "volunteer_deployment_rate": deployment_rate,
            "upcoming_sessions_count": len(upcoming_sessions),
            "critical_dependencies_count": len(deps),
            "health_score": max(40, 100 - (len(blocked_tasks) * 10) - (len(overdue_tasks) * 5))
        }

        # 2. AI synthesis
        ai_briefing = await ai_service.generate_briefing(briefing_type, metrics_snapshot)

        # 3. Store record in DB
        briefing_id = f"brf-{uuid.uuid4().hex[:8]}"
        record = BriefingRecord(
            id=briefing_id,
            event_id=self.event_id,
            briefing_type=briefing_type.upper(),
            content=ai_briefing,
            summary=ai_briefing.get("summary", "Operational daily briefing generated."),
            generated_at=now,
            saved_to_notion=False
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return record

    async def save_to_notion(self, briefing_id: str) -> Dict[str, Any]:
        """Exports and syncs briefing record to Notion workspace."""
        briefing = self.db.query(BriefingRecord).filter(BriefingRecord.id == briefing_id).first()
        if not briefing:
            return {"error": "Briefing record not found"}

        sync_result = await notion_service.sync_record(
            db=self.db,
            event_id=self.event_id,
            entity_type="BRIEFING",
            entity_id=briefing.id,
            title=briefing.content.get("title", f"Daily Briefing ({briefing.briefing_type})"),
            properties={
                "Briefing Type": briefing.briefing_type,
                "Health Score": briefing.content.get("metrics_snapshot", {}).get("health_score", 90),
                "Active Tasks": briefing.content.get("metrics_snapshot", {}).get("active_tasks_count", 0)
            },
            content_markdown=briefing.summary + "\n\n" + "\n".join([f"- {a}" for a in briefing.content.get("action_items", [])])
        )

        briefing.saved_to_notion = True
        self.db.commit()
        return sync_result
