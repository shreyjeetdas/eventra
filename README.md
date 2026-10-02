# EVENTRA
### *The intelligence behind every moving part.*

> **Project:** KBC-NOTION-03 — Intelligent Team Operations & Event Command Center  
> **Competition:** Kaun Banega Codepati 2026  
> **Domain:** Productivity  
> **Mandatory Integration:** Notion (Live API + Verified High-Fidelity Transparent Mock)  
> **Benchmark Scenario:** KIIT TECHNICAL FEST 2026 (Auditorium Emergency Crisis)

---

## 1. Overview

**EVENTRA** is not a generic CRUD event dashboard. It is an intelligent event operations platform that unites **dependency-aware planning**, **deterministic graph intelligence**, **AI-powered change impact analysis**, **role-based command centers**, **multi-factor volunteer optimization**, **in-memory simulation**, and a **synchronized Notion knowledge layer**.

Built with a bold **painterly street-art / dark editorial aesthetic**, EVENTRA blends the energy of an underground design magazine with the precision of an aerospace mission control room.

---

## 2. Key Capabilities & Technical Features

- **Directed Dependency Graph Engine:** Powered by `NetworkX`, modeling physical venues, sessions, AV hardware, volunteer shifts, and notifications as a Directed Acyclic Graph (DAG) with instant cycle-deadlock detection and critical path highlighting.
- **AI Change Impact Intelligence:** When a crisis occurs (e.g. Auditorium 1 cooling failure), the system calculates the exact blast radius, detects capacity deficits (e.g., 480 attendees vs 220 seats), identifies hardware needing relocation, and formulates a 4-department mitigation plan ready for 1-click dispatch.
- **WHAT IF? Simulation Sandbox:** Safely tests hypothetical changes in memory without mutating the live production database.
- **Volunteer Allocation Engine:** Multi-factor scoring algorithm weighting skill match (40%), availability (30%), workload balancing (20%), and venue continuity (10%).
- **Mandatory Notion Integration:** Bi-directional operational documentation syncing Run of Show, tasks, change logs, AI daily briefings, and post-event incident post-mortems. Works out-of-the-box in simulated mock mode and seamlessly connects to a live Notion workspace with an API key.
- **Six Purpose-Built Role Command Centers:** Dedicated views for Admin / Event Lead, Core Operations, Technical & AV, Marketing, Registration & Hospitality, and Volunteer Leads.

---

## 3. Tech Stack

- **Frontend:** Next.js 14+ (App Router), TypeScript, Tailwind CSS, React Flow (`@xyflow/react`), Recharts, Framer Motion, Lucide icons.
- **Backend:** Python 3.13, FastAPI, SQLAlchemy ORM, Pydantic v2, NetworkX, HTTPX, Pytest.
- **Persistence:** SQLite (default zero-config local file) / PostgreSQL (Supabase compatible).
- **AI Engine:** Google Gemini / OpenAI abstraction with deterministic rule-based fallback.
- **Notion:** Official Notion API client + transparent high-fidelity mock adapter.

---

## 4. Quick Start (Run Locally)

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Clone & Set Up Backend
```bash
cd eventra

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt   # or: pip install fastapi uvicorn pydantic sqlalchemy networkx python-dotenv httpx pytest pytest-asyncio

# Seed the database with KIIT Tech Fest 2026 sample data
python backend/scripts/seed.py

# Launch FastAPI backend on port 8000
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Set Up & Launch Frontend
In a new terminal window:
```bash
cd eventra/frontend

# Install frontend dependencies
npm install

# Start Next.js development server on port 3000
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 5. Running Automated Tests
```bash
cd eventra
./venv/bin/pytest backend/tests
```
All engine tests (Graph Traversal, Volunteer Allocation, Simulation, Impact Analysis) run in under 1 second.

---

## 6. The 5-Minute Hackathon Demo

Follow the complete script in [`docs/demo-script.md`](./docs/demo-script.md):
1. Launch `/app/overview` to view the live **Operational Pulse**.
2. Inspect the **Directed Dependency Graph** at `/app/dependencies`.
3. Click **"⚡ TRIGGER VENUE CRISIS"** in the top header.
4. Review the **AI Impact Report** showing capacity clash (-260 seats) and equipment transfers.
5. Click **"APPROVE & DISPATCH DIRECTIVES"** to automatically generate tasks and sync to Notion.
6. Open **Volunteers** (`/app/volunteers`) and click **"Run AI Allocation Engine"**.
7. Open **Knowledge** (`/app/knowledge`) to view the post-event retrospective.

---

## 7. Documentation Index
- [Architecture & Specifications](./docs/architecture.md)
- [API Endpoints & Schemas](./docs/api.md)
- [Notion Integration Setup](./docs/notion-setup.md)
- [Demo Presentation Script](./docs/demo-script.md)

---

EVENTRA © 2026 — Kaun Banega Codepati (KBC-NOTION-03).
