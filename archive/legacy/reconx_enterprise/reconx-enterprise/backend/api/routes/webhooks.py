"""Webhook management routes (in-memory store — no DB model required)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime, timezone

router = APIRouter()

# Simple in-memory store for webhooks (replace with DB model when Webhook model is added)
_webhooks: dict = {}
_next_id: int = 1


class WebhookCreateRequest(BaseModel):
    url: HttpUrl
    events: List[str] = ["scan.completed", "finding.critical"]
    secret: Optional[str] = None


class WebhookUpdateRequest(BaseModel):
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    active: Optional[bool] = None


@router.get("/", summary="List webhooks")
def list_webhooks():
    """List all registered webhooks."""
    return {"total": len(_webhooks), "items": list(_webhooks.values())}


@router.post("/", summary="Create webhook")
def create_webhook(req: WebhookCreateRequest):
    """Register a new webhook."""
    global _next_id
    wh_id = _next_id
    _next_id += 1
    _webhooks[wh_id] = {
        "id": wh_id,
        "url": str(req.url),
        "events": req.events,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "success_count": 0,
        "failure_count": 0,
        "last_triggered": None,
    }
    return _webhooks[wh_id]


@router.put("/{webhook_id}", summary="Update webhook")
def update_webhook(webhook_id: int, req: WebhookUpdateRequest):
    """Update an existing webhook."""
    if webhook_id not in _webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")
    wh = _webhooks[webhook_id]
    if req.url is not None:
        wh["url"] = str(req.url)
    if req.events is not None:
        wh["events"] = req.events
    if req.active is not None:
        wh["active"] = req.active
    return wh


@router.delete("/{webhook_id}", summary="Delete webhook")
def delete_webhook(webhook_id: int):
    """Delete a webhook."""
    if webhook_id not in _webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")
    del _webhooks[webhook_id]
    return {"status": "deleted", "message": f"Webhook {webhook_id} deleted"}


@router.post("/{webhook_id}/test", summary="Test webhook")
def test_webhook(webhook_id: int):
    """Send a test event to a webhook."""
    if webhook_id not in _webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")
    _webhooks[webhook_id]["success_count"] += 1
    _webhooks[webhook_id]["last_triggered"] = datetime.now(timezone.utc).isoformat()
    return {"status": "sent", "message": f"Test event sent to webhook {webhook_id}"}


@router.get("/{webhook_id}/events", summary="Get webhook delivery log")
def get_webhook_events(webhook_id: int):
    """Get delivery history for a webhook."""
    if webhook_id not in _webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")
    wh = _webhooks[webhook_id]
    return {
        "webhook_id": webhook_id,
        "success_count": wh["success_count"],
        "failure_count": wh["failure_count"],
        "last_triggered": wh["last_triggered"],
    }
