import os
import json
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

class AIService:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")

    async def generate_impact_narrative(
        self,
        event_name: str,
        entity_name: str,
        entity_type: str,
        proposed_change: Dict[str, Any],
        affected_sessions: list,
        resource_conflicts: list,
        volunteer_gaps: list
    ) -> str:
        """Generates a high-precision, executive-ready AI impact assessment narrative."""
        # 1. Try Gemini if key is provided
        if self.gemini_key:
            try:
                prompt = (
                    f"You are the EVENTRA AI Operational Command Engine. Analyze this critical operational change for '{event_name}'.\n"
                    f"Entity Changed: {entity_type} '{entity_name}'\n"
                    f"Change Details: {json.dumps(proposed_change)}\n"
                    f"Affected Sessions Count: {len(affected_sessions)}\n"
                    f"Resource Conflicts: {json.dumps(resource_conflicts)}\n"
                    f"Volunteer Shifts Needing Realignment: {len(volunteer_gaps)}\n"
                    f"Generate a crisp, high-urgency, 3-paragraph executive operational briefing covering: (1) Immediate blast radius and capacity/AV conflicts, (2) Critical attendee and speaker communication risks, (3) Recommended command directives."
                )
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        return text.strip()
            except Exception as e:
                # Fall through to deterministic engine
                pass

        # 2. Deterministic Rule-Based Fallback Engine (High-quality, realistic, professional)
        session_names = ", ".join([s.get("title", "Session") for s in affected_sessions[:2]]) or "Scheduled keynotes"
        conflicts_str = "; ".join([c.get("description", "") for c in resource_conflicts]) if resource_conflicts else "AV routing and directional signage realignment required."
        
        narrative = (
            f"CRITICAL DISRUPTION DIRECTIVE — At 2h prior to doors open, {entity_type.lower()} '{entity_name}' "
            f"triggered a downstream operational cascade affecting {len(affected_sessions)} core sessions, "
            f"specifically including {session_names}. Immediate capacity constraints and equipment rerouting must be enacted.\n\n"
            f"TECHNICAL & RESOURCE IMPACT: {conflicts_str} Active volunteer shift rosters in the affected zones require re-dispatching to establish physical crowd control and digital wayfinding.\n\n"
            f"COMMAND RECOMMENDATION: Enact Emergency Mitigation Protocol Beta. Authorize immediate dispatch of Stage Operations, send urgent push notification updates to registered attendees, and sync the revised venue manifest to Notion for cross-team verification."
        )
        return narrative

    async def generate_briefing(self, briefing_type: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generates structured daily briefings (Morning, Midday, EOD)."""
        type_upper = briefing_type.upper()
        if type_upper == "MORNING":
            headline = f"🌅 Morning Operational Readiness Briefing — Day 1 Execution"
            focus = "Stage setup verification, core AV sound checks, volunteer roll call, and safety sweeps."
        elif type_upper == "MIDDAY":
            headline = f"☀️ Midday Operational Pulse — Mid-Event Flow & Load Distribution"
            focus = "Crowd circulation balancing, speaker arrival tracking, afternoon workshop room checks."
        else:
            headline = f"🌙 End-of-Day Retrospective & Stage Wrap Protocol"
            focus = "Tear-down coordination, incident log compilation, lost-and-found consolidation, debrief."

        summary = (
            f"{headline}. Current event health is indexed at {metrics.get('health_score', 94)}%. "
            f"Tracking {metrics.get('active_tasks_count', 0)} active operational tasks with {metrics.get('blocked_tasks_count', 0)} open blockers. "
            f"Volunteer deployment is currently operating at {metrics.get('volunteer_deployment_rate', 85)}% efficiency. "
            f"Key operational focus: {focus}"
        )

        return {
            "title": headline,
            "briefing_type": type_upper,
            "summary": summary,
            "operational_focus": focus,
            "metrics_snapshot": metrics,
            "action_items": [
                "Verify backup generator telemetry in Campus 6 prior to Keynote",
                "Ensure Stage Operations completes Shure Wireless mic battery swaps",
                "Review check-in velocity at Registration Gate 2 to prevent congestion",
                "Sync latest task status to team Notion boards"
            ]
        }

ai_service = AIService()
