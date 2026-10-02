# EVENTRA — Notion Integration Setup Guide

Notion serves as EVENTRA's persistent knowledge and operational documentation layer.

---

## 1. High-Fidelity Transparent Mock Mode (Default)

EVENTRA comes pre-configured with a **zero-friction simulated adapter**:
- No external Notion API keys or internet connection required for testing or initial demo.
- Generates compliant Notion block models and database schemas.
- Simulates realistic API latency (300ms).
- Records all operations in the persistent `notion_sync_logs` database table.
- Generates authentic Notion page URLs (`https://notion.so/eventra-kiit-operations/...`).
- Transparently badges operations as `SIMULATED_MOCK`.

---

## 2. Connecting to a Live Notion Workspace

To connect EVENTRA to your real Notion workspace:

### Step 1: Create an Internal Integration in Notion
1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations).
2. Click **"+ New integration"**.
3. Name it **"EVENTRA Ops Bridge"**.
4. Select the workspace where you want the festival documentation stored.
5. Under Capabilities, ensure **Read, Update, and Insert content** are checked.
6. Click **Submit** and copy the **Internal Integration Secret** (starts with `secret_` or `ntn_`).

### Step 2: Share Target Notion Pages / Databases
1. In your Notion workspace, open or create a page called **"KIIT Technical Fest 2026 Operations"**.
2. Click the `...` menu in the top right -> **Connections** -> **Connect to** -> select **"EVENTRA Ops Bridge"**.

### Step 3: Configure Credentials in EVENTRA
You can configure credentials in two ways:

#### Option A: Via Application UI
1. In EVENTRA, navigate to **Settings** (`/app/settings`) or **Notion** (`/app/notion`).
2. Paste your Notion API secret into the **API Token Configuration** field.
3. Click **Update Notion API Key**.
4. The system status badge will immediately transition to **`LIVE_API`**.

#### Option B: Via Environment Variables (`.env`)
In `backend/.env`:
```env
NOTION_API_KEY=secret_your_live_token_here
NOTION_DATABASE_ID_EVENTS=your_notion_events_database_id
NOTION_DATABASE_ID_TASKS=your_notion_tasks_database_id
NOTION_DATABASE_ID_CHANGELOGS=your_notion_changelogs_database_id
NOTION_DATABASE_ID_KNOWLEDGE=your_notion_knowledge_database_id
NOTION_DATABASE_ID_BRIEFINGS=your_notion_briefings_database_id
```

---

## 3. Supported Synchronizations
1. **Event Overview & Run of Show:** Master schedules, venue capacities, and speaker details.
2. **Approved Mitigations & Change Logs:** Emergency room reassignments and mitigation action items.
3. **Daily Operational Briefings:** Morning readiness, midday pulse, and EOD debriefs.
4. **Post-Mortem Incident Knowledge Base:** Root-cause analyses and recommendations for 2027.
