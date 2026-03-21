"""In-memory data store for the ZTNA system."""
import time
import random
import hashlib
import os


def _generate_devices():
    """Generate a realistic set of network devices."""
    device_templates = [
        {"name": "WS-ENG-001", "type": "workstation", "os": "Windows 11 Pro", "zone": "corporate", "owner": "engineer"},
        {"name": "WS-ENG-002", "type": "workstation", "os": "macOS Sonoma", "zone": "corporate", "owner": "engineer"},
        {"name": "WS-ADMIN-001", "type": "workstation", "os": "Ubuntu 24.04", "zone": "corporate", "owner": "admin"},
        {"name": "LAPTOP-ANA-001", "type": "laptop", "os": "Windows 11 Pro", "zone": "vpn", "owner": "analyst"},
        {"name": "LAPTOP-ENG-003", "type": "laptop", "os": "macOS Ventura", "zone": "vpn", "owner": "engineer"},
        {"name": "MB-GUEST-001", "type": "mobile", "os": "iOS 18", "zone": "guest", "owner": "guest"},
        {"name": "MB-ENG-002", "type": "mobile", "os": "Android 15", "zone": "corporate", "owner": "engineer"},
        {"name": "SRV-WEB-001", "type": "server", "os": "RHEL 9.3", "zone": "dmz", "owner": "admin"},
        {"name": "SRV-DB-001", "type": "server", "os": "Ubuntu 22.04", "zone": "corporate", "owner": "admin"},
        {"name": "SRV-API-001", "type": "server", "os": "Alpine Linux", "zone": "cloud", "owner": "admin"},
        {"name": "IOT-SENSOR-001", "type": "iot", "os": "RTOS", "zone": "iot", "owner": "system"},
        {"name": "IOT-SENSOR-002", "type": "iot", "os": "RTOS", "zone": "iot", "owner": "system"},
        {"name": "IOT-CAMERA-001", "type": "iot", "os": "Linux Embedded", "zone": "iot", "owner": "system"},
        {"name": "SRV-CLOUD-K8S", "type": "server", "os": "Container OS", "zone": "cloud", "owner": "admin"},
        {"name": "FW-CORE-001", "type": "firewall", "os": "FortiOS", "zone": "dmz", "owner": "admin"},
    ]

    devices = []
    for tmpl in device_templates:
        device_id = hashlib.sha256(tmpl["name"].encode()).hexdigest()[:12]
        devices.append({
            "id": device_id,
            "name": tmpl["name"],
            "type": tmpl["type"],
            "os": tmpl["os"],
            "zone": tmpl["zone"],
            "owner": tmpl["owner"],
            "ip": f"10.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "mac": ":".join(f"{random.randint(0, 255):02x}" for _ in range(6)),
            "status": random.choice(["online", "online", "online", "idle"]),
            "trust_score": random.randint(45, 95),
            "os_updated": random.random() > 0.2,
            "firewall_enabled": random.random() > 0.15,
            "encryption_enabled": random.random() > 0.1,
            "cert_valid": random.random() > 0.1,
            "mfa_enabled": tmpl["type"] not in ("iot", "firewall"),
            "auth_method": "certificate" if tmpl["type"] in ("server", "firewall") else random.choice(["mfa", "biometric", "password"]),
            "pqc_enabled": random.random() > 0.3,
            "last_seen": time.time() - random.randint(0, 3600),
            "connected_since": time.time() - random.randint(300, 86400),
        })
    return devices


def _generate_topology(devices):
    """Generate network topology nodes and edges."""
    nodes = []
    edges = []

    for device in devices:
        nodes.append({
            "id": device["id"],
            "name": device["name"],
            "type": device["type"],
            "zone": device["zone"],
            "status": device["status"],
            "trust_score": device["trust_score"],
        })

    zone_gateways = {}
    for node in nodes:
        zone = node["zone"]
        if zone not in zone_gateways:
            zone_gateways[zone] = node["id"]
        elif node["type"] in ("server", "firewall"):
            zone_gateways[zone] = node["id"]

    for node in nodes:
        gateway = zone_gateways.get(node["zone"])
        if gateway and gateway != node["id"]:
            edges.append({
                "source": node["id"],
                "target": gateway,
                "bandwidth": random.randint(10, 1000),
                "encrypted": random.random() > 0.2,
                "pqc_protected": random.random() > 0.4,
            })

    from app.policies.engine import NETWORK_ZONES
    for zone, info in NETWORK_ZONES.items():
        for allowed in info["allowed_flows"]:
            if zone in zone_gateways and allowed in zone_gateways:
                edges.append({
                    "source": zone_gateways[zone],
                    "target": zone_gateways[allowed],
                    "bandwidth": random.randint(100, 10000),
                    "encrypted": True,
                    "pqc_protected": True,
                    "is_zone_link": True,
                })

    return {"nodes": nodes, "edges": edges}


class DataStore:
    """Centralized in-memory data store."""

    def __init__(self):
        self.devices = _generate_devices()
        self.topology = _generate_topology(self.devices)
        self.threats = []
        self.events = []
        self.access_log = []
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "active_sessions": 0,
            "pqc_encryptions": 0,
            "key_rotations": 0,
            "threats_detected": 0,
        }

    def add_threat(self, threat: dict):
        threat.setdefault("timestamp", time.time())
        self.threats.append(threat)
        if len(self.threats) > 1000:
            self.threats = self.threats[-500:]
        self.stats["threats_detected"] += 1

    def add_event(self, event: dict):
        event.setdefault("timestamp", time.time())
        self.events.append(event)
        if len(self.events) > 1000:
            self.events = self.events[-500:]

    def get_recent_threats(self, limit: int = 50) -> list:
        return list(reversed(self.threats[-limit:]))

    def get_recent_events(self, limit: int = 50) -> list:
        return list(reversed(self.events[-limit:]))

    def get_dashboard_stats(self) -> dict:
        online_devices = sum(1 for d in self.devices if d["status"] in ("online", "idle"))
        avg_trust = sum(d["trust_score"] for d in self.devices) / len(self.devices) if self.devices else 0
        pqc_devices = sum(1 for d in self.devices if d.get("pqc_enabled"))

        return {
            "total_devices": len(self.devices),
            "online_devices": online_devices,
            "average_trust_score": round(avg_trust, 1),
            "pqc_enabled_devices": pqc_devices,
            "pqc_coverage_percent": round(pqc_devices / len(self.devices) * 100, 1) if self.devices else 0,
            "total_threats": len(self.threats),
            "recent_threats_1h": sum(
                1 for t in self.threats if t.get("timestamp", 0) > time.time() - 3600
            ),
            **self.stats,
        }
