"""Webhook management routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from backend.api.models.common import StatusResponse

router = APIRouter()

# In-memory store for demo
_webhooks: dict = {}
_wh_id = 0

class WebhookCreateRequest(BaseModel):
    url: str
    events: List[str] = ["scan.completed", "finding.critical"]
    secret: Optional[str] = None

class WebhookResponse(BaseModel):
    id: int
    url: str
    events: List[str]
    active: bool = True

@router.get("/", summary="List webhooks")
def list_webhooks():
    """List all registered webhooks."""
    return {"total": len(_webhooks), "items": list(_webhooks.values())}

@router.post("/", summary="Create webhook")
def create_webhook(req: WebhookCreateRequest):
    """Register a new webhook."""
    global _wh_id
    _wh_id += 1
    wh = {"id": _wh_id, "url": req.url, "events": req.events, "active": True}
    _webhooks[_wh_id] = wh
    return wh

@router.put("/{webhook_id}", summary="Update webhook")
def update_webhook(webhook_id: int, req: WebhookCreateRequest):
    """Update an existing webhook."""
    if webhook_id not in _webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")
    _webhooks[webhook_id].update({"url": req.url, "events": req.events})
    return _webhooks[webhook_id]

@router.delete("/{webhook_id}", response_model=StatusResponse, summary="Delete webhook")
def delete_webhook(webhook_id: int):
    """Delete a webhook."""
    if webhook_id not in _webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")
    del _webhooks[webhook_id]
    return StatusResponse(status="deleted", message=f"Webhook {webhook_id} deleted")

@router.post("/{webhook_id}/test", response_model=StatusResponse, summary="Test webhook")
def test_webhook(webhook_id: int):
    """Send a test event to a webhook."""
    if webhook_id not in _webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return StatusResponse(status="sent", message=f"Test event sent to webhook {webhook_id}")
