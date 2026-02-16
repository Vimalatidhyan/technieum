"""Script to write all 24 database models to models.py."""

import os

MODELS_PATH = os.path.join(os.path.dirname(__file__), "backend", "db", "models.py")

CONTENT = '''\
"""SQLAlchemy ORM models for ReconX Enterprise v2.0.

Complete database schema with 24 models covering:
- Scanning (ScanRun, ScanProgress)
- Asset Discovery (Subdomain, PortScan, DNSRecord, HTTPHeader)
- Technology Detection (Technology, DomainTechnology, ServiceSignature)
- Vulnerability Management (Vulnerability, VulnerabilityMetadata)
- Threat Intelligence (ThreatIntelData, DataLeak, ActiveExploit, MalwareIndicator)
- Compliance (ComplianceReport, ComplianceCheck, ComplianceEvidence)
- Location & Vendor (ISPLocation, VendorMetadata)
- Change Detection (BaselineSnapshot)
- Caching & Performance (CacheEntry)
- Auth & Audit (APIToken, AuditLog)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Index,
    ForeignKey,
    Boolean,
    Float,
    UniqueConstraint,
    Text,
)
from sqlalchemy.orm import relationship

from backend.db.base import Base


# =============================================================================
# Model 1: ScanRun
# =============================================================================


class ScanRun(Base):
    """Represents a single domain scanning operation."""

    __tablename__ = "scan_runs"

    id: int = Column(Integer, primary_key=True)
    domain: str = Column(String(255), nullable=False, index=True)
    scan_type: str = Column(String(50), default="full")
    status: str = Column(String(50), default="pending")
    created_at: datetime = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at: Optional[datetime] = Column(DateTime, nullable=True)
    risk_score: Optional[int] = Column(Integer, nullable=True)
    phase: int = Column(Integer, default=0)

    subdomains = relationship("Subdomain", back_populates="scan_run", lazy="select")
    vulnerabilities = relationship("Vulnerability", back_populates="scan_run", lazy="select")
    dns_records = relationship("DNSRecord", back_populates="scan_run", lazy="select")
    compliance_reports = relationship("ComplianceReport", back_populates="scan_run", lazy="select")

    __table_args__ = (Index("ix_scan_runs_domain_created", "domain", "created_at"),)

    def __repr__(self) -> str:
        return f"<ScanRun(id={self.id}, domain={self.domain}, status={self.status})>"


# =============================================================================
# Model 2: Subdomain
# =============================================================================


class Subdomain(Base):
    """Discovered subdomain under a domain."""

    __tablename__ = "subdomains"

    id: int = Column(Integer, primary_key=True)
    scan_run_id: int = Column(Integer, ForeignKey("scan_runs.id"), nullable=False, index=True)
    subdomain: str = Column(String(255), nullable=False)
    is_alive: bool = Column(Boolean, default=False)
    discovered_method: Optional[str] = Column(String(50))
    first_seen: datetime = Column(DateTime, default=datetime.utcnow)
    last_seen: Optional[datetime] = Column(DateTime, nullable=True)
    priority: int = Column(Integer, default=0)

    scan_run = relationship("ScanRun", back_populates="subdomains", lazy="select")
    port_scans = relationship("PortScan", back_populates="subdomain", lazy="select")
    vulnerabilities = relationship("Vulnerability", back_populates="subdomain", lazy="select")
    http_headers = relationship("HTTPHeader", back_populates="subdomain", lazy="select")

    __table_args__ = (Index("ix_subdomains_scanrun_subdomain", "scan_run_id", "subdomain"),)

    def __repr__(self) -> str:
        return f"<Subdomain(id={self.id}, subdomain={self.subdomain}, is_alive={self.is_alive})>"


# =============================================================================
# Model 3: PortScan
# =============================================================================


class PortScan(Base):
    """Port scan result."""

    __tablename__ = "port_scans"

    id: int = Column(Integer, primary_key=True)
    subdomain_id: int = Column(Integer, ForeignKey("subdomains.id"), nullable=False, index=True)
    port: int = Column(Integer, nullable=False)
    protocol: str = Column(String(10), default="tcp")
    state: str = Column(String(50), default="closed")
    service: Optional[str] = Column(String(100), nullable=True)
    version: Optional[str] = Column(String(100), nullable=True)
    scanned_at: datetime = Column(DateTime, default=datetime.utcnow)

    subdomain = relationship("Subdomain", back_populates="port_scans", lazy="select")
    vulnerabilities = relationship("Vulnerability", back_populates="port_scan", lazy="select")

    __table_args__ = (Index("ix_port_scans_subdomain_port", "subdomain_id", "port"),)

    def __repr__(self) -> str:
        return f"<PortScan(port={self.port}, service={self.service}, state={self.state})>"


# =============================================================================
# Model 4: Vulnerability
# =============================================================================


class Vulnerability(Base):
    """Security finding from scanning."""

    __tablename__ = "vulnerabilities"

    id: int = Column(Integer, primary_key=True)
    scan_run_id: int = Column(Integer, ForeignKey("scan_runs.id"), nullable=False, index=True)
    subdomain_id: Optional[int] = Column(Integer, ForeignKey("subdomains.id"), nullable=True, index=True)
    port_scan_id: Optional[int] = Column(Integer, ForeignKey("port_scans.id"), nullable=True)
    vuln_type: str = Column(String(100), nullable=False)
    severity: Optional[int] = Column(Integer, nullable=True)
    title: str = Column(String(255), nullable=False)
    description: Optional[str] = Column(String(2000), nullable=True)
    remediation: Optional[str] = Column(String(2000), nullable=True)
    discovered_at: datetime = Column(DateTime, default=datetime.utcnow)
    cve_ids: Optional[str] = Column(String(1000), nullable=True)
    risk_score: Optional[int] = Column(Integer, nullable=True)

    scan_run = relationship("ScanRun", back_populates="vulnerabilities", lazy="select")
    subdomain = relationship("Subdomain", back_populates="vulnerabilities", lazy="select")
    port_scan = relationship("PortScan", back_populates="vulnerabilities", lazy="select")
    metadata = relationship("VulnerabilityMetadata", back_populates="vulnerability", uselist=False, lazy="select")
    threat_intel = relationship("ThreatIntelData", back_populates="vulnerability", lazy="select")

    def __repr__(self) -> str:
        return f"<Vulnerability(id={self.id}, type={self.vuln_type}, severity={self.severity})>"


# =============================================================================
# Model 5: DNSRecord
# =============================================================================


class DNSRecord(Base):
    """DNS record (A, CNAME, MX, etc)."""

    __tablename__ = "dns_records"

    id: int = Column(Integer, primary_key=True)
    scan_run_id: int = Column(Integer, ForeignKey("scan_runs.id"), nullable=False, index=True)
    domain: str = Column(String(255), nullable=False)
    record_type: str = Column(String(10), nullable=False)
    value: str = Column(String(1000), nullable=False)
    ttl: Optional[int] = Column(Integer, nullable=True)
    discovered_at: datetime = Column(DateTime, default=datetime.utcnow)

    scan_run = relationship("ScanRun", back_populates="dns_records", lazy="select")

    __table_args__ = (Index("ix_dns_records_domain_type", "domain", "record_type"),)

    def __repr__(self) -> str:
        return f"<DNSRecord(type={self.record_type}, value={self.value})>"


# =============================================================================
# Model 6: VulnerabilityMetadata
# =============================================================================


class VulnerabilityMetadata(Base):
    """Enriched vulnerability data with CVE, CVSS, EPSS, KEV."""

    __tablename__ = "vulnerability_metadata"

    id: int = Column(Integer, primary_key=True)
    vulnerability_id: int = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=False)
    cve_id: Optional[str] = Column(String(50), nullable=True)
    cvss_v31_score: Optional[float] = Column(Float, nullable=True)
    cvss_v31_vector: Optional[str] = Column(String(100), nullable=True)
    epss_score: Optional[float] = Column(Float, nullable=True)
    in_kev: bool = Column(Boolean, default=False)
    has_metasploit: bool = Column(Boolean, default=False)
    active_exploitation: bool = Column(Boolean, default=False)
    days_since_published: Optional[int] = Column(Integer, nullable=True)
    affected_versions: Optional[str] = Column(String(1000), nullable=True)
    source: Optional[str] = Column(String(100), nullable=True)
    checked_at: datetime = Column(DateTime, default=datetime.utcnow)

    vulnerability = relationship("Vulnerability", back_populates="metadata", lazy="select")

    def __repr__(self) -> str:
        return f"<VulnerabilityMetadata(cve={self.cve_id}, cvss={self.cvss_v31_score})>"


# =============================================================================
# Model 7: Technology
# =============================================================================


class Technology(Base):
    """Technology catalog (Apache, Nginx, WordPress, etc)."""

    __tablename__ = "technologies"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), nullable=False, unique=True)
    category: str = Column(String(50), nullable=False)
    type: str = Column(String(50), nullable=False)
    cpes: Optional[str] = Column(String(1000), nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    domain_technologies = relationship("DomainTechnology", back_populates="technology", lazy="select")

    def __repr__(self) -> str:
        return f"<Technology(name={self.name}, category={self.category})>"


# =============================================================================
# Model 8: DomainTechnology
# =============================================================================


class DomainTechnology(Base):
    """Junction table linking domains to detected technologies."""

    __tablename__ = "domain_technologies"

    id: int = Column(Integer, primary_key=True)
    scan_run_id: int = Column(Integer, ForeignKey("scan_runs.id"), nullable=False, index=True)
    technology_id: int = Column(Integer, ForeignKey("technologies.id"), nullable=False)
    version: Optional[str] = Column(String(100), nullable=True)
    discovered_method: Optional[str] = Column(String(100), nullable=True)
    confidence: int = Column(Integer, default=100)
    discovered_at: datetime = Column(DateTime, default=datetime.utcnow)

    scan_run = relationship("ScanRun", lazy="select")
    technology = relationship("Technology", back_populates="domain_technologies", lazy="select")

    __table_args__ = (UniqueConstraint("scan_run_id", "technology_id", name="uq_domain_tech"),)

    def __repr__(self) -> str:
        return f"<DomainTechnology(tech_id={self.technology_id}, version={self.version})>"


# =============================================================================
# Model 9: HTTPHeader
# =============================================================================


class HTTPHeader(Base):
    """HTTP response headers."""

    __tablename__ = "http_headers"

    id: int = Column(Integer, primary_key=True)
    subdomain_id: int = Column(Integer, ForeignKey("subdomains.id"), nullable=False, index=True)
    header_name: str = Column(String(255), nullable=False)
    header_value: str = Column(String(2000), nullable=False)
    discovered_at: datetime = Column(DateTime, default=datetime.utcnow)

    subdomain = relationship("Subdomain", back_populates="http_headers", lazy="select")

    __table_args__ = (Index("ix_http_headers_subdomain_name", "subdomain_id", "header_name"),)

    def __repr__(self) -> str:
        return f"<HTTPHeader(name={self.header_name}, value={self.header_value[:50]})>"


# =============================================================================
# Model 10: ServiceSignature
# =============================================================================


class ServiceSignature(Base):
    """Service fingerprint signature."""

    __tablename__ = "service_signatures"

    id: int = Column(Integer, primary_key=True)
    port: int = Column(Integer, nullable=False)
    protocol: str = Column(String(10), nullable=False)
    service_name: str = Column(String(100), nullable=False)
    banner_pattern: Optional[str] = Column(String(500), nullable=True)
    version_pattern: Optional[str] = Column(String(500), nullable=True)
    confidence: int = Column(Integer, default=80)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("port", "protocol", "service_name", name="uq_service_sig"),)

    def __repr__(self) -> str:
        return f"<ServiceSignature(service={self.service_name}, port={self.port})>"


# =============================================================================
# Model 11: ISPLocation
# =============================================================================


class ISPLocation(Base):
    """IP geolocation mapping."""

    __tablename__ = "isp_locations"

    id: int = Column(Integer, primary_key=True)
    ip_address: str = Column(String(45), nullable=False, unique=True)
    asn: Optional[str] = Column(String(20), nullable=True)
    organization: Optional[str] = Column(String(255), nullable=True)
    country_code: Optional[str] = Column(String(2), nullable=True)
    country_name: Optional[str] = Column(String(100), nullable=True)
    city: Optional[str] = Column(String(100), nullable=True)
    latitude: Optional[float] = Column(Float, nullable=True)
    longitude: Optional[float] = Column(Float, nullable=True)
    accuracy_radius: Optional[int] = Column(Integer, nullable=True)
    is_vpn: bool = Column(Boolean, default=False)
    is_proxy: bool = Column(Boolean, default=False)
    is_datacenter: bool = Column(Boolean, default=False)
    threat_level: Optional[str] = Column(String(20), nullable=True)
    last_updated: datetime = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_isp_locations_ip_asn", "ip_address", "asn"),)

    def __repr__(self) -> str:
        return f"<ISPLocation(ip={self.ip_address}, org={self.organization}, country={self.country_code})>"


# =============================================================================
# Model 12: VendorMetadata
# =============================================================================


class VendorMetadata(Base):
    """Organization/vendor metadata for TPRM."""

    __tablename__ = "vendor_metadata"

    id: int = Column(Integer, primary_key=True)
    org_name: str = Column(String(255), nullable=False, unique=True)
    website: Optional[str] = Column(String(255), nullable=True)
    industry: Optional[str] = Column(String(100), nullable=True)
    founded_year: Optional[int] = Column(Integer, nullable=True)
    employee_count: Optional[str] = Column(String(50), nullable=True)
    headquarters_country: Optional[str] = Column(String(2), nullable=True)
    breach_history: int = Column(Integer, default=0)
    last_breach_date: Optional[datetime] = Column(DateTime, nullable=True)
    breach_summary: Optional[str] = Column(String(1000), nullable=True)
    mean_time_to_repair: Optional[int] = Column(Integer, nullable=True)
    mean_time_to_detect: Optional[int] = Column(Integer, nullable=True)
    security_score: Optional[int] = Column(Integer, nullable=True)
    reputation_score: Optional[int] = Column(Integer, nullable=True)
    notes: Optional[str] = Column(String(2000), nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<VendorMetadata(org={self.org_name}, breaches={self.breach_history})>"


# =============================================================================
# Model 13: ComplianceReport
# =============================================================================


class ComplianceReport(Base):
    """Compliance audit report."""

    __tablename__ = "compliance_reports"

    id: int = Column(Integer, primary_key=True)
    scan_run_id: int = Column(Integer, ForeignKey("scan_runs.id"), nullable=False, index=True)
    org_name: str = Column(String(255), nullable=False)
    target_domain: str = Column(String(255), nullable=False)
    framework: str = Column(String(50), nullable=False)
    report_date: datetime = Column(DateTime, default=datetime.utcnow)
    audit_period_start: Optional[datetime] = Column(DateTime, nullable=True)
    audit_period_end: Optional[datetime] = Column(DateTime, nullable=True)
    compliance_score: Optional[int] = Column(Integer, nullable=True)
    critical_findings: int = Column(Integer, default=0)
    major_findings: int = Column(Integer, default=0)
    minor_findings: int = Column(Integer, default=0)
    total_controls: Optional[int] = Column(Integer, nullable=True)
    passed_controls: Optional[int] = Column(Integer, nullable=True)
    failed_controls: Optional[int] = Column(Integer, nullable=True)
    executive_summary: Optional[str] = Column(String(2000), nullable=True)
    remediation_required: bool = Column(Boolean, default=True)
    remediation_deadline: Optional[datetime] = Column(DateTime, nullable=True)
    assessor_name: Optional[str] = Column(String(255), nullable=True)
    assessor_organization: Optional[str] = Column(String(255), nullable=True)
    assessment_type: Optional[str] = Column(String(50), nullable=True)
    status: str = Column(String(50), default="draft")

    scan_run = relationship("ScanRun", back_populates="compliance_reports", lazy="select")
    compliance_checks = relationship("ComplianceCheck", back_populates="compliance_report", lazy="select")
    evidence = relationship("ComplianceEvidence", back_populates="compliance_report", lazy="select")

    __table_args__ = (Index("ix_compliance_reports_scanrun_framework", "scan_run_id", "framework"),)

    def __repr__(self) -> str:
        return f"<ComplianceReport(framework={self.framework}, compliance_score={self.compliance_score})>"


# =============================================================================
# Model 14: ComplianceCheck
# =============================================================================


class ComplianceCheck(Base):
    """Individual compliance control."""

    __tablename__ = "compliance_checks"

    id: int = Column(Integer, primary_key=True)
    compliance_report_id: int = Column(Integer, ForeignKey("compliance_reports.id"), nullable=False)
    control_id: str = Column(String(50), nullable=False)
    control_name: str = Column(String(255), nullable=False)
    control_description: Optional[str] = Column(String(1000), nullable=True)
    status: str = Column(String(20), default="fail")
    severity: Optional[str] = Column(String(20), nullable=True)
    findings_linked: int = Column(Integer, default=0)
    remediation_plan: Optional[str] = Column(String(1000), nullable=True)
    responsible_party: Optional[str] = Column(String(255), nullable=True)
    due_date: Optional[datetime] = Column(DateTime, nullable=True)
    evidence_provided: bool = Column(Boolean, default=False)
    last_checked: datetime = Column(DateTime, default=datetime.utcnow)

    compliance_report = relationship("ComplianceReport", back_populates="compliance_checks", lazy="select")
    evidence = relationship("ComplianceEvidence", back_populates="compliance_check", lazy="select")

    __table_args__ = (Index("ix_compliance_checks_report_control", "compliance_report_id", "control_id"),)

    def __repr__(self) -> str:
        return f"<ComplianceCheck(control={self.control_id}, status={self.status})>"


# =============================================================================
# Model 15: ThreatIntelData
# =============================================================================


class ThreatIntelData(Base):
    """Multi-source threat intelligence."""

    __tablename__ = "threat_intelligence"

    id: int = Column(Integer, primary_key=True)
    vulnerability_id: Optional[int] = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=True)
    intel_type: str = Column(String(50), nullable=False)
    source: str = Column(String(100), nullable=False)
    target: str = Column(String(500), nullable=False)
    severity: Optional[str] = Column(String(20), nullable=True)
    confidence: int = Column(Integer, default=100)
    first_detected: Optional[datetime] = Column(DateTime, nullable=True)
    last_detected: datetime = Column(DateTime, default=datetime.utcnow)
    detection_count: int = Column(Integer, default=1)
    metadata: Optional[str] = Column(String(2000), nullable=True)
    url: Optional[str] = Column(String(500), nullable=True)
    is_active: bool = Column(Boolean, default=True)
    mitigated: bool = Column(Boolean, default=False)
    mitigation_date: Optional[datetime] = Column(DateTime, nullable=True)

    vulnerability = relationship("Vulnerability", back_populates="threat_intel", lazy="select")

    __table_args__ = (Index("ix_threat_intel_type_source_target", "intel_type", "source", "target"),)

    def __repr__(self) -> str:
        return f"<ThreatIntelData(type={self.intel_type}, source={self.source}, target={self.target[:30]})>"


# =============================================================================
# Model 16: DataLeak
# =============================================================================


class DataLeak(Base):
    """Leaked credentials and breach data."""

    __tablename__ = "data_leaks"

    id: int = Column(Integer, primary_key=True)
    threat_intel_id: int = Column(Integer, ForeignKey("threat_intelligence.id"), nullable=False)
    email: str = Column(String(255), nullable=False)
    breach_name: str = Column(String(255), nullable=False)
    breach_date: Optional[datetime] = Column(DateTime, nullable=True)
    exposed_data: Optional[str] = Column(String(500), nullable=True)
    password_hash: Optional[str] = Column(String(255), nullable=True)
    password_plaintext: Optional[str] = Column(String(255), nullable=True)
    source_url: Optional[str] = Column(String(500), nullable=True)
    is_verified: bool = Column(Boolean, default=False)
    is_exploited: bool = Column(Boolean, default=False)
    credentials_tested: bool = Column(Boolean, default=False)
    exploit_date: Optional[datetime] = Column(DateTime, nullable=True)

    threat_intel = relationship("ThreatIntelData", lazy="select")

    __table_args__ = (Index("ix_data_leaks_email_breach", "email", "breach_date"),)

    def __repr__(self) -> str:
        return f"<DataLeak(email={self.email}, breach={self.breach_name})>"


# =============================================================================
# Model 17: ActiveExploit
# =============================================================================


class ActiveExploit(Base):
    """Public exploits for vulnerabilities."""

    __tablename__ = "active_exploits"

    id: int = Column(Integer, primary_key=True)
    vulnerability_id: int = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=False)
    cve_id: Optional[str] = Column(String(50), nullable=True)
    exploit_id: Optional[str] = Column(String(100), nullable=True)
    exploit_title: str = Column(String(255), nullable=False)
    exploit_source: str = Column(String(100), nullable=False)
    exploit_type: Optional[str] = Column(String(50), nullable=True)
    release_date: Optional[datetime] = Column(DateTime, nullable=True)
    is_public: bool = Column(Boolean, default=True)
    is_actively_exploited: bool = Column(Boolean, default=False)
    exploitation_reports: int = Column(Integer, default=0)
    proof_of_concept: bool = Column(Boolean, default=False)
    proof_of_concept_url: Optional[str] = Column(String(500), nullable=True)
    difficulty: Optional[str] = Column(String(20), nullable=True)
    popularity_score: Optional[int] = Column(Integer, nullable=True)
    last_updated: datetime = Column(DateTime, default=datetime.utcnow)

    vulnerability = relationship("Vulnerability", lazy="select")

    __table_args__ = (Index("ix_active_exploits_vuln_source", "vulnerability_id", "exploit_source"),)

    def __repr__(self) -> str:
        return f"<ActiveExploit(cve={self.cve_id}, source={self.exploit_source})>"


# =============================================================================
# Model 18: MalwareIndicator
# =============================================================================


class MalwareIndicator(Base):
    """Malware indicators (hashes, domains, IPs)."""

    __tablename__ = "malware_indicators"

    id: int = Column(Integer, primary_key=True)
    threat_intel_id: int = Column(Integer, ForeignKey("threat_intelligence.id"), nullable=False)
    indicator_type: str = Column(String(50), nullable=False)
    indicator_value: str = Column(String(500), nullable=False)
    hash_type: Optional[str] = Column(String(10), nullable=True)
    malware_family: Optional[str] = Column(String(100), nullable=True)
    yara_rule: Optional[str] = Column(String(1000), nullable=True)
    detection_count: int = Column(Integer, default=0)
    first_submission: Optional[datetime] = Column(DateTime, nullable=True)
    last_analysis: datetime = Column(DateTime, default=datetime.utcnow)
    verdict: Optional[str] = Column(String(50), nullable=True)
    analyzed_by: Optional[str] = Column(String(100), nullable=True)

    threat_intel = relationship("ThreatIntelData", lazy="select")

    __table_args__ = (Index("ix_malware_indicators_type_value", "indicator_type", "indicator_value"),)

    def __repr__(self) -> str:
        return f"<MalwareIndicator(type={self.indicator_type}, value={self.indicator_value[:30]})>"


# =============================================================================
# Model 19: ComplianceEvidence
# =============================================================================


class ComplianceEvidence(Base):
    """Evidence linking findings to compliance controls."""

    __tablename__ = "compliance_evidence"

    id: int = Column(Integer, primary_key=True)
    compliance_report_id: int = Column(Integer, ForeignKey("compliance_reports.id"), nullable=False)
    compliance_check_id: int = Column(Integer, ForeignKey("compliance_checks.id"), nullable=False)
    vulnerability_id: Optional[int] = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=True)
    evidence_type: str = Column(String(50), nullable=False)
    description: str = Column(String(1000), nullable=False)
    evidence_file: Optional[str] = Column(String(255), nullable=True)
    collected_date: datetime = Column(DateTime, default=datetime.utcnow)
    verified: bool = Column(Boolean, default=False)
    verifier_name: Optional[str] = Column(String(255), nullable=True)
    verification_date: Optional[datetime] = Column(DateTime, nullable=True)

    compliance_report = relationship("ComplianceReport", back_populates="evidence", lazy="select")
    compliance_check = relationship("ComplianceCheck", back_populates="evidence", lazy="select")
    vulnerability = relationship("Vulnerability", lazy="select")

    def __repr__(self) -> str:
        return f"<ComplianceEvidence(control={self.compliance_check_id}, type={self.evidence_type})>"


# =============================================================================
# Model 20: BaselineSnapshot
# =============================================================================


class BaselineSnapshot(Base):
    """Scan snapshot for baseline comparison and change detection."""

    __tablename__ = "baseline_snapshots"

    id: int = Column(Integer, primary_key=True)
    scan_run_id: int = Column(Integer, ForeignKey("scan_runs.id"), nullable=False)
    snapshot_date: datetime = Column(DateTime, default=datetime.utcnow)
    is_baseline: bool = Column(Boolean, default=False)
    asset_count: Optional[int] = Column(Integer, nullable=True)
    subdomain_count: Optional[int] = Column(Integer, nullable=True)
    port_count: Optional[int] = Column(Integer, nullable=True)
    vulnerability_count: Optional[int] = Column(Integer, nullable=True)
    technology_count: Optional[int] = Column(Integer, nullable=True)
    risk_score_snapshot: Optional[int] = Column(Integer, nullable=True)
    snapshot_data: Optional[str] = Column(Text, nullable=True)
    md5_hash: Optional[str] = Column(String(32), nullable=True)

    scan_run = relationship("ScanRun", lazy="select")

    __table_args__ = (Index("ix_baseline_snapshots_scanrun_baseline", "scan_run_id", "is_baseline"),)

    def __repr__(self) -> str:
        return f"<BaselineSnapshot(scan_run={self.scan_run_id}, is_baseline={self.is_baseline})>"


# =============================================================================
# Model 21: ScanProgress
# =============================================================================


class ScanProgress(Base):
    """Real-time scan progress tracking."""

    __tablename__ = "scan_progress"

    id: int = Column(Integer, primary_key=True)
    scan_run_id: int = Column(Integer, ForeignKey("scan_runs.id"), nullable=False, unique=True)
    current_phase: int = Column(Integer, default=0)
    current_tool: Optional[str] = Column(String(100), nullable=True)
    progress_percentage: int = Column(Integer, default=0)
    status: str = Column(String(50), default="queued")
    subdomains_found: int = Column(Integer, default=0)
    ports_found: int = Column(Integer, default=0)
    vulnerabilities_found: int = Column(Integer, default=0)
    assets_added: int = Column(Integer, default=0)
    assets_removed: int = Column(Integer, default=0)
    last_update: datetime = Column(DateTime, default=datetime.utcnow)
    estimated_completion: Optional[datetime] = Column(DateTime, nullable=True)
    duration_seconds: Optional[int] = Column(Integer, nullable=True)

    scan_run = relationship("ScanRun", lazy="select")

    def __repr__(self) -> str:
        return f"<ScanProgress(scan={self.scan_run_id}, phase={self.current_phase}, progress={self.progress_percentage}%)>"


# =============================================================================
# Model 22: CacheEntry
# =============================================================================


class CacheEntry(Base):
    """Query result cache."""

    __tablename__ = "cache_entries"

    id: int = Column(Integer, primary_key=True)
    cache_key: str = Column(String(500), nullable=False, unique=True)
    cache_value: str = Column(Text, nullable=False)
    source: str = Column(String(100), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    expires_at: Optional[datetime] = Column(DateTime, nullable=True)
    hit_count: int = Column(Integer, default=0)
    is_expired: bool = Column(Boolean, default=False)

    __table_args__ = (Index("ix_cache_entries_key_expires", "cache_key", "expires_at"),)

    def __repr__(self) -> str:
        return f"<CacheEntry(key={self.cache_key[:30]}, source={self.source})>"


# =============================================================================
# Model 23: APIToken
# =============================================================================


class APIToken(Base):
    """API authentication tokens."""

    __tablename__ = "api_tokens"

    id: int = Column(Integer, primary_key=True)
    token_hash: str = Column(String(255), nullable=False, unique=True)
    user_name: str = Column(String(255), nullable=False)
    token_type: str = Column(String(50), default="bearer")
    scopes: Optional[str] = Column(String(500), nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    last_used: Optional[datetime] = Column(DateTime, nullable=True)
    expires_at: Optional[datetime] = Column(DateTime, nullable=True)
    is_active: bool = Column(Boolean, default=True)
    ip_whitelist: Optional[str] = Column(String(1000), nullable=True)
    rate_limit: int = Column(Integer, default=1000)

    __table_args__ = (Index("ix_api_tokens_hash_active", "token_hash", "is_active"),)

    def __repr__(self) -> str:
        return f"<APIToken(user={self.user_name}, active={self.is_active})>"


# =============================================================================
# Model 24: AuditLog
# =============================================================================


class AuditLog(Base):
    """Security audit trail."""

    __tablename__ = "audit_logs"

    id: int = Column(Integer, primary_key=True)
    user_name: str = Column(String(255), nullable=False)
    action: str = Column(String(255), nullable=False)
    resource_type: str = Column(String(50), nullable=False)
    resource_id: Optional[str] = Column(String(255), nullable=True)
    old_value: Optional[str] = Column(String(1000), nullable=True)
    new_value: Optional[str] = Column(String(1000), nullable=True)
    status: str = Column(String(20), default="success")
    timestamp: datetime = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address: Optional[str] = Column(String(45), nullable=True)
    user_agent: Optional[str] = Column(String(500), nullable=True)
    error_message: Optional[str] = Column(String(500), nullable=True)

    __table_args__ = (Index("ix_audit_logs_user_timestamp", "user_name", "timestamp"),)

    def __repr__(self) -> str:
        return f"<AuditLog(user={self.user_name}, action={self.action}, timestamp={self.timestamp})>"


# =============================================================================
# Convenience: __all__ for imports
# =============================================================================

__all__ = [
    "ScanRun", "Subdomain", "PortScan", "Vulnerability", "DNSRecord",
    "VulnerabilityMetadata", "Technology", "DomainTechnology", "HTTPHeader",
    "ServiceSignature", "ISPLocation", "VendorMetadata", "ComplianceReport",
    "ComplianceCheck", "ThreatIntelData", "DataLeak", "ActiveExploit",
    "MalwareIndicator", "ComplianceEvidence", "BaselineSnapshot",
    "ScanProgress", "CacheEntry", "APIToken", "AuditLog",
]
'''

with open(MODELS_PATH, 'w') as f:
    f.write(CONTENT)

print(f"Written {len(CONTENT)} bytes to {MODELS_PATH}")
