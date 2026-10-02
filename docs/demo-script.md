# EVENTRA — 5-Minute Hackathon Demonstration Script

> **Competition:** Kaun Banega Codepati 2026 (KBC-NOTION-03)  
> **Benchmark Scenario:** "KIIT Technical Fest 2026 — Main Auditorium Emergency Crisis"

---

## The Pitch Narrative
> *"An event is running. Everything appears normal. Suddenly, the main auditorium becomes unavailable."*

---

## Step-by-Step Demonstration Walkthrough

### 00:00 — 00:45 | Step 1: Landing Page & Command Room Entry
1. Open `http://localhost:3000`.
2. Highlight the distinctive painterly street-art design direction: dark textured background (`#101010`), warm cream display typography, intense vermilion and orange accents, and bespoke auditorium artwork.
3. Click **"Enter Command Center"**.
4. Land on **The Control Room** (`/app/overview`).
5. Point out the live **Operational Pulse**:
   - System Health score (e.g. 90/100).
   - Real-time countdown to KIIT Technical Fest 2026.
   - 30 tasks, 8 sessions, 6 departments, and verified Notion sync status.

---

### 00:45 — 01:30 | Step 2: Inspection of the Dependency Graph
1. Navigate to **Dependencies** (`/app/dependencies`).
2. Show the interactive directed graph (React Flow):
   - Notice tiered visual layers: Venues (top) → Sessions → Resources → Tasks.
   - Click on **"Auditorium 1 - Campus 6"** to inspect its downstream blast radius:
     - 4 downstream sessions, the 4K LED wall, wireless mic kits, and attendee broadcasts are instantly highlighted.
   - Point out the **"DAG VERIFIED (NO CYCLES)"** badge, demonstrating deterministic topological safety.

---

### 01:30 — 02:45 | Step 3: Trigger the Signature Crisis (Impact Intelligence)
1. Click the prominent header button: **"⚡ TRIGGER VENUE CRISIS"** (or click Reassign on the Timeline).
2. The **Impact Intelligence** modal opens with a live blast radius calculation:
   - **Trigger:** Auditorium 1 closed 2 hours prior to Opening Keynote due to emergency cooling failure.
   - **Deterministic Blast Radius:** 8 downstream records affected.
   - **Capacity Conflict Detected:** 480 registered attendees for the Keynote vs 220 seats in Convention Centre Hall A (-260 seat deficit!).
   - **Equipment Conflict Detected:** 4K LED wall and Shure Axient microphones need physical transfer.
   - **AI Operational Narrative:** A crisp 3-paragraph executive briefing explaining the disruption, VIP speaker impacts, and wayfinding requirements.
   - **Recommended Action Directives:** 4 formulated tasks with department leads, priorities, and deadlines:
     1. Tech & AV: Reroute audio lines and stage monitors.
     2. Marketing: Broadcast SMS & App push notifications to 2,400 students.
     3. Volunteer Ops: Station 6 crowd marshals for wayfinding chokepoints.
     4. Hospitality: Brief Dr. Elena Vance and escort team.

---

### 02:45 — 03:30 | Step 4: Run a "What-If?" Simulation & Approve Mitigation
1. Navigate to **Simulator** (`/app/simulator`).
2. Click **"Scenario A: Auditorium 1 Emergency Shutdown"**.
3. Point out that the simulator operates on an in-memory clone, proving that live database state is never mutated accidentally.
4. Return to the Impact modal and click **"APPROVE & DISPATCH DIRECTIVES"** with the Notion checkbox enabled.
5. In under 200ms:
   - 4 follow-up mitigation tasks are created in the database.
   - ChangeLog is updated.
   - The mitigation record is synchronized to the **Notion Knowledge Layer** with a live confirmation link!

---

### 03:30 — 04:15 | Step 5: Verify Roster Balancing & Volunteer Optimizer
1. Navigate to **Volunteers** (`/app/volunteers`).
2. Show the 20-person volunteer pool.
3. Click **"Run AI Allocation Engine"**:
   - The engine scores candidates based on skill match (40%), availability (30%), and workload balancing (20%).
   - Click **"Approve & Commit All Shifts"** to roster the volunteers into confirmed status.

---

### 04:15 — 05:00 | Step 6: Post-Event Retrospective & Closing
1. Navigate to **Knowledge** (`/app/knowledge`).
2. Show the post-event incident retrospective:
   - Problem, Root Cause, Resolution, Lessons Learned, and Future Recommendations for Tech Fest 2027.
   - Click **"Export to Notion Wiki"**.
3. Conclude with the keynote statement:

> *"EVENTRA doesn't just tell teams what changed. It shows what that change means, who needs to act, and what the organization should remember."*
