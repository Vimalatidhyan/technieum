"""Alert generator for change detection events."""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

ALERT_TYPES = {
    "CRITICAL_FINDING_NEW": "New critical/high vulnerability discovered",
    "SERVICE_DOWN": "Previously active service is now down",
    "MASS_ASSET_CHURN": "Large number of assets added or removed",
    "CONFIGURATION_DRIFT": "Technology or service configuration changed",
    "COMPLIANCE_DEGRADATION": "New findings affecting compliance posture",
}

class AlertGenerator:
    """Generate security alerts from scan delta data."""

    def __init__(self, delta: Dict, scan_run_id: int, thresholds: Dict = None) -> None:
        self.delta = delta
        self.scan_run_id = scan_run_id
        self.thresholds = thresholds or {"mass_churn": 10, "critical_severity": 90}

    def generate_alerts(self) -> List[Dict]:
        """Generate alerts based on configured thresholds."""
        alerts = []
        for vuln in self.delta.get("new_vulnerabilities", []):
            if (vuln.get("severity") or 0) >= self.thresholds["critical_severity"]:
                alerts.append({"type": "CRITICAL_FINDING_NEW", "severity": "critical", "data": vuln})

        summary = self.delta.get("summary", {})
        if summary.get("assets_added", 0) + summary.get("assets_removed", 0) >= self.thresholds["mass_churn"]:
            alerts.append({"type": "MASS_ASSET_CHURN", "severity": "high", "data": summary})

        logger.info(f"Generated {len(alerts)} alerts for scan {self.scan_run_id}")
        return alerts

    def should_alert(self, event_type: str, data: Dict) -> bool:
        """Check if an event meets alert threshold."""
        if event_type == "CRITICAL_FINDING_NEW":
            return (data.get("severity") or 0) >= self.thresholds["critical_severity"]
        if event_type == "MASS_ASSET_CHURN":
            return (data.get("assets_added", 0) + data.get("assets_removed", 0)) >= self.thresholds["mass_churn"]
        return True
