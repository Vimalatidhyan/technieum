"""Report generation API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from backend.db.database import get_db
from backend.db.models import ScanRun, ComplianceReport
from backend.api.models.common import StatusResponse

router = APIRouter()

@router.get("/", summary="List reports")
def list_reports(scan_run_id: Optional[int] = None, db: Session = Depends(get_db)):
    """List available compliance reports."""
    q = db.query(ComplianceReport)
    if scan_run_id:
        q = q.filter(ComplianceReport.scan_run_id == scan_run_id)
    reports = q.all()
    return {"total": len(reports), "items": [{"id": r.id, "type": r.report_type, "scan_run_id": r.scan_run_id} for r in reports]}

@router.post("/", response_model=StatusResponse, summary="Generate report")
def generate_report(scan_run_id: int, report_type: str = "technical", db: Session = Depends(get_db)):
    """Generate a new compliance report."""
    scan = db.query(ScanRun).filter(ScanRun.id == scan_run_id).first()
    if not scan:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Scan not found")
    report = ComplianceReport(scan_run_id=scan_run_id, report_type=report_type, generated_at=datetime.utcnow())
    db.add(report)
    db.commit()
    return StatusResponse(status="generated", message=f"Report created for scan {scan_run_id}")

@router.get("/templates", summary="List report templates")
def list_templates():
    """List available report templates."""
    return {"templates": ["executive", "technical", "compliance", "risk_summary", "change_summary", "trend", "custom"]}
