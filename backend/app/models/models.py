import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="ACTIVE")  # PLANNING, ACTIVE, COMPLETED, ARCHIVED
    organizer_id = Column(String, nullable=True)
    notion_page_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Relationships
    sessions = relationship("Session", back_populates="event", cascade="all, delete-orphan")
    venues = relationship("Venue", back_populates="event", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="event", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="event", cascade="all, delete-orphan")
    resources = relationship("Resource", back_populates="event", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="event", cascade="all, delete-orphan")
    changelogs = relationship("ChangeLog", back_populates="event", cascade="all, delete-orphan")
    synclogs = relationship("NotionSyncLog", back_populates="event", cascade="all, delete-orphan")
    knowledge_records = relationship("KnowledgeRecord", back_populates="event", cascade="all, delete-orphan")


class Venue(Base):
    __tablename__ = "venues"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    name = Column(String, nullable=False)
    capacity = Column(Integer, default=100)
    location = Column(String, nullable=True)
    equipment = Column(JSON, default=list)  # list of strings / specs
    availability = Column(Boolean, default=True)

    event = relationship("Event", back_populates="venues")
    sessions = relationship("Session", back_populates="venue")
    resources = relationship("Resource", back_populates="assigned_venue")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    venue_id = Column(String, ForeignKey("venues.id"), nullable=True)
    speaker_id = Column(String, nullable=True)
    speaker_name = Column(String, nullable=True)
    expected_attendees = Column(Integer, default=150)
    status = Column(String, default="SCHEDULED")  # SCHEDULED, LIVE, COMPLETED, RESCHEDULED, CANCELLED

    event = relationship("Event", back_populates="sessions")
    venue = relationship("Venue", back_populates="sessions")
    volunteer_shifts = relationship("VolunteerShift", back_populates="session", cascade="all, delete-orphan")


class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)  # Core Ops, Tech & AV, Logistics, Marketing, Hospitality, Volunteer Ops
    lead_id = Column(String, nullable=True)
    lead_name = Column(String, nullable=True)

    event = relationship("Event", back_populates="teams")
    tasks = relationship("Task", back_populates="team")


class Member(Base):
    __tablename__ = "members"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="MEMBER")  # ADMIN, OPERATIONS, TECHNICAL, MARKETING, REGISTRATION, VOLUNTEER_LEAD, VOLUNTEER
    skills = Column(JSON, default=list)  # ["AV_SETUP", "VIP_HANDLING", "CROWD_CONTROL", "REGISTRATION", "STREAMING", "RAPID_LOGISTICS"]
    availability = Column(Boolean, default=True)
    workload = Column(Integer, default=0)  # active task / shift count
    phone = Column(String, nullable=True)

    volunteer_shifts = relationship("VolunteerShift", back_populates="volunteer")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String, nullable=True)
    owner_name = Column(String, nullable=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    priority = Column(String, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String, default="TODO")  # TODO, IN_PROGRESS, BLOCKED, REVIEW, COMPLETED
    blocker = Column(Text, nullable=True)
    escalation_level = Column(Integer, default=0)  # 0: Normal, 1: Dept Escalated, 2: Command Escalated, 3: Crisis
    comments = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    event = relationship("Event", back_populates="tasks")
    team = relationship("Team", back_populates="tasks")


class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    source_type = Column(String, nullable=False)  # VENUE, SESSION, RESOURCE, TASK, VOLUNTEER
    source_id = Column(String, nullable=False)
    target_type = Column(String, nullable=False)  # SESSION, TASK, VOLUNTEER_SHIFT, RESOURCE
    target_id = Column(String, nullable=False)
    dependency_type = Column(String, default="REQUIRES")  # REQUIRES, PREREQUISITE, ALLOCATED_TO, NOTIFIES, FOLLOWS
    criticality = Column(String, default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
    created_at = Column(DateTime(timezone=True), default=utcnow)


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # AV_GEAR, POWER, NETWORK, STAGE, SECURITY
    quantity = Column(Integer, default=1)
    availability = Column(Boolean, default=True)
    assigned_venue_id = Column(String, ForeignKey("venues.id"), nullable=True)

    event = relationship("Event", back_populates="resources")
    assigned_venue = relationship("Venue", back_populates="resources")


class VolunteerShift(Base):
    __tablename__ = "volunteer_shifts"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    volunteer_id = Column(String, ForeignKey("members.id"), nullable=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=True)
    role_required = Column(String, default="GENERAL")  # AV_SUPPORT, STAGE_RUNNER, CROWD_FLOW, VIP_ESCORT, BADGE_CHECK
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    assignment_status = Column(String, default="PENDING")  # PENDING, CONFIRMED, REJECTED, AUTO_PROPOSED
    allocation_score = Column(Integer, default=0)

    volunteer = relationship("Member", back_populates="volunteer_shifts")
    session = relationship("Session", back_populates="volunteer_shifts")


class Risk(Base):
    __tablename__ = "risks"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    title = Column(String, nullable=False)
    severity = Column(String, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    probability = Column(String, default="MEDIUM")  # LOW, MEDIUM, HIGH
    impact = Column(Text, nullable=False)
    mitigation = Column(Text, nullable=False)
    status = Column(String, default="OPEN")  # OPEN, MITIGATED, RESOLVED

    event = relationship("Event", back_populates="risks")


class ChangeLog(Base):
    __tablename__ = "changelogs"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    previous_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    impact_summary = Column(Text, nullable=True)
    approved = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    event = relationship("Event", back_populates="changelogs")


class NotionSyncLog(Base):
    __tablename__ = "notion_sync_logs"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    notion_page_id = Column(String, nullable=True)
    sync_status = Column(String, default="SUCCESS")  # SUCCESS, FAILED, PENDING, SIMULATED
    last_synced_at = Column(DateTime(timezone=True), default=utcnow)
    error_message = Column(Text, nullable=True)

    event = relationship("Event", back_populates="synclogs")


class KnowledgeRecord(Base):
    __tablename__ = "knowledge_records"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    title = Column(String, nullable=False)
    department = Column(String, nullable=False)
    problem = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=False)
    resolution = Column(Text, nullable=False)
    lessons_learned = Column(Text, nullable=False)
    recommended_future_action = Column(Text, nullable=False)
    tags = Column(JSON, default=list)
    source_references = Column(JSON, default=list)
    notion_page_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    event = relationship("Event", back_populates="knowledge_records")


class BriefingRecord(Base):
    __tablename__ = "briefing_records"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    briefing_type = Column(String, default="MORNING")  # MORNING, MIDDAY, EOD
    content = Column(JSON, nullable=False)  # full structured payload
    summary = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), default=utcnow)
    saved_to_notion = Column(Boolean, default=False)
