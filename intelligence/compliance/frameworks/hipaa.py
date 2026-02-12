"""HIPAA compliance framework."""
from typing import Dict, List

HIPAA_CONTROLS = {
    "164.308(a)(1)": "Security Management Process",
    "164.308(a)(5)": "Security Awareness and Training",
    "164.312(a)(1)": "Access Control",
    "164.312(b)": "Audit Controls",
    "164.312(e)(1)": "Transmission Security",
}

VULN_MAPPING = {
    "weak_cipher": ["164.312(e)(1)"], "missing_auth": ["164.312(a)(1)"],
    "unpatched": ["164.308(a)(5)"], "xss": ["164.308(a)(1)"],
}

class HIPAAFramework:
    def get_controls(self) -> Dict[str, str]: return HIPAA_CONTROLS
    def map_finding(self, vuln_type: str) -> List[str]: return VULN_MAPPING.get(vuln_type, [])
