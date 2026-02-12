"""GDPR compliance framework."""
from typing import Dict, List

GDPR_CONTROLS = {
    "Art.25": "Data protection by design and default",
    "Art.32": "Security of processing",
    "Art.33": "Notification of personal data breach",
    "Art.35": "Data protection impact assessment",
}

VULN_MAPPING = {
    "data_exposure": ["Art.32", "Art.33"], "weak_cipher": ["Art.32"],
    "xss": ["Art.25"], "sqli": ["Art.32"],
}

class GDPRFramework:
    def get_controls(self) -> Dict[str, str]: return GDPR_CONTROLS
    def map_finding(self, vuln_type: str) -> List[str]: return VULN_MAPPING.get(vuln_type, [])
