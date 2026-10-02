# EVENTRA API Documentation & Schema Contracts

FastAPI OpenAPI Interactive Swagger UI is hosted at `/docs` when running the backend.

Base Path: `/api`

---

## 1. Events & Operational Pulse

### `GET /api/events`
Returns all active events.

### `GET /api/events/{event_id}`
Returns details for a single event.

### `GET /api/events/{event_id}/pulse`
Returns the real-time operational pulse of the event:
- `health_score`: Dynamic 0-100 score computed from open blockers, overdue tasks, and risks.
- `active_tasks_count`: Total in-flight tasks.
- `overdue_tasks_count`: Tasks past deadline.
- `blocked_tasks_count`: Tasks marked BLOCKED.
- `unresolved_blockers`: List of blocker strings.
- `volunteer_deployment_rate`: Percentage of confirmed volunteer shifts.
- `resource_utilization_rate`: Percentage of active hardware assets deployed.
- `critical_dependencies_count`: Number of CRITICAL criticality graph edges.
- `upcoming_sessions`: Next scheduled sessions in chronological order.
- `notion_connected`: Boolean state.

### `POST /api/events/{event_id}/reset-seed`
Resets the demonstration database back to initial seed state.

---

## 2. Dependency Graph & Traversal

### `GET /api/dependencies/graph?event_id={id}`
Returns complete React Flow graph payload:
- `nodes`: List of graph nodes with types (`VENUE`, `SESSION`, `RESOURCE`, `TASK`).
- `edges`: List of directed edges with `dependency_type` and `criticality`.
- `has_cycles`: Boolean result of Tarjan's cycle test.
- `critical_paths`: Longest continuous unskippable dependency chains.

### `GET /api/dependencies/downstream/{node_id}?event_id={id}`
Returns all directly and indirectly affected downstream nodes sorted by ripple level (+1, +2, +3).

---

## 3. Impact Intelligence

### `POST /api/impact/analyze`
Payload:
```json
{
  "event_id": "evt-kiit-techfest-2026",
  "entity_type": "VENUE",
  "entity_id": "ven-aud-1",
  "proposed_change": {
    "name": "Convention Centre Hall A",
    "capacity": 220,
    "reason": "Emergency cooling failure"
  }
}
```
Response:
- `change_summary`: Formulated change event statement.
- `risk_level`: CRITICAL | HIGH | MEDIUM | LOW.
- `affected_sessions`: Array of sessions scheduled in that venue with capacity clash analysis.
- `resource_conflicts`: Physical equipment needing transfer.
- `communication_tasks`: Notification broadcasts required.
- `ai_narrative`: 3-paragraph executive operational directive.
- `recommended_actions`: Concrete tasks ready to assign with department leads and deadlines.

### `POST /api/impact/approve`
Approves and commits mitigation plan:
- Auto-generates follow-up tasks in the task database.
- Creates an approved ChangeLog record.
- Synchronizes approved updates to Notion.

---

## 4. Volunteer Allocation Engine

### `POST /api/volunteers/allocate/proposals?event_id={id}`
Computes multi-factor scoring assignments across unassigned shifts.

### `POST /api/volunteers/allocate/approve?event_id={id}`
Payload: Array of approved proposals. Commits assignments to the database.

---

## 5. Simulation Sandbox

### `POST /api/simulation/run`
Payload:
```json
{
  "event_id": "evt-kiit-techfest-2026",
  "scenario_name": "Auditorium 1 Outage",
  "description": "Simulate sudden venue closure",
  "changes": [
    { "type": "VENUE", "id": "ven-aud-1", "field": "available", "value": false }
  ]
}
```
Response:
Side-by-side diff with capacity violations, equipment shortages, and recommended mitigations in memory without touching persistent database.

---

## 6. Daily Briefings & Notion

### `POST /api/briefings/generate?event_id={id}&briefing_type={MORNING|MIDDAY|EOD}`
Generates structured daily operational briefing from actual database metrics.

### `POST /api/briefings/{briefing_id}/notion?event_id={id}`
Synchronizes briefing to Notion database.

### `POST /api/notion/sync-all?event_id={id}`
Triggers full bi-directional synchronization of events, sessions, tasks, change logs, and knowledge post-mortems.
