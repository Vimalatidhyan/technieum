"""NIST CSF 2.0 compliance framework."""
from typing import Dict, List

NIST_CONTROLS = {
    "GV.OC": "Organizational Context",
    "ID.AM": "Asset Management",
    "PR.AC": "Identity Management and Access Control",
    "PR.DS": "Data Security",
    "DE.CM": "Continuous Monitoring",
    "RS.RP": "Incident Management",
    "RC.RP": "Incident Recovery Plan",
}

VULN_MAPPING = {
    "open_port": ["ID.AM", "PR.AC"], "weak_cipher": ["PR.DS"],
    "unpatched": ["DE.CM"], "missing_auth": ["PR.AC"],
}

class NISTCSFFramework:
    def get_controls(self) -> Dict[str, str]: return NIST_CONTROLS
    def map_finding(self, vuln_type: str) -> List[str]: return VULN_MAPPING.get(vuln_type, [])
