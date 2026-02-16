"""Threat intelligence API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from backend.db.database import get_db
from backend.db.models import ThreatIntelData, DataLeak, MalwareIndicator

router = APIRouter()


class ThreatIndicator(BaseModel):
    id: int
    type: str
    value: str
    source: str
    severity: Optional[str] = None


class ThreatFeedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[ThreatIndicator]


class DataLeakItem(BaseModel):
    id: int
    email: str
    breach: str


class DataLeaksResponse(BaseModel):
    total: int
    items: List[DataLeakItem]


class MalwareIndicatorItem(BaseModel):
    type: str
    family: Optional[str] = None
    verdict: Optional[str] = None


class MalwareLookupResponse(BaseModel):
    ioc: str
    found: bool
    indicators: List[MalwareIndicatorItem]


class ReputationItem(BaseModel):
    source: str
    severity: Optional[str] = None


class IPReputationResponse(BaseModel):
    ip: str
    reports: int
    data: List[ReputationItem]


class DomainReputationResponse(BaseModel):
    domain: str
    reports: int
    data: List[ReputationItem]


@router.get("/threat-feed", response_model=ThreatFeedResponse, summary="Latest threat data")
def threat_feed(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get latest threat intelligence data."""
    q = db.query(ThreatIntelData).order_by(ThreatIntelData.last_detected.desc())
    total = q.count()
    items = [
        ThreatIndicator(
            id=t.id,
            type=t.intel_type,
            value=t.target,
            source=t.source,
            severity=t.severity,
        )
        for t in q.offset((page - 1) * per_page).limit(per_page).all()
    ]
    return ThreatFeedResponse(total=total, page=page, per_page=per_page, items=items)


@router.get("/data-leaks", response_model=DataLeaksResponse, summary="Data leaks")
def data_leaks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Query data leak findings with PII redaction."""
    q = db.query(DataLeak)
    total = q.count()
    items_raw = q.offset((page - 1) * per_page).limit(per_page).all()

    redacted = []
    for d in items_raw:
        email = d.email or ""
        parts = email.split("@") if "@" in email else [email, ""]
        username, domain = parts[0], parts[1] if len(parts) > 1 else ""
        redacted_email = f"{username[:3]}***@{domain}" if len(username) > 3 else f"***@{domain}"
        redacted.append(DataLeakItem(id=d.id, email=redacted_email, breach=d.breach_name))

    return DataLeaksResponse(total=total, items=redacted)


@router.get("/malware/{ioc}", response_model=MalwareLookupResponse, summary="Malware indicator lookup")
def malware_lookup(ioc: str, db: Session = Depends(get_db)):
    """Look up a malware indicator (hash, domain, IP)."""
    indicators = (
        db.query(MalwareIndicator)
        .filter(MalwareIndicator.indicator_value.contains(ioc))
        .limit(10)
        .all()
    )
    if not indicators:
        return MalwareLookupResponse(ioc=ioc, found=False, indicators=[])
    items = [
        MalwareIndicatorItem(
            type=i.indicator_type,
            family=i.malware_family,
            verdict=i.verdict,
        )
        for i in indicators
    ]
    return MalwareLookupResponse(ioc=ioc, found=True, indicators=items)


@router.get("/ip-reputation/{ip}", response_model=IPReputationResponse, summary="IP reputation")
def ip_reputation(ip: str, db: Session = Depends(get_db)):
    """Check IP reputation against threat intel database."""
    results = db.query(ThreatIntelData).filter(ThreatIntelData.target == ip).all()
    data = [ReputationItem(source=r.source, severity=r.severity) for r in results]
    return IPReputationResponse(ip=ip, reports=len(results), data=data)


@router.get("/domain-reputation/{domain}", response_model=DomainReputationResponse, summary="Domain reputation")
def domain_reputation(domain: str, db: Session = Depends(get_db)):
    """Check domain reputation against threat intel database."""
    results = db.query(ThreatIntelData).filter(ThreatIntelData.target.contains(domain)).all()
    data = [ReputationItem(source=r.source, severity=r.severity) for r in results]
    return DomainReputationResponse(domain=domain, reports=len(results), data=data)
