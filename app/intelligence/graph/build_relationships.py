"""Extract relationships from scan data for graph construction."""
from typing import Any, Dict, List


def build_relationships(scan_data: Dict[str, Any]) -> List[Dict]:
    """Extract all relationships from scan data as edges."""
    edges: List[Dict] = []
    domain = scan_data.get("domain", "")

    # Domain -> Subdomain
    for sub in scan_data.get("subdomains", []):
        edges.append({"source": domain, "source_type": "domain", "target": sub, "target_type": "subdomain", "relationship": "parent_domain", "weight": 1.0})

    # DNS records
    for dns in scan_data.get("dns_records", []):
        edges.append({"source": dns.get("domain", domain), "source_type": "domain", "target": dns.get("value", ""), "target_type": "ip" if dns.get("record_type") == "A" else "domain", "relationship": f"dns_{dns.get('record_type', 'unknown').lower()}", "weight": 1.0})

    # Subdomain -> Port (services)
    for port in scan_data.get("ports", []):
        edges.append({"source": port.get("subdomain", ""), "source_type": "subdomain", "target": str(port.get("port", "")), "target_type": "port", "relationship": "listening_port", "weight": 1.0})

    # Port -> Vulnerability
    for vuln in scan_data.get("vulnerabilities", []):
        if vuln.get("port"):
            edges.append({"source": str(vuln["port"]), "source_type": "port", "target": vuln.get("title", ""), "target_type": "vulnerability", "relationship": "vulnerable_to", "weight": min(1.0, (vuln.get("severity") or 50) / 100)})

    return edges
