from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session as DBSession
from app.models.models import Member, VolunteerShift, Session as EventSession
from app.schemas.schemas import VolunteerAllocationProposal

# Mapping skills to shift role requirements
ROLE_SKILL_AFFINITY = {
    "AV_SUPPORT": ["AV_SETUP", "STREAMING", "RAPID_LOGISTICS"],
    "STAGE_RUNNER": ["STAGE_OPS", "RAPID_LOGISTICS", "VIP_HANDLING"],
    "CROWD_FLOW": ["CROWD_CONTROL", "REGISTRATION", "RAPID_LOGISTICS"],
    "VIP_ESCORT": ["VIP_HANDLING", "COMMUNICATIONS"],
    "BADGE_CHECK": ["REGISTRATION", "COMMUNICATIONS"],
    "GENERAL": ["RAPID_LOGISTICS", "CROWD_CONTROL"]
}

class VolunteerAllocationEngine:
    def __init__(self, db: DBSession, event_id: str):
        self.db = db
        self.event_id = event_id

    def compute_proposals(self) -> List[VolunteerAllocationProposal]:
        """Runs the multi-factor scoring optimization algorithm across unassigned/pending volunteer shifts."""
        shifts = self.db.query(VolunteerShift).filter(
            VolunteerShift.event_id == self.event_id
        ).all()

        volunteers = self.db.query(Member).filter(
            Member.role.in_(["VOLUNTEER", "VOLUNTEER_LEAD"])
        ).all()

        # Build in-memory workload and schedule tracker
        volunteer_shifts_map: Dict[str, List[VolunteerShift]] = {v.id: [] for v in volunteers}
        # Populate already confirmed shifts
        for s in shifts:
            if s.volunteer_id and s.assignment_status == "CONFIRMED":
                if s.volunteer_id in volunteer_shifts_map:
                    volunteer_shifts_map[s.volunteer_id].append(s)

        proposals = []

        for shift in shifts:
            session = self.db.query(EventSession).filter(EventSession.id == shift.session_id).first()
            session_title = session.title if session else "Operational Duty"

            # If already confirmed and manual override retained
            if shift.assignment_status == "CONFIRMED" and shift.volunteer_id:
                vol = next((v for v in volunteers if v.id == shift.volunteer_id), None)
                proposals.append(VolunteerAllocationProposal(
                    shift_id=shift.id,
                    session_title=session_title,
                    role_required=shift.role_required,
                    assigned_volunteer_id=shift.volunteer_id,
                    assigned_volunteer_name=vol.name if vol else "Assigned Volunteer",
                    score=95,
                    rationale="Manually verified and confirmed by Volunteer Lead.",
                    potential_conflicts=[]
                ))
                continue

            # Score each candidate
            best_candidate = None
            best_score = -1
            best_rationale = ""
            conflicts = []

            for vol in volunteers:
                score = 0
                reasons = []

                # 1. Availability check (30 pts)
                if not vol.availability:
                    continue

                # Time overlap check with already assigned shifts
                has_time_clash = False
                for assigned_s in volunteer_shifts_map[vol.id]:
                    # Overlap if max(start1, start2) < min(end1, end2)
                    if max(shift.start_time, assigned_s.start_time) < min(shift.end_time, assigned_s.end_time):
                        has_time_clash = True
                        break

                if has_time_clash:
                    continue  # Incompatible time slot

                score += 30
                reasons.append("Available during shift window")

                # 2. Skill match (40 pts)
                required_skills = ROLE_SKILL_AFFINITY.get(shift.role_required, ["GENERAL"])
                vol_skills = set(vol.skills or [])
                matched_skills = [s for s in required_skills if s in vol_skills]
                
                if matched_skills:
                    match_ratio = len(matched_skills) / len(required_skills)
                    skill_score = int(40 * match_ratio)
                    score += skill_score
                    reasons.append(f"Skill verified: {', '.join(matched_skills)} (+{skill_score}pts)")
                else:
                    score += 15
                    reasons.append("General aptitude match (+15pts)")

                # 3. Workload balancing (prevents burnout) (20 pts)
                # Optimal workload: 1-2 shifts. Penalize volunteers who already have 3+ shifts.
                current_load = len(volunteer_shifts_map[vol.id]) + (vol.workload or 0)
                if current_load == 0:
                    score += 20
                    reasons.append("Zero current load (optimal capacity)")
                elif current_load == 1:
                    score += 15
                    reasons.append("Balanced load (1 active shift)")
                elif current_load == 2:
                    score += 8
                    reasons.append("Moderate load (2 shifts)")
                else:
                    score += 2
                    reasons.append("High load penalty")

                # 4. Proximity / Continuity bonus (10 pts)
                score += 10

                if score > best_score:
                    best_score = score
                    best_candidate = vol
                    best_rationale = " | ".join(reasons)

            if best_candidate:
                # Tentatively record in memory tracker to balance remaining allocations
                volunteer_shifts_map[best_candidate.id].append(shift)
                proposals.append(VolunteerAllocationProposal(
                    shift_id=shift.id,
                    session_title=session_title,
                    role_required=shift.role_required,
                    assigned_volunteer_id=best_candidate.id,
                    assigned_volunteer_name=best_candidate.name,
                    score=best_score,
                    rationale=best_rationale,
                    potential_conflicts=[]
                ))
            else:
                proposals.append(VolunteerAllocationProposal(
                    shift_id=shift.id,
                    session_title=session_title,
                    role_required=shift.role_required,
                    assigned_volunteer_id=None,
                    assigned_volunteer_name=None,
                    score=0,
                    rationale="No conflict-free volunteers available with required profile.",
                    potential_conflicts=["All eligible volunteers currently committed to parallel sessions."]
                ))

        return proposals

    def apply_proposals(self, proposals: List[VolunteerAllocationProposal]) -> int:
        """Commits the approved volunteer allocations to the live database."""
        count = 0
        for prop in proposals:
            if prop.assigned_volunteer_id:
                shift = self.db.query(VolunteerShift).filter(VolunteerShift.id == prop.shift_id).first()
                if shift:
                    shift.volunteer_id = prop.assigned_volunteer_id
                    shift.assignment_status = "CONFIRMED"
                    shift.allocation_score = prop.score
                    count += 1
        self.db.commit()
        return count
