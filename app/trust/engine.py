"""
Zero Trust Score Computation Engine.
Calculates composite trust scores using weighted factors.
"""
import time
import math


class TrustFactor:
    """Individual trust factor with weight and current value."""

    def __init__(self, name: str, weight: float, value: float = 50.0):
        self.name = name
        self.weight = weight
        self.value = max(0, min(100, value))
        self.history = []

    def update(self, new_value: float):
        self.history.append({"value": self.value, "timestamp": time.time()})
        if len(self.history) > 100:
            self.history = self.history[-50:]
        self.value = max(0, min(100, new_value))

    def to_dict(self):
        return {
            "name": self.name,
            "weight": self.weight,
            "value": round(self.value, 1),
            "weighted_score": round(self.value * self.weight, 1),
        }


class TrustEngine:
    """Computes and manages trust scores for devices and sessions."""

    def __init__(self):
        self.factors = {
            "device_posture": TrustFactor("Device Posture", 0.25, 75),
            "auth_strength": TrustFactor("Authentication Strength", 0.20, 80),
            "behavior": TrustFactor("Behavioral Score", 0.20, 70),
            "network_context": TrustFactor("Network Context", 0.15, 65),
            "time_factor": TrustFactor("Time Factor", 0.10, 85),
            "pqc_compliance": TrustFactor("PQC Compliance", 0.10, 90),
        }
        self.session_scores = {}

    def compute_score(self, session_id: str = None, overrides: dict = None) -> dict:
        """Compute weighted trust score."""
        factors = {}
        for key, factor in self.factors.items():
            val = overrides.get(key, factor.value) if overrides else factor.value
            factors[key] = {"value": val, "weight": factor.weight}

        total = sum(f["value"] * f["weight"] for f in factors.values())
        total = max(0, min(100, total))

        if total >= 80:
            risk_level = "low"
        elif total >= 60:
            risk_level = "medium"
        elif total >= 40:
            risk_level = "high"
        else:
            risk_level = "critical"

        result = {
            "trust_score": round(total, 1),
            "risk_level": risk_level,
            "factors": {k: v for k, v in factors.items()},
            "timestamp": time.time(),
        }

        if session_id:
            self.session_scores[session_id] = result

        return result

    def update_factor(self, factor_name: str, value: float):
        if factor_name in self.factors:
            self.factors[factor_name].update(value)

    def get_all_factors(self) -> list:
        return [f.to_dict() for f in self.factors.values()]

    def evaluate_device(self, device: dict) -> dict:
        """Evaluate trust based on device attributes."""
        score = 50.0
        details = []

        if device.get("os_updated", False):
            score += 10
            details.append("OS is up to date (+10)")
        else:
            score -= 10
            details.append("OS is outdated (-10)")

        if device.get("firewall_enabled", False):
            score += 8
            details.append("Firewall enabled (+8)")

        if device.get("encryption_enabled", False):
            score += 8
            details.append("Disk encryption enabled (+8)")

        if device.get("cert_valid", False):
            score += 12
            details.append("Valid device certificate (+12)")
        else:
            score -= 15
            details.append("Invalid/missing certificate (-15)")

        if device.get("mfa_enabled", False):
            score += 12
            details.append("MFA enabled (+12)")

        auth_method = device.get("auth_method", "password")
        auth_scores = {"certificate": 15, "biometric": 12, "mfa": 10, "password": 0}
        score += auth_scores.get(auth_method, 0)
        details.append(f"Auth method: {auth_method} (+{auth_scores.get(auth_method, 0)})")

        score = max(0, min(100, score))

        return {
            "device_trust_score": round(score, 1),
            "details": details,
            "risk_level": "low" if score >= 70 else "medium" if score >= 50 else "high",
        }
