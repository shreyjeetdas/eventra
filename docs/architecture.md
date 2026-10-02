# EVENTRA — System Architecture & Technical Specifications

> **Project:** KBC-NOTION-03 — Intelligent Team Operations & Event Command Center  
> **Event Benchmark:** KIIT TECHNICAL FEST 2026  
> **Tagline:** *The intelligence behind every moving part.*

---

## 1. System Philosophy

EVENTRA rejects the notion of a generic CRUD event dashboard. Real high-stakes events (conferences, technical symposiums, hackathons, arena festivals) fail not from lack of effort, but from **invisible, cascading dependencies**. 

EVENTRA models operational reality as a **Directed Acyclic Graph (DAG)** where physical venues, scheduled sessions, AV hardware, volunteer rosters, and digital communications form interconnected nodes. When an operational disruption strikes (e.g. auditorium thermal trip, flight delay, or equipment failure), EVENTRA's deterministic graph engine immediately isolates the full blast radius, while AI synthesizes an actionable, multi-department mitigation plan.

---

## 2. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT LAYER                                      |
|  Next.js 14+ (App Router) • React Flow (DAG Canvas) • Recharts • Framer Motion    |
|  Painterly Dark Editorial UI • Warm Cream (#F4F0E9) • Vermilion (#F04432) Accents  |
+-----------------------------------------------------------------------------------+
                                         │  HTTP / REST API (Reverse Proxy)
                                         ▼
+-----------------------------------------------------------------------------------+
|                              FASTAPI BACKEND CORE                                 |
|                                                                                   |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  |    Graph Engine    |  |  Impact Intelligence |  |    Volunteer Optimizer    |  |
|  | (NetworkX Traversal|  | (Deterministic Blast |  |  (Multi-factor Scoring:   |  |
|  |   & Cycle Guard)   |  |  + LLM Directive)    |  |  Skill, Load, Time slots) |  |
|  +--------------------+  +----------------------+  +---------------------------+  |
|                                                                                   |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  |  Simulation Engine |  | AI Daily Briefings   |  |  Notion Sync Adapter      |  |
|  |  (In-Memory Clone  |  |  (Morning, Midday,   |  |  (Live API + High-Fi      |  |
|  |   Safe Sandbox)    |  |   EOD Directives)    |  |   Transparent Mock)       |  |
|  +--------------------+  +----------------------+  +---------------------------+  |
+-----------------------------------------------------------------------------------+
                                         │  SQLAlchemy ORM
                                         ▼
+-----------------------------------------------------------------------------------+
|                                PERSISTENCE LAYER                                  |
|         SQLite (Local Zero-Config) / PostgreSQL (Supabase Compatible)            |
|     14 Relational Models • Foreign Keys • Cascading Deletes • JSON Metadata       |
+-----------------------------------------------------------------------------------+
                                         │  Bi-directional Sync
                                         ▼
+-----------------------------------------------------------------------------------+
|                             NOTION KNOWLEDGE LAYER                                |
|   Master Event Wiki • Run of Show • Approved Mitigations • Post-Mortem Wiki       |
+-----------------------------------------------------------------------------------+
```

---

## 3. Core Engine Deep Dive

### 3.1 Directed Dependency Graph Engine (`app/engines/graph_engine.py`)
- Constructed with `NetworkX` directed graph data structures (`DiGraph`).
- Dynamically ingests both explicit foreign key dependencies and cross-entity linkages:
  - `VENUE -> SESSION` (`HOSTS`)
  - `RESOURCE -> SESSION` (`REQUIRES`)
  - `TASK -> SESSION` (`PREREQUISITE`)
  - `SESSION -> SESSION` (`FOLLOWS` sequential ordering)
- **Topological Sorting & Longest Path:** Identifies the unskippable critical path that gates event launch.
- **Cycle Detection:** Tarjan's cycle algorithm catches circular task dependencies before they deadlock teams.
- **Downstream Blast Radius:** BFS/DFS traversal calculates tiered ripple levels (`+1, +2, +3`) whenever any upstream entity is modified.

### 3.2 AI Change Impact Engine (`app/engines/impact_engine.py`)
- Employs a strict separation between:
  1. **Detected Facts:** Hard capacity numbers, conflicting session times, and hardware assignments.
  2. **Predicted Impacts:** Projected attendee crowding, volunteer deficits, and audio failovers.
  3. **Formulated Action Directives:** Concrete follow-up tasks with assigned department leads and relative deadlines.
  4. **Approved Changes:** Human-in-the-loop approval barrier that commits tasks to live state and triggers Notion sync.

### 3.3 Volunteer Allocation Engine (`app/engines/volunteer_engine.py`)
- Implements a multi-factor scoring optimization algorithm:
  - Skill affinity match: **40%**
  - Availability & schedule compatibility: **30%**
  - Workload balancing (prevents burnout, penalizes overloaded staff): **20%**
  - Venue continuity & proximity bonus: **10%**
- Returns structured explanations for each recommended assignment with full override capabilities.

### 3.4 In-Memory "What If?" Simulator (`app/engines/simulation_engine.py`)
- Deep-clones the operational database snapshot in memory.
- Evaluates hypothetical stress scenarios (e.g. auditorium closures, volunteer dropouts, speaker flight delays).
- Generates a side-by-side diff showing capacity violations and equipment shortages without mutating persistent storage.

---

## 4. Visual Design Identity

- **Palette:**
  - Backgrounds: Dark charcoal `#101010` and deep surface `#191919`.
  - Foreground: Warm cream `#F4F0E9` and muted stone `#A7A19B`.
  - Accents: Intense Vermilion `#F04432`, Vivid Orange `#FF7A36`, Deep Burgundy `#591E27`, Muted Olive `#77734F`.
- **Typography:**
  - `Space Grotesk`: Bold, angular display typography for editorial impact.
  - `Inter`: Crisp, readable typography for dense data grids.
  - `IBM Plex Mono`: Technical timestamps, node identifiers, and status codes.
- **Atmosphere:**
  - Fine grain texture overlays, high-contrast framing, asymmetric editorial compositions, and custom painterly street-art assets.
