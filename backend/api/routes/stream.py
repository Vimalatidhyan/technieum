"""Server-Sent Events streaming routes."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import ScanProgress
import asyncio, json
from datetime import datetime

router = APIRouter()

async def _scan_log_generator(scan_id: int, db: Session):
    progress = db.query(ScanProgress).filter(ScanProgress.scan_run_id == scan_id).first()
    for _ in range(3):
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "progress_update",
            "scan_id": scan_id,
            "phase": progress.current_phase if progress else 0,
            "percentage": progress.progress_percentage if progress else 0,
        }
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(2)

@router.get("/logs/{scan_id}", summary="Stream scan logs")
async def stream_logs(scan_id: int, db: Session = Depends(get_db)):
    """Stream scan logs in real-time via SSE."""
    return StreamingResponse(_scan_log_generator(scan_id, db), media_type="text/event-stream")

@router.get("/progress/{scan_id}", summary="Stream progress")
async def stream_progress(scan_id: int, db: Session = Depends(get_db)):
    """Stream progress updates via SSE."""
    return StreamingResponse(_scan_log_generator(scan_id, db), media_type="text/event-stream")

@router.get("/alerts", summary="Stream alerts")
async def stream_alerts():
    """Stream all security alerts via SSE."""
    async def gen():
        for i in range(2):
            yield f"data: {json.dumps({'timestamp': datetime.utcnow().isoformat(), 'event': 'heartbeat'})}\n\n"
            await asyncio.sleep(5)
    return StreamingResponse(gen(), media_type="text/event-stream")
