"""SOC 2 compliance framework."""
from typing import Dict, List

SOC2_CONTROLS = {
    "CC6.1": "Logical and physical access controls",
    "CC6.6": "Logical access security measures",
    "CC7.1": "System operations monitoring",
    "CC8.1": "Change management",
    "A1.1": "Availability commitments",
}

VULN_MAPPING = {
    "missing_auth": ["CC6.1", "CC6.6"], "open_port": ["CC6.6"],
    "unpatched": ["CC8.1"], "service_down": ["A1.1"],
}

class SOC2Framework:
    def get_controls(self) -> Dict[str, str]: return SOC2_CONTROLS
    def map_finding(self, vuln_type: str) -> List[str]: return VULN_MAPPING.get(vuln_type, [])
