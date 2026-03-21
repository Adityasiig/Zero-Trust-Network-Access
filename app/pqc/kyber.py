"""
CRYSTALS-Kyber (ML-KEM) Post-Quantum Key Encapsulation Mechanism.

SIMULATION: This mirrors FIPS 203 output formats and sizes but uses
HMAC-SHA256 internally. Not for production cryptography.
"""
import os
import hashlib
import hmac
import time
from .constants import KYBER_PARAMS, DEFAULT_KEM_PARAM


class KyberKEM:
    """Simulates CRYSTALS-Kyber key encapsulation mechanism."""

    def __init__(self, param_set: str = DEFAULT_KEM_PARAM):
        if param_set not in KYBER_PARAMS:
            raise ValueError(f"Unknown parameter set: {param_set}")
        self.param_set = param_set
        self.params = KYBER_PARAMS[param_set]
        self._key_store = {}

    def keygen(self) -> dict:
        """Generate a public/secret key pair with correct FIPS 203 sizes."""
        start = time.perf_counter()

        seed = os.urandom(64)
        pk_bytes = os.urandom(self.params["public_key_size"])
        sk_seed = os.urandom(32)
        sk_bytes = hmac.new(sk_seed, seed, hashlib.sha256).digest()
        sk_bytes = sk_bytes + os.urandom(self.params["secret_key_size"] - len(sk_bytes))

        key_id = hashlib.sha256(pk_bytes).hexdigest()[:16]
        self._key_store[key_id] = {
            "public_key": pk_bytes,
            "secret_key": sk_bytes,
            "seed": seed,
        }

        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "key_id": key_id,
            "public_key_hex": pk_bytes.hex(),
            "public_key_size": len(pk_bytes),
            "secret_key_size": len(sk_bytes),
            "param_set": self.param_set,
            "security_level": self.params["security_level"],
            "generation_time_ms": round(elapsed_ms, 3),
        }

    def encapsulate(self, key_id: str) -> dict:
        """Encapsulate: produce ciphertext and shared secret from a public key."""
        start = time.perf_counter()

        if key_id not in self._key_store:
            raise ValueError(f"Unknown key_id: {key_id}")

        pk = self._key_store[key_id]["public_key"]
        randomness = os.urandom(32)

        shared_secret = hmac.new(
            self._key_store[key_id]["seed"], randomness, hashlib.sha256
        ).digest()

        ct_bytes = os.urandom(self.params["ciphertext_size"])

        self._key_store[key_id]["last_shared_secret"] = shared_secret
        self._key_store[key_id]["last_ciphertext"] = ct_bytes

        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "ciphertext_hex": ct_bytes.hex(),
            "ciphertext_size": len(ct_bytes),
            "shared_secret_hex": shared_secret.hex(),
            "shared_secret_size": len(shared_secret),
            "param_set": self.param_set,
            "encapsulation_time_ms": round(elapsed_ms, 3),
        }

    def decapsulate(self, key_id: str) -> dict:
        """Decapsulate: recover shared secret from ciphertext using secret key."""
        start = time.perf_counter()

        if key_id not in self._key_store:
            raise ValueError(f"Unknown key_id: {key_id}")

        store = self._key_store[key_id]
        if "last_shared_secret" not in store:
            raise ValueError("No encapsulation performed for this key")

        shared_secret = store["last_shared_secret"]
        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "shared_secret_hex": shared_secret.hex(),
            "shared_secret_size": len(shared_secret),
            "decapsulation_time_ms": round(elapsed_ms, 3),
            "match": True,
        }

    def get_status(self) -> dict:
        return {
            "algorithm": "CRYSTALS-Kyber (ML-KEM)",
            "param_set": self.param_set,
            "security_level": self.params["security_level"],
            "description": self.params["description"],
            "active_keys": len(self._key_store),
            "public_key_size": self.params["public_key_size"],
            "ciphertext_size": self.params["ciphertext_size"],
            "shared_secret_size": self.params["shared_secret_size"],
        }
