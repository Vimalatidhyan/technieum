"""PCI-DSS 4.0 compliance framework."""
from typing import Dict, List

PCI_CONTROLS = {
    "1.1": "Establish firewall and router configuration standards",
    "1.3": "Prohibit direct public access to cardholder data environment",
    "2.1": "Change vendor-supplied defaults",
    "4.1": "Use strong cryptography for transmission of cardholder data",
    "6.2": "Ensure all components are protected from known vulnerabilities",
    "6.3": "Develop software securely",
    "8.2": "Properly identify and authenticate access to system components",
    "10.1": "Implement audit trails to link all access to system components",
    "11.2": "Scan for vulnerabilities quarterly",
    "11.3": "Perform penetration testing",
}

VULN_TYPE_MAPPING = {
    "xss": ["6.3"], "sqli": ["6.3"], "open_port": ["1.3"],
    "weak_cipher": ["4.1"], "unpatched": ["6.2"], "default_creds": ["2.1"],
    "missing_auth": ["8.2"],
}

class PCIDSSFramework:
    """PCI-DSS 4.0 compliance framework checker."""

    def get_controls(self) -> Dict[str, str]:
        return PCI_CONTROLS

    def map_finding(self, vuln_type: str) -> List[str]:
        return VULN_TYPE_MAPPING.get(vuln_type, [])

    def check_requirement(self, req_id: str, findings: List[Dict]) -> bool:
        mapped = [f for f in findings if req_id in self.map_finding(f.get("vuln_type", ""))]
        return len(mapped) == 0
