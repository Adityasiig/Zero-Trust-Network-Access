"""
CRYSTALS-Dilithium (ML-DSA) Post-Quantum Digital Signature Algorithm.

SIMULATION: This mirrors FIPS 204 output formats and sizes but uses
HMAC-SHA256 internally. Not for production cryptography.
"""
import os
import hashlib
import hmac
import time
from .constants import DILITHIUM_PARAMS, DEFAULT_DSA_PARAM


class DilithiumDSA:
    """Simulates CRYSTALS-Dilithium digital signature scheme."""

    def __init__(self, param_set: str = DEFAULT_DSA_PARAM):
        if param_set not in DILITHIUM_PARAMS:
            raise ValueError(f"Unknown parameter set: {param_set}")
        self.param_set = param_set
        self.params = DILITHIUM_PARAMS[param_set]
        self._key_store = {}

    def keygen(self) -> dict:
        """Generate a signing/verification key pair with correct FIPS 204 sizes."""
        start = time.perf_counter()

        seed = os.urandom(64)
        pk_bytes = os.urandom(self.params["public_key_size"])
        sk_bytes = os.urandom(self.params["secret_key_size"])

        key_id = hashlib.sha256(pk_bytes).hexdigest()[:16]
        self._key_store[key_id] = {
            "public_key": pk_bytes,
            "secret_key": sk_bytes,
            "seed": seed,
        }

        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "key_id": key_id,
            "public_key_hex": pk_bytes[:32].hex() + "...",
            "public_key_size": len(pk_bytes),
            "secret_key_size": len(sk_bytes),
            "param_set": self.param_set,
            "security_level": self.params["security_level"],
            "generation_time_ms": round(elapsed_ms, 3),
        }

    def sign(self, key_id: str, message: str) -> dict:
        """Sign a message using the secret key."""
        start = time.perf_counter()

        if key_id not in self._key_store:
            raise ValueError(f"Unknown key_id: {key_id}")

        sk = self._key_store[key_id]["secret_key"]
        msg_bytes = message.encode("utf-8")

        sig_core = hmac.new(sk[:32], msg_bytes, hashlib.sha512).digest()
        padding_size = self.params["signature_size"] - len(sig_core)
        sig_padding = hmac.new(sk[32:64], sig_core, hashlib.sha256).digest()
        signature = sig_core + (sig_padding * (padding_size // len(sig_padding) + 1))[:padding_size]

        self._key_store[key_id].setdefault("signatures", {})[
            hashlib.sha256(msg_bytes).hexdigest()
        ] = signature

        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "signature_hex": signature.hex(),
            "signature_size": len(signature),
            "message_hash": hashlib.sha256(msg_bytes).hexdigest(),
            "param_set": self.param_set,
            "signing_time_ms": round(elapsed_ms, 3),
        }

    def verify(self, key_id: str, message: str, signature_hex: str) -> dict:
        """Verify a signature against a message and public key."""
        start = time.perf_counter()

        if key_id not in self._key_store:
            raise ValueError(f"Unknown key_id: {key_id}")

        msg_bytes = message.encode("utf-8")
        msg_hash = hashlib.sha256(msg_bytes).hexdigest()
        stored_sigs = self._key_store[key_id].get("signatures", {})

        valid = False
        if msg_hash in stored_sigs:
            valid = stored_sigs[msg_hash].hex() == signature_hex

        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "valid": valid,
            "message_hash": msg_hash,
            "param_set": self.param_set,
            "verification_time_ms": round(elapsed_ms, 3),
        }

    def get_status(self) -> dict:
        return {
            "algorithm": "CRYSTALS-Dilithium (ML-DSA)",
            "param_set": self.param_set,
            "security_level": self.params["security_level"],
            "description": self.params["description"],
            "active_keys": len(self._key_store),
            "public_key_size": self.params["public_key_size"],
            "signature_size": self.params["signature_size"],
        }
