"""Unified PQC manager handling key lifecycle and algorithm coordination."""
import time
from .kyber import KyberKEM
from .dilithium import DilithiumDSA
from .constants import KYBER_PARAMS, DILITHIUM_PARAMS


class PQCManager:
    """Manages post-quantum cryptographic operations and key rotation."""

    def __init__(self):
        self.kyber = KyberKEM("ML-KEM-768")
        self.dilithium = DilithiumDSA("ML-DSA-65")
        self.active_kem_key = None
        self.active_dsa_key = None
        self.key_rotation_count = 0
        self.created_at = time.time()
        self.last_rotation = None
        self._initialize_keys()

    def _initialize_keys(self):
        self.active_kem_key = self.kyber.keygen()
        self.active_dsa_key = self.dilithium.keygen()
        self.last_rotation = time.time()
        self.key_rotation_count += 1

    def rotate_keys(self) -> dict:
        """Generate new key pairs for both KEM and DSA."""
        self.active_kem_key = self.kyber.keygen()
        self.active_dsa_key = self.dilithium.keygen()
        self.last_rotation = time.time()
        self.key_rotation_count += 1
        return {
            "kem_key_id": self.active_kem_key["key_id"],
            "dsa_key_id": self.active_dsa_key["key_id"],
            "rotation_count": self.key_rotation_count,
        }

    def encrypt_demo(self, plaintext: str) -> dict:
        """Demo: encapsulate key and show encrypted output."""
        kem_result = self.kyber.encapsulate(self.active_kem_key["key_id"])
        sig_result = self.dilithium.sign(self.active_dsa_key["key_id"], plaintext)
        return {
            "plaintext": plaintext,
            "kem_encapsulation": kem_result,
            "digital_signature": sig_result,
            "algorithms": {
                "kem": self.kyber.param_set,
                "dsa": self.dilithium.param_set,
            },
        }

    def get_full_status(self) -> dict:
        key_age = time.time() - self.last_rotation if self.last_rotation else 0
        return {
            "kem": self.kyber.get_status(),
            "dsa": self.dilithium.get_status(),
            "active_kem_key_id": self.active_kem_key["key_id"] if self.active_kem_key else None,
            "active_dsa_key_id": self.active_dsa_key["key_id"] if self.active_dsa_key else None,
            "key_age_seconds": round(key_age, 1),
            "key_rotation_count": self.key_rotation_count,
            "uptime_seconds": round(time.time() - self.created_at, 1),
            "quantum_safe": True,
            "fips_compliant_sizes": True,
            "available_kem_params": list(KYBER_PARAMS.keys()),
            "available_dsa_params": list(DILITHIUM_PARAMS.keys()),
        }
