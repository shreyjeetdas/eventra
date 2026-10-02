from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime

# ----------------- Base schemas -----------------
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# ----------------- Events -----------------
class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: Optional[str] = "ACTIVE"
    organizer_id: Optional[str] = None
    notion_page_id: Optional[str] = None

class EventCreate(EventBase):
    id: Optional[str] = None

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class EventResponse(EventBase, BaseSchema):
    id: str
    created_at: datetime
    updated_at: datetime

# ----------------- Venues -----------------
class VenueBase(BaseModel):
    name: str
    capacity: int
    location: Optional[str] = None
    equipment: Optional[List[str]] = []
    availability: Optional[bool] = True

class VenueCreate(VenueBase):
    id: Optional[str] = None
    event_id: str

class VenueUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    equipment: Optional[List[str]] = None
    availability: Optional[bool] = None

class VenueResponse(VenueBase, BaseSchema):
    id: str
    event_id: str

# ----------------- Sessions -----------------
class SessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    venue_id: Optional[str] = None
    speaker_id: Optional[str] = None
    speaker_name: Optional[str] = None
    expected_attendees: Optional[int] = 150
    status: Optional[str] = "SCHEDULED"

class SessionCreate(SessionBase):
    id: Optional[str] = None
    event_id: str

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    venue_id: Optional[str] = None
    speaker_name: Optional[str] = None
    status: Optional[str] = None
    expected_attendees: Optional[int] = None

class SessionResponse(SessionBase, BaseSchema):
    id: str
    event_id: str

# ----------------- Teams & Members -----------------
class TeamResponse(BaseSchema):
    id: str
    event_id: str
    name: str
    department: str
    lead_id: Optional[str] = None
    lead_name: Optional[str] = None

class MemberResponse(BaseSchema):
    id: str
    name: str
    email: str
    role: str
    skills: List[str] = []
    availability: bool = True
    workload: int = 0
    phone: Optional[str] = None

# ----------------- Tasks -----------------
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    team_id: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[str] = "MEDIUM"
    status: Optional[str] = "TODO"
    blocker: Optional[str] = None
    escalation_level: Optional[int] = 0

class TaskCreate(TaskBase):
    id: Optional[str] = None
    event_id: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    team_id: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    blocker: Optional[str] = None
    escalation_level: Optional[int] = None
    comments: Optional[List[Dict[str, Any]]] = None

class TaskResponse(TaskBase, BaseSchema):
    id: str
    event_id: str
    comments: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime

# ----------------- Dependencies -----------------
class DependencyBase(BaseModel):
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    dependency_type: Optional[str] = "REQUIRES"
    criticality: Optional[str] = "HIGH"

class DependencyCreate(DependencyBase):
    id: Optional[str] = None
    event_id: str

class DependencyResponse(DependencyBase, BaseSchema):
    id: str
    event_id: str
    created_at: datetime

class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # VENUE, SESSION, RESOURCE, TASK, VOLUNTEER
    status: Optional[str] = "NORMAL"
    data: Dict[str, Any] = {}

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    criticality: str = "HIGH"
    dependency_type: str = "REQUIRES"

class DependencyGraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    has_cycles: bool
    critical_paths: List[List[str]]
    total_nodes: int
    total_edges: int

# ----------------- Resources -----------------
class ResourceBase(BaseModel):
    name: str
    category: str
    quantity: int = 1
    availability: bool = True
    assigned_venue_id: Optional[str] = None

class ResourceCreate(ResourceBase):
    id: Optional[str] = None
    event_id: str

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    availability: Optional[bool] = None
    assigned_venue_id: Optional[str] = None

class ResourceResponse(ResourceBase, BaseSchema):
    id: str
    event_id: str

# ----------------- Volunteers -----------------
class VolunteerShiftBase(BaseModel):
    volunteer_id: Optional[str] = None
    session_id: Optional[str] = None
    role_required: str = "GENERAL"
    start_time: datetime
    end_time: datetime
    assignment_status: Optional[str] = "PENDING"
    allocation_score: Optional[int] = 0

class VolunteerShiftCreate(VolunteerShiftBase):
    id: Optional[str] = None
    event_id: str

class VolunteerShiftResponse(VolunteerShiftBase, BaseSchema):
    id: str
    event_id: str

class VolunteerAllocationProposal(BaseModel):
    shift_id: str
    session_title: Optional[str] = None
    role_required: str
    assigned_volunteer_id: Optional[str] = None
    assigned_volunteer_name: Optional[str] = None
    score: int
    rationale: str
    potential_conflicts: List[str] = []

# ----------------- Risks -----------------
class RiskBase(BaseModel):
    title: str
    severity: str
    probability: str
    impact: str
    mitigation: str
    status: Optional[str] = "OPEN"

class RiskCreate(RiskBase):
    id: Optional[str] = None
    event_id: str

class RiskResponse(RiskBase, BaseSchema):
    id: str
    event_id: str

# ----------------- Change Logs -----------------
class ChangeLogResponse(BaseSchema):
    id: str
    event_id: str
    entity_type: str
    entity_id: str
    previous_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    impact_summary: Optional[str] = None
    approved: bool
    created_at: datetime

# ----------------- Notion -----------------
class NotionSyncLogResponse(BaseSchema):
    id: str
    event_id: str
    entity_type: str
    entity_id: str
    notion_page_id: Optional[str] = None
    sync_status: str
    last_synced_at: datetime
    error_message: Optional[str] = None

class NotionConfig(BaseModel):
    api_key_configured: bool
    mock_mode: bool
    database_mapping: Dict[str, str]
    last_sync_timestamp: Optional[datetime] = None

# ----------------- Knowledge Base -----------------
class KnowledgeRecordBase(BaseModel):
    title: str
    department: str
    problem: str
    root_cause: str
    resolution: str
    lessons_learned: str
    recommended_future_action: str
    tags: List[str] = []
    source_references: List[str] = []

class KnowledgeRecordCreate(KnowledgeRecordBase):
    id: Optional[str] = None
    event_id: str

class KnowledgeRecordResponse(KnowledgeRecordBase, BaseSchema):
    id: str
    event_id: str
    notion_page_id: Optional[str] = None
    created_at: datetime

# ----------------- Impact Intelligence -----------------
class ProposedAction(BaseModel):
    id: str
    title: str
    department: str
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    priority: str
    deadline_offset_minutes: int
    description: str

class ImpactAnalysisRequest(BaseModel):
    event_id: str
    entity_type: str  # VENUE, SESSION, RESOURCE, VOLUNTEER
    entity_id: str
    proposed_change: Dict[str, Any]

class ImpactAnalysisResponse(BaseModel):
    change_summary: str
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    affected_sessions: List[Dict[str, Any]]
    affected_people: List[Dict[str, Any]]
    resource_conflicts: List[Dict[str, Any]]
    communication_tasks: List[str]
    ai_narrative: str
    recommended_actions: List[ProposedAction]
    approval_required: bool
    deterministic_blast_radius: int

class MitigationApprovalRequest(BaseModel):
    event_id: str
    analysis: ImpactAnalysisResponse
    approved_by: str = "Admin"
    sync_to_notion: bool = True

# ----------------- What-If Simulation -----------------
class SimulationScenarioRequest(BaseModel):
    event_id: str
    scenario_name: str
    description: str
    changes: List[Dict[str, Any]]

class SimulationResponse(BaseModel):
    scenario_name: str
    total_conflicts_detected: int
    capacity_violations: List[Dict[str, Any]]
    equipment_shortages: List[Dict[str, Any]]
    volunteer_shortages: List[Dict[str, Any]]
    timeline_clashes: List[Dict[str, Any]]
    recommended_mitigations: List[str]
    severity_score: int  # 0 to 100
    is_safe_to_promote: bool

# ----------------- Briefings -----------------
class BriefingResponse(BaseSchema):
    id: str
    event_id: str
    briefing_type: str
    content: Dict[str, Any]
    summary: str
    generated_at: datetime
    saved_to_notion: bool

# ----------------- Operational Pulse -----------------
class OperationalPulseResponse(BaseModel):
    event_id: str
    event_name: str
    event_status: str
    health_score: int  # 0 to 100
    pulse_summary: str
    active_tasks_count: int
    overdue_tasks_count: int
    blocked_tasks_count: int
    unresolved_blockers: List[str]
    volunteer_deployment_rate: int  # percentage
    resource_utilization_rate: int  # percentage
    critical_dependencies_count: int
    recent_changes_count: int
    upcoming_sessions: List[Dict[str, Any]]
    high_priority_risks: List[Dict[str, Any]]
    notion_connected: bool
    mock_notion: bool
