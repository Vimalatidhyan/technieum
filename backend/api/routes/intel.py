"""Threat intelligence API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.db.database import get_db
from backend.db.models import ThreatIntelData, DataLeak, MalwareIndicator

router = APIRouter()

@router.get("/threat-feed", summary="Latest threat data")
def threat_feed(page: int = Query(1, ge=1), per_page: int = Query(20), db: Session = Depends(get_db)):
    """Get latest threat intelligence data."""
    q = db.query(ThreatIntelData).order_by(ThreatIntelData.last_updated.desc())
    total = q.count()
    items = [{"id": t.id, "type": t.indicator_type, "value": t.indicator_value, "source": t.source, "severity": t.severity} for t in q.offset((page-1)*per_page).limit(per_page).all()]
    return {"total": total, "page": page, "per_page": per_page, "items": items}

@router.get("/data-leaks", summary="Data leaks")
def data_leaks(page: int = Query(1, ge=1), per_page: int = Query(20), scan_run_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Query data leak findings."""
    q = db.query(DataLeak)
    if scan_run_id:
        q = q.filter(DataLeak.scan_run_id == scan_run_id)
    total = q.count()
    items = q.offset((page-1)*per_page).limit(per_page).all()
    return {"total": total, "items": [{"id": d.id, "email": d.email, "breach": d.breach_name} for d in items]}

@router.get("/malware/{ioc}", summary="Malware indicator lookup")
def malware_lookup(ioc: str, db: Session = Depends(get_db)):
    """Look up a malware indicator (hash, domain, IP)."""
    indicators = db.query(MalwareIndicator).filter(MalwareIndicator.indicator_value.contains(ioc)).limit(10).all()
    if not indicators:
        return {"ioc": ioc, "found": False, "indicators": []}
    return {"ioc": ioc, "found": True, "indicators": [{"type": i.indicator_type, "family": i.malware_family, "verdict": i.verdict} for i in indicators]}

@router.get("/ip-reputation/{ip}", summary="IP reputation")
def ip_reputation(ip: str, db: Session = Depends(get_db)):
    """Check IP reputation."""
    results = db.query(ThreatIntelData).filter(ThreatIntelData.indicator_value == ip).all()
    return {"ip": ip, "reports": len(results), "data": [{"source": r.source, "severity": r.severity} for r in results]}

@router.get("/domain-reputation/{domain}", summary="Domain reputation")
def domain_reputation(domain: str, db: Session = Depends(get_db)):
    """Check domain reputation."""
    results = db.query(ThreatIntelData).filter(ThreatIntelData.indicator_value.contains(domain)).all()
    return {"domain": domain, "reports": len(results), "data": [{"source": r.source, "severity": r.severity} for r in results]}
