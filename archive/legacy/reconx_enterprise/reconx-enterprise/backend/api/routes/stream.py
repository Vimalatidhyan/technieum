"""Server-Sent Events streaming routes."""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.db.database import Database
from backend.db.models import ScanProgress
import asyncio
import json
from datetime import datetime, timezone

router = APIRouter()


async def _progress_generator(scan_id: int):
    """Generate SSE progress events for a scan."""
    db_conn = Database()
    db_conn.connect()
    try:
        iteration = 0
        while iteration < 300:  # ~10 min max at 2s intervals
            progress = db_conn.session.query(ScanProgress).filter(
                ScanProgress.scan_run_id == scan_id
            ).first()

            if not progress:
                yield f"data: {json.dumps({'event': 'error', 'message': 'Scan not found'})}\n\n"
                break

            data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "progress",
                "scan_id": scan_id,
                "phase": progress.current_phase,
                "percentage": progress.progress_percentage,
                "status": progress.status,
            }
            yield f"data: {json.dumps(data)}\n\n"

            if iteration % 5 == 0:
                yield f"data: {json.dumps({'event': 'heartbeat', 'timestamp': datetime.now(timezone.utc).isoformat()})}\n\n"

            if progress.status in ("completed", "failed", "stopped"):
                yield f"data: {json.dumps({'event': 'completed', 'status': progress.status})}\n\n"
                break

            await asyncio.sleep(2)
            iteration += 1
    except Exception as e:
        yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"
    finally:
        db_conn.close()


@router.get("/logs/{scan_id}", summary="Stream scan logs")
async def stream_logs(scan_id: int):
    """Stream scan logs in real-time via SSE."""
    return StreamingResponse(_progress_generator(scan_id), media_type="text/event-stream")


@router.get("/progress/{scan_id}", summary="Stream progress")
async def stream_progress(scan_id: int):
    """Stream progress updates via SSE."""
    return StreamingResponse(_progress_generator(scan_id), media_type="text/event-stream")


@router.get("/scan/{scan_id}", summary="Stream scan updates")
async def stream_scan(scan_id: int):
    """Stream comprehensive scan updates via SSE."""
    async def gen():
        db_conn = Database()
        db_conn.connect()
        try:
            for i in range(100):
                progress = db_conn.session.query(ScanProgress).filter(
                    ScanProgress.scan_run_id == scan_id
                ).first()
                if not progress:
                    yield f"data: {json.dumps({'event': 'error', 'message': 'Scan not found'})}\n\n"
                    break
                yield f"data: {json.dumps({'event': 'progress', 'progress': progress.progress_percentage, 'phase': progress.current_phase})}\n\n"
                if progress.progress_percentage >= 100:
                    yield f"data: {json.dumps({'event': 'completed'})}\n\n"
                    break
                await asyncio.sleep(1)
        finally:
            db_conn.close()

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.get("/alerts", summary="Stream alerts")
async def stream_alerts():
    """Stream all security alerts via SSE."""
    async def gen():
        for _ in range(2):
            yield f"data: {json.dumps({'timestamp': datetime.now(timezone.utc).isoformat(), 'event': 'heartbeat'})}\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(gen(), media_type="text/event-stream")
