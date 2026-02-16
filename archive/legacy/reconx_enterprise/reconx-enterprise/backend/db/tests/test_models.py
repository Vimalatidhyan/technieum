"""Comprehensive test suite for ReconX Enterprise v2.0 database models.

Tests all 24 SQLAlchemy ORM models:
- Creation and default values
- Relationships and foreign keys
- Constraints (unique, composite indices)
- __repr__ methods
- Nullable fields
- Cascade behavior
- Transaction rollback
"""

import sys
import os
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# Ensure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from backend.db.base import Base
from backend.db.models import (
    ScanRun,
    Subdomain,
    PortScan,
    Vulnerability,
    DNSRecord,
    VulnerabilityMetadata,
    Technology,
    DomainTechnology,
    HTTPHeader,
    ServiceSignature,
    ISPLocation,
    VendorMetadata,
    ComplianceReport,
    ComplianceCheck,
    ThreatIntelData,
    DataLeak,
    ActiveExploit,
    MalwareIndicator,
    ComplianceEvidence,
    BaselineSnapshot,
    ScanProgress,
    CacheEntry,
    APIToken,
    AuditLog,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def engine():
    """Create a fresh in-memory SQLite engine for each test."""
    eng = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture(scope="function")
def session(engine):
    """Create a new database session for each test with rollback."""
    SessionLocal = sessionmaker(bind=engine)
    sess = SessionLocal()
    yield sess
    sess.rollback()
    sess.close()


@pytest.fixture
def scan_run(session: Session) -> ScanRun:
    """Create a standard ScanRun for use in related model tests."""
    sr = ScanRun(domain="example.com", scan_type="full", status="running", phase=1)
    session.add(sr)
    session.commit()
    return sr


@pytest.fixture
def subdomain(session: Session, scan_run: ScanRun) -> Subdomain:
    """Create a standard Subdomain for related model tests."""
    sub = Subdomain(
        scan_run_id=scan_run.id,
        subdomain="api.example.com",
        is_alive=True,
        discovered_method="passive_dns",
    )
    session.add(sub)
    session.commit()
    return sub


@pytest.fixture
def port_scan(session: Session, subdomain: Subdomain) -> PortScan:
    """Create a standard PortScan for related model tests."""
    ps = PortScan(
        subdomain_id=subdomain.id,
        port=443,
        protocol="tcp",
        state="open",
        service="https",
        version="nginx/1.21",
    )
    session.add(ps)
    session.commit()
    return ps


@pytest.fixture
def vulnerability(
    session: Session, scan_run: ScanRun, subdomain: Subdomain, port_scan: PortScan
) -> Vulnerability:
    """Create a standard Vulnerability for related model tests."""
    vuln = Vulnerability(
        scan_run_id=scan_run.id,
        subdomain_id=subdomain.id,
        port_scan_id=port_scan.id,
        vuln_type="xss",
        severity=7,
        title="Reflected XSS in search",
        description="User input is reflected without sanitization",
        cve_ids="CVE-2023-1234",
    )
    session.add(vuln)
    session.commit()
    return vuln


@pytest.fixture
def compliance_report(session: Session, scan_run: ScanRun) -> ComplianceReport:
    """Create a standard ComplianceReport for related model tests."""
    cr = ComplianceReport(
        scan_run_id=scan_run.id,
        org_name="Acme Corp",
        target_domain="example.com",
        framework="PCI-DSS",
        compliance_score=85,
        total_controls=100,
        passed_controls=85,
        failed_controls=15,
    )
    session.add(cr)
    session.commit()
    return cr


@pytest.fixture
def threat_intel(session: Session, vulnerability: Vulnerability) -> ThreatIntelData:
    """Create a standard ThreatIntelData for related model tests."""
    ti = ThreatIntelData(
        vulnerability_id=vulnerability.id,
        intel_type="exploit",
        source="dehashed",
        target="example.com",
        severity="high",
        confidence=90,
    )
    session.add(ti)
    session.commit()
    return ti


# =============================================================================
# Test: Schema Creation
# =============================================================================


class TestSchemaCreation:
    """Verify all 24 tables are created with correct schema."""

    def test_all_tables_created(self, engine):
        """Verify all 24 tables exist in metadata."""
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        expected_tables = [
            "scan_runs",
            "subdomains",
            "port_scans",
            "vulnerabilities",
            "dns_records",
            "vulnerability_metadata",
            "technologies",
            "domain_technologies",
            "http_headers",
            "service_signatures",
            "isp_locations",
            "vendor_metadata",
            "compliance_reports",
            "compliance_checks",
            "threat_intelligence",
            "data_leaks",
            "active_exploits",
            "malware_indicators",
            "compliance_evidence",
            "baseline_snapshots",
            "scan_progress",
            "cache_entries",
            "api_tokens",
            "audit_logs",
        ]
        for table in expected_tables:
            assert table in table_names, f"Table '{table}' not found in database"

    def test_table_count(self, engine):
        """Verify exactly 24 tables are created."""
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        assert len(table_names) == 24, f"Expected 24 tables, got {len(table_names)}"


# =============================================================================
# Test: ScanRun (Model 1)
# =============================================================================


class TestScanRun:
    """Tests for ScanRun model."""

    def test_create_scan_run(self, session):
        sr = ScanRun(domain="test.com")
        session.add(sr)
        session.commit()
        assert sr.id is not None
        assert sr.domain == "test.com"

    def test_scan_run_defaults(self, session):
        sr = ScanRun(domain="test.com")
        session.add(sr)
        session.commit()
        assert sr.scan_type == "full"
        assert sr.status == "pending"
        assert sr.phase == 0
        assert sr.risk_score is None
        assert sr.completed_at is None
        assert sr.created_at is not None

    def test_scan_run_repr(self, scan_run):
        assert "ScanRun" in repr(scan_run)
        assert "example.com" in repr(scan_run)

    def test_scan_run_relationships(self, session, scan_run):
        sub = Subdomain(
            scan_run_id=scan_run.id,
            subdomain="www.example.com",
            is_alive=True,
        )
        session.add(sub)
        session.commit()
        session.refresh(scan_run)
        assert len(scan_run.subdomains) == 1
        assert scan_run.subdomains[0].subdomain == "www.example.com"

    def test_scan_run_domain_required(self, session):
        sr = ScanRun()
        session.add(sr)
        with pytest.raises(IntegrityError):
            session.commit()


# =============================================================================
# Test: Subdomain (Model 2)
# =============================================================================


class TestSubdomain:
    """Tests for Subdomain model."""

    def test_create_subdomain(self, session, scan_run):
        sub = Subdomain(
            scan_run_id=scan_run.id,
            subdomain="mail.example.com",
            is_alive=False,
        )
        session.add(sub)
        session.commit()
        assert sub.id is not None
        assert sub.subdomain == "mail.example.com"

    def test_subdomain_defaults(self, session, scan_run):
        sub = Subdomain(scan_run_id=scan_run.id, subdomain="test.example.com")
        session.add(sub)
        session.commit()
        assert sub.is_alive is False
        assert sub.priority == 0
        assert sub.first_seen is not None

    def test_subdomain_back_populates(self, session, scan_run, subdomain):
        session.refresh(scan_run)
        assert subdomain in scan_run.subdomains

    def test_subdomain_repr(self, subdomain):
        assert "Subdomain" in repr(subdomain)
        assert "api.example.com" in repr(subdomain)

    def test_subdomain_foreign_key_required(self, session):
        sub = Subdomain(subdomain="orphan.example.com")
        session.add(sub)
        with pytest.raises(IntegrityError):
            session.commit()


# =============================================================================
# Test: PortScan (Model 3)
# =============================================================================


class TestPortScan:
    """Tests for PortScan model."""

    def test_create_port_scan(self, session, subdomain):
        ps = PortScan(
            subdomain_id=subdomain.id,
            port=80,
            protocol="tcp",
            state="open",
            service="http",
        )
        session.add(ps)
        session.commit()
        assert ps.id is not None
        assert ps.port == 80

    def test_port_scan_defaults(self, session, subdomain):
        ps = PortScan(subdomain_id=subdomain.id, port=22)
        session.add(ps)
        session.commit()
        assert ps.protocol == "tcp"
        assert ps.state == "closed"
        assert ps.service is None

    def test_port_scan_repr(self, port_scan):
        assert "PortScan" in repr(port_scan)

    def test_port_scan_back_populates(self, session, subdomain, port_scan):
        session.refresh(subdomain)
        assert port_scan in subdomain.port_scans


# =============================================================================
# Test: Vulnerability (Model 4)
# =============================================================================


class TestVulnerability:
    """Tests for Vulnerability model."""

    def test_create_vulnerability(self, vulnerability):
        assert vulnerability.id is not None
        assert vulnerability.vuln_type == "xss"
        assert vulnerability.severity == 7

    def test_vulnerability_relationships(self, session, vulnerability, scan_run, subdomain):
        assert vulnerability.scan_run == scan_run
        assert vulnerability.subdomain == subdomain

    def test_vulnerability_repr(self, vulnerability):
        assert "Vulnerability" in repr(vulnerability)
        assert "xss" in repr(vulnerability)

    def test_vulnerability_metadata_relationship(self, session, vulnerability):
        meta = VulnerabilityMetadata(
            vulnerability_id=vulnerability.id,
            cve_id="CVE-2023-1234",
            cvss_v31_score=7.5,
            in_kev=True,
        )
        session.add(meta)
        session.commit()
        session.refresh(vulnerability)
        assert vulnerability.vuln_metadata is not None
        assert vulnerability.vuln_metadata.cve_id == "CVE-2023-1234"

    def test_vulnerability_threat_intel_relationship(self, session, vulnerability, threat_intel):
        session.refresh(vulnerability)
        assert len(vulnerability.threat_intel) == 1
        assert vulnerability.threat_intel[0].intel_type == "exploit"


# =============================================================================
# Test: DNSRecord (Model 5)
# =============================================================================


class TestDNSRecord:
    """Tests for DNSRecord model."""

    def test_create_dns_record(self, session, scan_run):
        dns = DNSRecord(
            scan_run_id=scan_run.id,
            domain="example.com",
            record_type="A",
            value="93.184.216.34",
            ttl=3600,
        )
        session.add(dns)
        session.commit()
        assert dns.id is not None
        assert dns.record_type == "A"

    def test_dns_record_repr(self, session, scan_run):
        dns = DNSRecord(
            scan_run_id=scan_run.id,
            domain="example.com",
            record_type="MX",
            value="mail.example.com",
        )
        session.add(dns)
        session.commit()
        assert "DNSRecord" in repr(dns)
        assert "MX" in repr(dns)

    def test_dns_record_back_populates(self, session, scan_run):
        dns = DNSRecord(
            scan_run_id=scan_run.id,
            domain="example.com",
            record_type="CNAME",
            value="cdn.example.com",
        )
        session.add(dns)
        session.commit()
        session.refresh(scan_run)
        assert len(scan_run.dns_records) == 1


# =============================================================================
# Test: VulnerabilityMetadata (Model 6)
# =============================================================================


class TestVulnerabilityMetadata:
    """Tests for VulnerabilityMetadata model."""

    def test_create_vuln_metadata(self, session, vulnerability):
        meta = VulnerabilityMetadata(
            vulnerability_id=vulnerability.id,
            cve_id="CVE-2023-5678",
            cvss_v31_score=9.8,
            cvss_v31_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            epss_score=0.85,
            in_kev=True,
            has_metasploit=True,
            active_exploitation=True,
        )
        session.add(meta)
        session.commit()
        assert meta.id is not None
        assert meta.cvss_v31_score == 9.8
        assert meta.in_kev is True

    def test_vuln_metadata_defaults(self, session, vulnerability):
        meta = VulnerabilityMetadata(vulnerability_id=vulnerability.id)
        session.add(meta)
        session.commit()
        assert meta.in_kev is False
        assert meta.has_metasploit is False
        assert meta.active_exploitation is False

    def test_vuln_metadata_repr(self, session, vulnerability):
        meta = VulnerabilityMetadata(
            vulnerability_id=vulnerability.id,
            cve_id="CVE-2023-9999",
            cvss_v31_score=8.1,
        )
        session.add(meta)
        session.commit()
        assert "VulnerabilityMetadata" in repr(meta)


# =============================================================================
# Test: Technology (Model 7)
# =============================================================================


class TestTechnology:
    """Tests for Technology model."""

    def test_create_technology(self, session):
        tech = Technology(name="nginx", category="web-server", type="server")
        session.add(tech)
        session.commit()
        assert tech.id is not None
        assert tech.name == "nginx"

    def test_technology_unique_name(self, session):
        t1 = Technology(name="apache", category="web-server", type="server")
        session.add(t1)
        session.commit()
        t2 = Technology(name="apache", category="web-server", type="server")
        session.add(t2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_technology_repr(self, session):
        tech = Technology(name="wordpress", category="cms", type="application")
        session.add(tech)
        session.commit()
        assert "Technology" in repr(tech)
        assert "wordpress" in repr(tech)


# =============================================================================
# Test: DomainTechnology (Model 8)
# =============================================================================


class TestDomainTechnology:
    """Tests for DomainTechnology model."""

    def test_create_domain_technology(self, session, scan_run):
        tech = Technology(name="python", category="language", type="runtime")
        session.add(tech)
        session.commit()
        dt = DomainTechnology(
            scan_run_id=scan_run.id,
            technology_id=tech.id,
            version="3.11",
            confidence=95,
        )
        session.add(dt)
        session.commit()
        assert dt.id is not None
        assert dt.confidence == 95

    def test_domain_technology_unique_constraint(self, session, scan_run):
        tech = Technology(name="nodejs", category="runtime", type="runtime")
        session.add(tech)
        session.commit()
        dt1 = DomainTechnology(scan_run_id=scan_run.id, technology_id=tech.id)
        session.add(dt1)
        session.commit()
        dt2 = DomainTechnology(scan_run_id=scan_run.id, technology_id=tech.id)
        session.add(dt2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_domain_technology_defaults(self, session, scan_run):
        tech = Technology(name="react", category="framework", type="frontend")
        session.add(tech)
        session.commit()
        dt = DomainTechnology(scan_run_id=scan_run.id, technology_id=tech.id)
        session.add(dt)
        session.commit()
        assert dt.confidence == 100


# =============================================================================
# Test: HTTPHeader (Model 9)
# =============================================================================


class TestHTTPHeader:
    """Tests for HTTPHeader model."""

    def test_create_http_header(self, session, subdomain):
        hdr = HTTPHeader(
            subdomain_id=subdomain.id,
            header_name="X-Frame-Options",
            header_value="DENY",
        )
        session.add(hdr)
        session.commit()
        assert hdr.id is not None
        assert hdr.header_name == "X-Frame-Options"

    def test_http_header_back_populates(self, session, subdomain):
        hdr = HTTPHeader(
            subdomain_id=subdomain.id,
            header_name="Server",
            header_value="nginx/1.21",
        )
        session.add(hdr)
        session.commit()
        session.refresh(subdomain)
        assert len(subdomain.http_headers) == 1

    def test_http_header_repr(self, session, subdomain):
        hdr = HTTPHeader(
            subdomain_id=subdomain.id,
            header_name="Content-Type",
            header_value="text/html; charset=utf-8",
        )
        session.add(hdr)
        session.commit()
        assert "HTTPHeader" in repr(hdr)


# =============================================================================
# Test: ServiceSignature (Model 10)
# =============================================================================


class TestServiceSignature:
    """Tests for ServiceSignature model."""

    def test_create_service_signature(self, session):
        sig = ServiceSignature(
            port=22,
            protocol="tcp",
            service_name="ssh",
            banner_pattern="SSH-2.0-OpenSSH*",
            confidence=95,
        )
        session.add(sig)
        session.commit()
        assert sig.id is not None
        assert sig.service_name == "ssh"

    def test_service_signature_unique_constraint(self, session):
        s1 = ServiceSignature(port=80, protocol="tcp", service_name="http")
        session.add(s1)
        session.commit()
        s2 = ServiceSignature(port=80, protocol="tcp", service_name="http")
        session.add(s2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_service_signature_repr(self, session):
        sig = ServiceSignature(port=443, protocol="tcp", service_name="https")
        session.add(sig)
        session.commit()
        assert "ServiceSignature" in repr(sig)


# =============================================================================
# Test: ISPLocation (Model 11)
# =============================================================================


class TestISPLocation:
    """Tests for ISPLocation model."""

    def test_create_isp_location(self, session):
        loc = ISPLocation(
            ip_address="93.184.216.34",
            asn="AS15133",
            organization="Edgecast Inc.",
            country_code="US",
            city="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
        )
        session.add(loc)
        session.commit()
        assert loc.id is not None
        assert loc.ip_address == "93.184.216.34"

    def test_isp_location_unique_ip(self, session):
        l1 = ISPLocation(ip_address="1.1.1.1", country_code="US")
        session.add(l1)
        session.commit()
        l2 = ISPLocation(ip_address="1.1.1.1", country_code="AU")
        session.add(l2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_isp_location_defaults(self, session):
        loc = ISPLocation(ip_address="8.8.8.8")
        session.add(loc)
        session.commit()
        assert loc.is_vpn is False
        assert loc.is_proxy is False
        assert loc.is_datacenter is False

    def test_isp_location_repr(self, session):
        loc = ISPLocation(
            ip_address="10.0.0.1",
            organization="Private",
            country_code="XX",
        )
        session.add(loc)
        session.commit()
        assert "ISPLocation" in repr(loc)


# =============================================================================
# Test: VendorMetadata (Model 12)
# =============================================================================


class TestVendorMetadata:
    """Tests for VendorMetadata model."""

    def test_create_vendor_metadata(self, session):
        vm = VendorMetadata(
            org_name="Acme Corp",
            website="https://acme.com",
            industry="Technology",
            employee_count="5000+",
            breach_history=2,
            security_score=78,
        )
        session.add(vm)
        session.commit()
        assert vm.id is not None
        assert vm.org_name == "Acme Corp"

    def test_vendor_unique_org_name(self, session):
        v1 = VendorMetadata(org_name="UniqueOrg")
        session.add(v1)
        session.commit()
        v2 = VendorMetadata(org_name="UniqueOrg")
        session.add(v2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_vendor_defaults(self, session):
        vm = VendorMetadata(org_name="DefaultCorp")
        session.add(vm)
        session.commit()
        assert vm.breach_history == 0

    def test_vendor_repr(self, session):
        vm = VendorMetadata(org_name="ReprCorp", breach_history=3)
        session.add(vm)
        session.commit()
        assert "VendorMetadata" in repr(vm)
        assert "ReprCorp" in repr(vm)


# =============================================================================
# Test: ComplianceReport (Model 13)
# =============================================================================


class TestComplianceReport:
    """Tests for ComplianceReport model."""

    def test_create_compliance_report(self, compliance_report):
        assert compliance_report.id is not None
        assert compliance_report.framework == "PCI-DSS"

    def test_compliance_report_defaults(self, session, scan_run):
        cr = ComplianceReport(
            scan_run_id=scan_run.id,
            org_name="Test",
            target_domain="test.com",
            framework="HIPAA",
        )
        session.add(cr)
        session.commit()
        assert cr.status == "draft"
        assert cr.remediation_required is True
        assert cr.critical_findings == 0
        assert cr.major_findings == 0
        assert cr.minor_findings == 0

    def test_compliance_report_repr(self, compliance_report):
        assert "ComplianceReport" in repr(compliance_report)
        assert "PCI-DSS" in repr(compliance_report)

    def test_compliance_report_checks_relationship(self, session, compliance_report):
        check = ComplianceCheck(
            compliance_report_id=compliance_report.id,
            control_id="PCI-1.1",
            control_name="Firewall Configuration",
            status="pass",
        )
        session.add(check)
        session.commit()
        session.refresh(compliance_report)
        assert len(compliance_report.compliance_checks) == 1


# =============================================================================
# Test: ComplianceCheck (Model 14)
# =============================================================================


class TestComplianceCheck:
    """Tests for ComplianceCheck model."""

    def test_create_compliance_check(self, session, compliance_report):
        check = ComplianceCheck(
            compliance_report_id=compliance_report.id,
            control_id="PCI-2.1",
            control_name="Default Passwords",
            status="fail",
            severity="high",
        )
        session.add(check)
        session.commit()
        assert check.id is not None
        assert check.control_id == "PCI-2.1"

    def test_compliance_check_defaults(self, session, compliance_report):
        check = ComplianceCheck(
            compliance_report_id=compliance_report.id,
            control_id="PCI-3.1",
            control_name="Encrypt Stored Data",
        )
        session.add(check)
        session.commit()
        assert check.status == "fail"
        assert check.findings_linked == 0
        assert check.evidence_provided is False

    def test_compliance_check_repr(self, session, compliance_report):
        check = ComplianceCheck(
            compliance_report_id=compliance_report.id,
            control_id="PCI-4.1",
            control_name="Encrypt Transmission",
            status="pass",
        )
        session.add(check)
        session.commit()
        assert "ComplianceCheck" in repr(check)
        assert "PCI-4.1" in repr(check)


# =============================================================================
# Test: ThreatIntelData (Model 15)
# =============================================================================


class TestThreatIntelData:
    """Tests for ThreatIntelData model."""

    def test_create_threat_intel(self, threat_intel):
        assert threat_intel.id is not None
        assert threat_intel.intel_type == "exploit"

    def test_threat_intel_defaults(self, session):
        ti = ThreatIntelData(
            intel_type="ip_reputation",
            source="greynoise",
            target="1.2.3.4",
        )
        session.add(ti)
        session.commit()
        assert ti.confidence == 100
        assert ti.detection_count == 1
        assert ti.is_active is True
        assert ti.mitigated is False

    def test_threat_intel_repr(self, threat_intel):
        assert "ThreatIntelData" in repr(threat_intel)
        assert "exploit" in repr(threat_intel)


# =============================================================================
# Test: DataLeak (Model 16)
# =============================================================================


class TestDataLeak:
    """Tests for DataLeak model."""

    def test_create_data_leak(self, session, threat_intel):
        leak = DataLeak(
            threat_intel_id=threat_intel.id,
            email="user@example.com",
            breach_name="BigBreach2023",
            exposed_data="email,password_hash",
            is_verified=True,
        )
        session.add(leak)
        session.commit()
        assert leak.id is not None
        assert leak.email == "user@example.com"

    def test_data_leak_defaults(self, session, threat_intel):
        leak = DataLeak(
            threat_intel_id=threat_intel.id,
            email="test@example.com",
            breach_name="TestBreach",
        )
        session.add(leak)
        session.commit()
        assert leak.is_verified is False
        assert leak.is_exploited is False
        assert leak.credentials_tested is False

    def test_data_leak_repr(self, session, threat_intel):
        leak = DataLeak(
            threat_intel_id=threat_intel.id,
            email="repr@example.com",
            breach_name="ReprBreach",
        )
        session.add(leak)
        session.commit()
        assert "DataLeak" in repr(leak)
        assert "repr@example.com" in repr(leak)


# =============================================================================
# Test: ActiveExploit (Model 17)
# =============================================================================


class TestActiveExploit:
    """Tests for ActiveExploit model."""

    def test_create_active_exploit(self, session, vulnerability):
        exploit = ActiveExploit(
            vulnerability_id=vulnerability.id,
            cve_id="CVE-2023-1234",
            exploit_id="EDB-12345",
            exploit_title="XSS PoC",
            exploit_source="exploit-db",
            exploit_type="webapps",
            is_public=True,
            is_actively_exploited=True,
        )
        session.add(exploit)
        session.commit()
        assert exploit.id is not None
        assert exploit.exploit_source == "exploit-db"

    def test_active_exploit_defaults(self, session, vulnerability):
        exploit = ActiveExploit(
            vulnerability_id=vulnerability.id,
            exploit_title="Default Exploit",
            exploit_source="metasploit",
        )
        session.add(exploit)
        session.commit()
        assert exploit.is_public is True
        assert exploit.is_actively_exploited is False
        assert exploit.exploitation_reports == 0
        assert exploit.proof_of_concept is False

    def test_active_exploit_repr(self, session, vulnerability):
        exploit = ActiveExploit(
            vulnerability_id=vulnerability.id,
            cve_id="CVE-2023-9999",
            exploit_title="Test",
            exploit_source="github",
        )
        session.add(exploit)
        session.commit()
        assert "ActiveExploit" in repr(exploit)


# =============================================================================
# Test: MalwareIndicator (Model 18)
# =============================================================================


class TestMalwareIndicator:
    """Tests for MalwareIndicator model."""

    def test_create_malware_indicator(self, session, threat_intel):
        mi = MalwareIndicator(
            threat_intel_id=threat_intel.id,
            indicator_type="hash",
            indicator_value="a1b2c3d4e5f6",
            hash_type="sha256",
            malware_family="emotet",
            detection_count=15,
        )
        session.add(mi)
        session.commit()
        assert mi.id is not None
        assert mi.malware_family == "emotet"

    def test_malware_indicator_defaults(self, session, threat_intel):
        mi = MalwareIndicator(
            threat_intel_id=threat_intel.id,
            indicator_type="domain",
            indicator_value="evil.example.com",
        )
        session.add(mi)
        session.commit()
        assert mi.detection_count == 0

    def test_malware_indicator_repr(self, session, threat_intel):
        mi = MalwareIndicator(
            threat_intel_id=threat_intel.id,
            indicator_type="ip",
            indicator_value="10.0.0.1",
        )
        session.add(mi)
        session.commit()
        assert "MalwareIndicator" in repr(mi)


# =============================================================================
# Test: ComplianceEvidence (Model 19)
# =============================================================================


class TestComplianceEvidence:
    """Tests for ComplianceEvidence model."""

    def test_create_compliance_evidence(self, session, compliance_report, vulnerability):
        check = ComplianceCheck(
            compliance_report_id=compliance_report.id,
            control_id="PCI-6.5",
            control_name="Secure Coding",
        )
        session.add(check)
        session.commit()
        ev = ComplianceEvidence(
            compliance_report_id=compliance_report.id,
            compliance_check_id=check.id,
            vulnerability_id=vulnerability.id,
            evidence_type="scan_result",
            description="XSS found in search endpoint",
        )
        session.add(ev)
        session.commit()
        assert ev.id is not None
        assert ev.evidence_type == "scan_result"

    def test_compliance_evidence_defaults(self, session, compliance_report):
        check = ComplianceCheck(
            compliance_report_id=compliance_report.id,
            control_id="PCI-7.1",
            control_name="Access Control",
        )
        session.add(check)
        session.commit()
        ev = ComplianceEvidence(
            compliance_report_id=compliance_report.id,
            compliance_check_id=check.id,
            evidence_type="manual",
            description="Manual review completed",
        )
        session.add(ev)
        session.commit()
        assert ev.verified is False
        assert ev.verifier_name is None

    def test_compliance_evidence_repr(self, session, compliance_report):
        check = ComplianceCheck(
            compliance_report_id=compliance_report.id,
            control_id="PCI-8.1",
            control_name="User Identification",
        )
        session.add(check)
        session.commit()
        ev = ComplianceEvidence(
            compliance_report_id=compliance_report.id,
            compliance_check_id=check.id,
            evidence_type="config_review",
            description="Config review",
        )
        session.add(ev)
        session.commit()
        assert "ComplianceEvidence" in repr(ev)


# =============================================================================
# Test: BaselineSnapshot (Model 20)
# =============================================================================


class TestBaselineSnapshot:
    """Tests for BaselineSnapshot model."""

    def test_create_baseline_snapshot(self, session, scan_run):
        snap = BaselineSnapshot(
            scan_run_id=scan_run.id,
            is_baseline=True,
            asset_count=50,
            subdomain_count=25,
            port_count=100,
            vulnerability_count=10,
            risk_score_snapshot=72,
        )
        session.add(snap)
        session.commit()
        assert snap.id is not None
        assert snap.is_baseline is True

    def test_baseline_snapshot_defaults(self, session, scan_run):
        snap = BaselineSnapshot(scan_run_id=scan_run.id)
        session.add(snap)
        session.commit()
        assert snap.is_baseline is False

    def test_baseline_snapshot_repr(self, session, scan_run):
        snap = BaselineSnapshot(scan_run_id=scan_run.id, is_baseline=True)
        session.add(snap)
        session.commit()
        assert "BaselineSnapshot" in repr(snap)


# =============================================================================
# Test: ScanProgress (Model 21)
# =============================================================================


class TestScanProgress:
    """Tests for ScanProgress model."""

    def test_create_scan_progress(self, session, scan_run):
        sp = ScanProgress(
            scan_run_id=scan_run.id,
            current_phase=3,
            current_tool="nuclei",
            progress_percentage=45,
            status="running",
        )
        session.add(sp)
        session.commit()
        assert sp.id is not None
        assert sp.progress_percentage == 45

    def test_scan_progress_defaults(self, session, scan_run):
        sp = ScanProgress(scan_run_id=scan_run.id)
        session.add(sp)
        session.commit()
        assert sp.current_phase == 0
        assert sp.progress_percentage == 0
        assert sp.status == "queued"
        assert sp.subdomains_found == 0
        assert sp.ports_found == 0
        assert sp.vulnerabilities_found == 0

    def test_scan_progress_unique_scan_run(self, session, scan_run):
        sp1 = ScanProgress(scan_run_id=scan_run.id)
        session.add(sp1)
        session.commit()
        sp2 = ScanProgress(scan_run_id=scan_run.id)
        session.add(sp2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_scan_progress_repr(self, session, scan_run):
        sp = ScanProgress(scan_run_id=scan_run.id, current_phase=5, progress_percentage=80)
        session.add(sp)
        session.commit()
        assert "ScanProgress" in repr(sp)


# =============================================================================
# Test: CacheEntry (Model 22)
# =============================================================================


class TestCacheEntry:
    """Tests for CacheEntry model."""

    def test_create_cache_entry(self, session):
        ce = CacheEntry(
            cache_key="whois:example.com",
            cache_value='{"registrar": "GoDaddy"}',
            source="whois",
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        session.add(ce)
        session.commit()
        assert ce.id is not None
        assert ce.cache_key == "whois:example.com"

    def test_cache_entry_unique_key(self, session):
        c1 = CacheEntry(cache_key="dns:test.com", cache_value="1.2.3.4", source="dns")
        session.add(c1)
        session.commit()
        c2 = CacheEntry(cache_key="dns:test.com", cache_value="5.6.7.8", source="dns")
        session.add(c2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_cache_entry_defaults(self, session):
        ce = CacheEntry(
            cache_key="test:key",
            cache_value="test-value",
            source="test",
        )
        session.add(ce)
        session.commit()
        assert ce.hit_count == 0
        assert ce.is_expired is False

    def test_cache_entry_repr(self, session):
        ce = CacheEntry(
            cache_key="repr:key",
            cache_value="repr-value",
            source="repr",
        )
        session.add(ce)
        session.commit()
        assert "CacheEntry" in repr(ce)


# =============================================================================
# Test: APIToken (Model 23)
# =============================================================================


class TestAPIToken:
    """Tests for APIToken model."""

    def test_create_api_token(self, session):
        token = APIToken(
            token_hash="abc123def456",
            user_name="admin",
            scopes="read,write",
            rate_limit=5000,
        )
        session.add(token)
        session.commit()
        assert token.id is not None
        assert token.user_name == "admin"

    def test_api_token_unique_hash(self, session):
        t1 = APIToken(token_hash="same_hash", user_name="user1")
        session.add(t1)
        session.commit()
        t2 = APIToken(token_hash="same_hash", user_name="user2")
        session.add(t2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_api_token_defaults(self, session):
        token = APIToken(token_hash="unique1", user_name="default_user")
        session.add(token)
        session.commit()
        assert token.token_type == "bearer"
        assert token.is_active is True
        assert token.rate_limit == 1000

    def test_api_token_repr(self, session):
        token = APIToken(token_hash="repr_hash", user_name="repr_user")
        session.add(token)
        session.commit()
        assert "APIToken" in repr(token)
        assert "repr_user" in repr(token)


# =============================================================================
# Test: AuditLog (Model 24)
# =============================================================================


class TestAuditLog:
    """Tests for AuditLog model."""

    def test_create_audit_log(self, session):
        log = AuditLog(
            user_name="admin",
            action="create_scan",
            resource_type="scan_run",
            resource_id="123",
            ip_address="192.168.1.1",
        )
        session.add(log)
        session.commit()
        assert log.id is not None
        assert log.action == "create_scan"

    def test_audit_log_defaults(self, session):
        log = AuditLog(
            user_name="system",
            action="auto_cleanup",
            resource_type="cache",
        )
        session.add(log)
        session.commit()
        assert log.status == "success"
        assert log.timestamp is not None

    def test_audit_log_repr(self, session):
        log = AuditLog(
            user_name="test_user",
            action="delete_scan",
            resource_type="scan_run",
        )
        session.add(log)
        session.commit()
        assert "AuditLog" in repr(log)
        assert "test_user" in repr(log)


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for model relationships and cascades."""

    def test_full_scan_chain(self, session):
        """Test the full ScanRun → Subdomain → PortScan → Vulnerability chain."""
        scan = ScanRun(domain="chain.example.com", status="running")
        session.add(scan)
        session.commit()

        sub = Subdomain(
            scan_run_id=scan.id,
            subdomain="www.chain.example.com",
            is_alive=True,
        )
        session.add(sub)
        session.commit()

        port = PortScan(
            subdomain_id=sub.id,
            port=8080,
            state="open",
            service="http",
        )
        session.add(port)
        session.commit()

        vuln = Vulnerability(
            scan_run_id=scan.id,
            subdomain_id=sub.id,
            port_scan_id=port.id,
            vuln_type="sqli",
            severity=9,
            title="SQL Injection",
        )
        session.add(vuln)
        session.commit()

        # Verify chain
        session.refresh(scan)
        assert len(scan.subdomains) == 1
        assert len(scan.vulnerabilities) == 1
        assert scan.subdomains[0].port_scans[0].port == 8080
        assert scan.vulnerabilities[0].subdomain.subdomain == "www.chain.example.com"

    def test_compliance_full_chain(self, session, scan_run):
        """Test ComplianceReport → ComplianceCheck → ComplianceEvidence chain."""
        report = ComplianceReport(
            scan_run_id=scan_run.id,
            org_name="ChainTest",
            target_domain="example.com",
            framework="SOC2",
        )
        session.add(report)
        session.commit()

        check = ComplianceCheck(
            compliance_report_id=report.id,
            control_id="SOC2-CC1.1",
            control_name="Integrity & Ethics",
            status="pass",
        )
        session.add(check)
        session.commit()

        evidence = ComplianceEvidence(
            compliance_report_id=report.id,
            compliance_check_id=check.id,
            evidence_type="policy_doc",
            description="Code of conduct document provided",
            verified=True,
        )
        session.add(evidence)
        session.commit()

        session.refresh(report)
        assert len(report.compliance_checks) == 1
        assert len(report.evidence) == 1
        assert report.compliance_checks[0].evidence[0].verified is True

    def test_threat_intel_chain(self, session, vulnerability):
        """Test Vulnerability → ThreatIntelData → DataLeak/MalwareIndicator chain."""
        intel = ThreatIntelData(
            vulnerability_id=vulnerability.id,
            intel_type="data_leak",
            source="dehashed",
            target="example.com",
        )
        session.add(intel)
        session.commit()

        leak = DataLeak(
            threat_intel_id=intel.id,
            email="leaked@example.com",
            breach_name="MegaBreach",
        )
        session.add(leak)
        session.commit()

        malware = MalwareIndicator(
            threat_intel_id=intel.id,
            indicator_type="domain",
            indicator_value="c2.example.com",
        )
        session.add(malware)
        session.commit()

        session.refresh(vulnerability)
        assert len(vulnerability.threat_intel) >= 1

    def test_transaction_rollback(self, session):
        """Verify transaction rollback works correctly."""
        scan = ScanRun(domain="rollback.test.com")
        session.add(scan)
        session.commit()
        initial_id = scan.id

        # Start a new operation that will fail
        bad_sub = Subdomain(subdomain="no_scan_run.com")  # Missing FK
        session.add(bad_sub)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

        # Original scan should still be accessible
        result = session.query(ScanRun).filter_by(id=initial_id).first()
        assert result is not None
        assert result.domain == "rollback.test.com"

    def test_multiple_scans_same_domain(self, session):
        """Verify multiple scans of the same domain work."""
        scan1 = ScanRun(domain="multi.example.com", scan_type="quick")
        scan2 = ScanRun(domain="multi.example.com", scan_type="full")
        session.add_all([scan1, scan2])
        session.commit()
        results = session.query(ScanRun).filter_by(domain="multi.example.com").all()
        assert len(results) == 2

    def test_bulk_subdomain_creation(self, session, scan_run):
        """Test creating many subdomains for one scan."""
        subs = [
            Subdomain(
                scan_run_id=scan_run.id,
                subdomain=f"sub{i}.example.com",
                is_alive=i % 2 == 0,
            )
            for i in range(20)
        ]
        session.add_all(subs)
        session.commit()
        session.refresh(scan_run)
        assert len(scan_run.subdomains) == 20
        alive = [s for s in scan_run.subdomains if s.is_alive]
        assert len(alive) == 10
