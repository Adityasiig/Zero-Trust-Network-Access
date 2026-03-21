"""
Network simulation engine - generates realistic security events,
trust score fluctuations, and threat scenarios.
"""
import asyncio
import random
import time
import math


THREAT_TYPES = [
    {"type": "brute_force", "severity": "high", "description": "Brute force login attempt detected"},
    {"type": "anomalous_access", "severity": "medium", "description": "Unusual access pattern detected"},
    {"type": "policy_violation", "severity": "medium", "description": "Access policy violation"},
    {"type": "zone_crossing", "severity": "high", "description": "Unauthorized network zone crossing"},
    {"type": "cert_expiry", "severity": "low", "description": "Device certificate expiring soon"},
    {"type": "data_exfiltration", "severity": "critical", "description": "Potential data exfiltration detected"},
    {"type": "malware_signature", "severity": "critical", "description": "Known malware signature detected"},
    {"type": "port_scan", "severity": "medium", "description": "Port scanning activity detected"},
    {"type": "privilege_escalation", "severity": "high", "description": "Privilege escalation attempt"},
    {"type": "suspicious_login", "severity": "low", "description": "Login from unusual location"},
]


class NetworkSimulator:
    """Simulates network activity for the ZTNA dashboard."""

    def __init__(self, store, trust_engine, pqc_manager, ws_manager):
        self.store = store
        self.trust_engine = trust_engine
        self.pqc_manager = pqc_manager
        self.ws_manager = ws_manager
        self.running = False
        self._tick = 0

    async def start(self):
        """Start all simulation loops."""
        self.running = True
        await asyncio.gather(
            self._trust_fluctuation_loop(),
            self._threat_generation_loop(),
            self._device_status_loop(),
            self._pqc_rotation_loop(),
            self._stats_broadcast_loop(),
        )

    async def stop(self):
        self.running = False

    async def _trust_fluctuation_loop(self):
        """Simulate gradual trust score changes."""
        while self.running:
            try:
                for factor_name, factor in self.trust_engine.factors.items():
                    drift = random.gauss(0, 2)
                    mean_revert = (65 - factor.value) * 0.05
                    new_val = factor.value + drift + mean_revert

                    # Occasional spikes
                    if random.random() < 0.02:
                        new_val -= random.uniform(10, 25)
                    elif random.random() < 0.01:
                        new_val += random.uniform(5, 15)

                    factor.update(new_val)

                score = self.trust_engine.compute_score()
                await self.ws_manager.broadcast({
                    "type": "trust_update",
                    "data": score,
                })

                for device in self.store.devices:
                    drift = random.gauss(0, 1.5)
                    device["trust_score"] = max(0, min(100, device["trust_score"] + drift))

            except Exception:
                pass
            await asyncio.sleep(3)

    async def _threat_generation_loop(self):
        """Generate threat events at realistic intervals."""
        while self.running:
            try:
                roll = random.random()
                if roll < 0.3:
                    severity_weights = [0.4, 0.25, 0.15, 0.1, 0.05, 0.02, 0.01, 0.05, 0.02, 0.05]
                    threat_template = random.choices(THREAT_TYPES, weights=severity_weights, k=1)[0]

                    source_device = random.choice(self.store.devices)
                    threat = {
                        "id": f"THR-{int(time.time()*1000) % 100000:05d}",
                        "type": threat_template["type"],
                        "severity": threat_template["severity"],
                        "description": threat_template["description"],
                        "source_device": source_device["name"],
                        "source_ip": source_device["ip"],
                        "source_zone": source_device["zone"],
                        "timestamp": time.time(),
                        "status": "active",
                    }
                    self.store.add_threat(threat)

                    if threat["severity"] in ("high", "critical"):
                        source_device["trust_score"] = max(
                            0, source_device["trust_score"] - random.uniform(10, 30)
                        )

                    await self.ws_manager.broadcast({
                        "type": "threat_event",
                        "data": threat,
                    })

            except Exception:
                pass
            await asyncio.sleep(random.uniform(4, 12))

    async def _device_status_loop(self):
        """Simulate device status changes."""
        while self.running:
            try:
                device = random.choice(self.store.devices)
                old_status = device["status"]

                if random.random() < 0.1:
                    device["status"] = random.choice(["offline", "idle"])
                elif device["status"] == "offline" and random.random() < 0.3:
                    device["status"] = "online"
                elif device["status"] == "idle" and random.random() < 0.5:
                    device["status"] = "online"

                if device["status"] != old_status:
                    device["last_seen"] = time.time()
                    await self.ws_manager.broadcast({
                        "type": "device_status",
                        "data": {
                            "device_id": device["id"],
                            "name": device["name"],
                            "old_status": old_status,
                            "new_status": device["status"],
                            "trust_score": device["trust_score"],
                        },
                    })

            except Exception:
                pass
            await asyncio.sleep(random.uniform(5, 15))

    async def _pqc_rotation_loop(self):
        """Periodically rotate PQC keys."""
        while self.running:
            await asyncio.sleep(300)
            try:
                result = self.pqc_manager.rotate_keys()
                self.store.stats["key_rotations"] += 1
                self.store.add_event({
                    "type": "pqc_key_rotation",
                    "detail": f"Automatic key rotation #{result['rotation_count']}",
                    "severity": "info",
                })
                await self.ws_manager.broadcast({
                    "type": "pqc_rotation",
                    "data": result,
                })
            except Exception:
                pass

    async def _stats_broadcast_loop(self):
        """Broadcast aggregated stats periodically."""
        while self.running:
            try:
                stats = self.store.get_dashboard_stats()
                trust = self.trust_engine.compute_score()
                pqc = self.pqc_manager.get_full_status()
                await self.ws_manager.broadcast({
                    "type": "stats_update",
                    "data": {
                        "stats": stats,
                        "trust": trust,
                        "pqc": {
                            "key_age": pqc["key_age_seconds"],
                            "rotation_count": pqc["key_rotation_count"],
                            "quantum_safe": pqc["quantum_safe"],
                        },
                        "connections": self.ws_manager.connection_count,
                    },
                })
            except Exception:
                pass
            await asyncio.sleep(5)
