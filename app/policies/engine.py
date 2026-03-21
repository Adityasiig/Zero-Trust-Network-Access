"""
Zero Trust Policy Engine - RBAC + ABAC access control with micro-segmentation.
"""
import time


DEFAULT_POLICIES = [
    {
        "id": "POL-001",
        "name": "Engineering Database Access",
        "resource": "/api/data/engineering-db",
        "conditions": {
            "roles": ["engineer", "admin"],
            "min_trust_score": 75,
            "required_zones": ["corporate", "vpn"],
            "require_mfa": True,
            "require_pqc": True,
        },
        "action": "allow",
        "priority": 1,
        "enabled": True,
    },
    {
        "id": "POL-002",
        "name": "Public API Access",
        "resource": "/api/public/*",
        "conditions": {
            "roles": ["engineer", "analyst", "admin", "guest"],
            "min_trust_score": 30,
            "required_zones": ["corporate", "vpn", "guest"],
            "require_mfa": False,
            "require_pqc": False,
        },
        "action": "allow",
        "priority": 5,
        "enabled": True,
    },
    {
        "id": "POL-003",
        "name": "Admin Console Access",
        "resource": "/admin/*",
        "conditions": {
            "roles": ["admin"],
            "min_trust_score": 85,
            "required_zones": ["corporate"],
            "require_mfa": True,
            "require_pqc": True,
        },
        "action": "allow",
        "priority": 1,
        "enabled": True,
    },
    {
        "id": "POL-004",
        "name": "IoT Sensor Data",
        "resource": "/api/data/iot-sensors",
        "conditions": {
            "roles": ["engineer", "analyst", "admin"],
            "min_trust_score": 50,
            "required_zones": ["corporate", "vpn", "iot"],
            "require_mfa": False,
            "require_pqc": True,
        },
        "action": "allow",
        "priority": 3,
        "enabled": True,
    },
    {
        "id": "POL-005",
        "name": "Restricted Lab Access",
        "resource": "/api/data/restricted-lab",
        "conditions": {
            "roles": ["admin"],
            "min_trust_score": 90,
            "required_zones": ["restricted"],
            "require_mfa": True,
            "require_pqc": True,
        },
        "action": "allow",
        "priority": 1,
        "enabled": True,
    },
    {
        "id": "POL-006",
        "name": "Cloud Services Gateway",
        "resource": "/api/cloud/*",
        "conditions": {
            "roles": ["engineer", "admin"],
            "min_trust_score": 65,
            "required_zones": ["corporate", "vpn", "cloud"],
            "require_mfa": True,
            "require_pqc": True,
        },
        "action": "allow",
        "priority": 2,
        "enabled": True,
    },
]

NETWORK_ZONES = {
    "corporate": {
        "name": "Corporate LAN",
        "isolation_level": "medium",
        "allowed_flows": ["dmz", "cloud", "vpn"],
        "color": "#00d4ff",
    },
    "dmz": {
        "name": "DMZ",
        "isolation_level": "high",
        "allowed_flows": ["corporate", "cloud"],
        "color": "#ffaa00",
    },
    "guest": {
        "name": "Guest WiFi",
        "isolation_level": "high",
        "allowed_flows": ["dmz"],
        "color": "#ff3366",
    },
    "iot": {
        "name": "IoT Segment",
        "isolation_level": "very_high",
        "allowed_flows": ["corporate"],
        "color": "#aa66ff",
    },
    "cloud": {
        "name": "Cloud Services",
        "isolation_level": "medium",
        "allowed_flows": ["corporate", "dmz", "vpn"],
        "color": "#00ff88",
    },
    "restricted": {
        "name": "Restricted Lab",
        "isolation_level": "maximum",
        "allowed_flows": [],
        "color": "#ff0044",
    },
    "vpn": {
        "name": "VPN Tunnel",
        "isolation_level": "medium",
        "allowed_flows": ["corporate", "cloud"],
        "color": "#44aaff",
    },
}


class PolicyEngine:
    """Evaluates access requests against Zero Trust policies."""

    def __init__(self):
        self.policies = list(DEFAULT_POLICIES)
        self.zones = dict(NETWORK_ZONES)
        self.evaluation_log = []

    def evaluate(self, request: dict) -> dict:
        """Evaluate an access request against all matching policies."""
        resource = request.get("resource", "")
        role = request.get("role", "guest")
        trust_score = request.get("trust_score", 0)
        zone = request.get("zone", "guest")
        has_mfa = request.get("has_mfa", False)
        has_pqc = request.get("has_pqc", False)

        matching_policies = []
        for policy in self.policies:
            if not policy["enabled"]:
                continue
            if self._resource_matches(policy["resource"], resource):
                matching_policies.append(policy)

        matching_policies.sort(key=lambda p: p["priority"])

        if not matching_policies:
            result = {
                "decision": "deny",
                "reason": "No matching policy found",
                "resource": resource,
                "timestamp": time.time(),
            }
            self.evaluation_log.append(result)
            return result

        for policy in matching_policies:
            conds = policy["conditions"]
            failures = []

            if role not in conds.get("roles", []):
                failures.append(f"Role '{role}' not authorized")
            if trust_score < conds.get("min_trust_score", 0):
                failures.append(
                    f"Trust score {trust_score} below minimum {conds['min_trust_score']}"
                )
            if zone not in conds.get("required_zones", []):
                failures.append(f"Zone '{zone}' not permitted")
            if conds.get("require_mfa") and not has_mfa:
                failures.append("MFA required but not present")
            if conds.get("require_pqc") and not has_pqc:
                failures.append("PQC encryption required")

            result = {
                "decision": "allow" if not failures else "deny",
                "policy_id": policy["id"],
                "policy_name": policy["name"],
                "resource": resource,
                "failures": failures,
                "conditions_met": len(conds) - len(failures),
                "conditions_total": len(
                    [v for v in conds.values() if v not in (False, None)]
                ),
                "timestamp": time.time(),
            }
            self.evaluation_log.append(result)
            if len(self.evaluation_log) > 500:
                self.evaluation_log = self.evaluation_log[-250:]
            return result

        return {"decision": "deny", "reason": "Default deny"}

    def _resource_matches(self, pattern: str, resource: str) -> bool:
        if pattern.endswith("/*"):
            return resource.startswith(pattern[:-2])
        return pattern == resource

    def get_policies(self) -> list:
        return self.policies

    def get_zones(self) -> dict:
        return self.zones

    def get_recent_evaluations(self, limit: int = 20) -> list:
        return list(reversed(self.evaluation_log[-limit:]))
