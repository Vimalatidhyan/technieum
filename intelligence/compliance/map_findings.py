"""Map security findings to compliance framework requirements."""
from typing import Dict, List
import logging

from intelligence.compliance.frameworks.pci_dss import PCIDSSFramework
from intelligence.compliance.frameworks.hipaa import HIPAAFramework
from intelligence.compliance.frameworks.gdpr import GDPRFramework
from intelligence.compliance.frameworks.soc2 import SOC2Framework
from intelligence.compliance.frameworks.nist_csf import NISTCSFFramework

logger = logging.getLogger(__name__)

FRAMEWORKS = {
    "pci": PCIDSSFramework,
    "hipaa": HIPAAFramework,
    "gdpr": GDPRFramework,
    "soc2": SOC2Framework,
    "nist": NISTCSFFramework,
}


def map_findings_to_compliance(
    findings: List[Dict],
    frameworks: List[str],
    config: Dict = None,
) -> Dict[str, Dict]:
    """Map security findings to compliance framework requirements."""
    results: Dict[str, Dict] = {}

    for fw_name in frameworks:
        fw_cls = FRAMEWORKS.get(fw_name.lower())
        if not fw_cls:
            logger.warning(f"Unknown framework: {fw_name}")
            continue

        fw = fw_cls()
        controls = fw.get_controls()
        control_status: Dict[str, Dict] = {}

        for ctrl_id, ctrl_name in controls.items():
            mapped_findings = []
            for finding in findings:
                if ctrl_id in fw.map_finding(finding.get("vuln_type", "")):
                    mapped_findings.append(finding.get("id", 0))
            control_status[ctrl_id] = {
                "name": ctrl_name,
                "status": "fail" if mapped_findings else "pass",
                "findings": mapped_findings,
                "remediation": f"Remediate findings: {mapped_findings}" if mapped_findings else "No action needed",
            }

        passed = sum(1 for v in control_status.values() if v["status"] == "pass")
        total = len(control_status)
        results[fw_name] = {
            "controls": control_status,
            "overall_compliance": round((passed / total) * 100) if total else 100,
            "passed": passed,
            "failed": total - passed,
            "total": total,
        }
        logger.info(f"{fw_name}: {passed}/{total} controls passing ({results[fw_name]['overall_compliance']}%)")

    return results
