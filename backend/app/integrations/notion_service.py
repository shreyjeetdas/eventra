import os
import httpx
import uuid
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session as DBSession
from app.core.config import settings
from app.models.models import NotionSyncLog

class NotionService:
    def __init__(self):
        self.api_key = settings.NOTION_API_KEY
        self.version = "2022-06-28"
        self.base_url = "https://api.notion.com/v1"
        self.database_mapping = {
            "events": settings.NOTION_DATABASE_ID_EVENTS or "notion-db-events-kiit",
            "sessions": "notion-db-sessions-kiit",
            "tasks": settings.NOTION_DATABASE_ID_TASKS or "notion-db-tasks-kiit",
            "changelogs": settings.NOTION_DATABASE_ID_CHANGELOGS or "notion-db-changelogs-kiit",
            "knowledge": settings.NOTION_DATABASE_ID_KNOWLEDGE or "notion-db-knowledge-kiit",
            "briefings": settings.NOTION_DATABASE_ID_BRIEFINGS or "notion-db-briefings-kiit"
        }

    def is_live_configured(self) -> bool:
        return bool(self.api_key and self.api_key.startswith("secret_") or self.api_key.startswith("ntn_"))

    def get_status(self) -> Dict[str, Any]:
        return {
            "configured": self.is_live_configured(),
            "mode": "LIVE_API" if self.is_live_configured() else "SIMULATED_MOCK",
            "database_mapping": self.database_mapping,
            "version": self.version,
            "description": "Live Notion workspace sync" if self.is_live_configured() else "High-fidelity simulated Notion sync engine active. Add NOTION_API_KEY to sync to live workspace."
        }

    async def sync_record(
        self,
        db: DBSession,
        event_id: str,
        entity_type: str,
        entity_id: str,
        title: str,
        properties: Dict[str, Any],
        content_markdown: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronizes an operational entity to Notion (either live or high-fidelity simulated)."""
        if self.is_live_configured():
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Notion-Version": self.version,
                    "Content-Type": "application/json"
                }
                # Construct Notion page payload
                target_db_id = self.database_mapping.get(entity_type.lower(), self.database_mapping["tasks"])
                payload = {
                    "parent": {"database_id": target_db_id},
                    "properties": {
                        "Name": {
                            "title": [{"text": {"content": title[:100]}}]
                        },
                        "Type": {
                            "select": {"name": entity_type}
                        }
                    }
                }
                if content_markdown:
                    payload["children"] = [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": content_markdown[:2000]}}]
                            }
                        }
                    ]

                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(f"{self.base_url}/pages", json=payload, headers=headers)
                    if resp.status_code in [200, 201]:
                        page_data = resp.json()
                        page_id = page_data.get("id", f"notion-live-{uuid.uuid4().hex[:8]}")
                        page_url = page_data.get("url", f"https://notion.so/{page_id.replace('-', '')}")
                        
                        log = NotionSyncLog(
                            id=f"sync-{uuid.uuid4().hex[:10]}",
                            event_id=event_id,
                            entity_type=entity_type,
                            entity_id=entity_id,
                            notion_page_id=page_id,
                            sync_status="SUCCESS",
                            last_synced_at=datetime.datetime.now(datetime.timezone.utc),
                            error_message=None
                        )
                        db.add(log)
                        db.commit()
                        return {"status": "SUCCESS", "mode": "LIVE_API", "notion_page_id": page_id, "url": page_url}
                    else:
                        err_msg = f"Notion API error HTTP {resp.status_code}: {resp.text}"
                        log = NotionSyncLog(
                            id=f"sync-{uuid.uuid4().hex[:10]}",
                            event_id=event_id,
                            entity_type=entity_type,
                            entity_id=entity_id,
                            notion_page_id=None,
                            sync_status="FAILED",
                            last_synced_at=datetime.datetime.now(datetime.timezone.utc),
                            error_message=err_msg
                        )
                        db.add(log)
                        db.commit()
                        return {"status": "FAILED", "mode": "LIVE_API", "error": err_msg}
            except Exception as e:
                err_msg = f"Exception during Notion sync: {str(e)}"
                log = NotionSyncLog(
                    id=f"sync-{uuid.uuid4().hex[:10]}",
                    event_id=event_id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    notion_page_id=None,
                    sync_status="FAILED",
                    last_synced_at=datetime.datetime.now(datetime.timezone.utc),
                    error_message=err_msg
                )
                db.add(log)
                db.commit()
                return {"status": "FAILED", "mode": "LIVE_API", "error": err_msg}

        # ----------------- Transparent Simulated Mock Adapter -----------------
        simulated_page_id = f"mock-ntn-{uuid.uuid4().hex[:12]}"
        simulated_url = f"https://notion.so/eventra-kiit-operations/{simulated_page_id}"
        
        log = NotionSyncLog(
            id=f"sync-{uuid.uuid4().hex[:10]}",
            event_id=event_id,
            entity_type=entity_type,
            entity_id=entity_id,
            notion_page_id=simulated_page_id,
            sync_status="SIMULATED",
            last_synced_at=datetime.datetime.now(datetime.timezone.utc),
            error_message=None
        )
        db.add(log)
        db.commit()

        return {
            "status": "SIMULATED",
            "mode": "SIMULATED_MOCK",
            "notion_page_id": simulated_page_id,
            "url": simulated_url,
            "synced_title": title,
            "properties": properties,
            "synced_at": log.last_synced_at.isoformat()
        }

    def update_config(self, api_key: str, database_mapping: Optional[Dict[str, str]] = None):
        """Allows hot-updating Notion API token from UI settings."""
        self.api_key = api_key
        if database_mapping:
            self.database_mapping.update(database_mapping)

notion_service = NotionService()
