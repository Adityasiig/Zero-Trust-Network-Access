"""NIST FIPS 203/204 parameter sets for post-quantum algorithms."""

# CRYSTALS-Kyber (ML-KEM) parameter sets per FIPS 203
KYBER_PARAMS = {
    "ML-KEM-512": {
        "security_level": 1,
        "public_key_size": 800,
        "secret_key_size": 1632,
        "ciphertext_size": 768,
        "shared_secret_size": 32,
        "description": "NIST Security Level 1 (equivalent to AES-128)",
    },
    "ML-KEM-768": {
        "security_level": 3,
        "public_key_size": 1184,
        "secret_key_size": 2400,
        "ciphertext_size": 1088,
        "shared_secret_size": 32,
        "description": "NIST Security Level 3 (equivalent to AES-192)",
    },
    "ML-KEM-1024": {
        "security_level": 5,
        "public_key_size": 1568,
        "secret_key_size": 3168,
        "ciphertext_size": 1568,
        "shared_secret_size": 32,
        "description": "NIST Security Level 5 (equivalent to AES-256)",
    },
}

# CRYSTALS-Dilithium (ML-DSA) parameter sets per FIPS 204
DILITHIUM_PARAMS = {
    "ML-DSA-44": {
        "security_level": 2,
        "public_key_size": 1312,
        "secret_key_size": 2528,
        "signature_size": 2420,
        "description": "NIST Security Level 2 (equivalent to SHA-256 collision resistance)",
    },
    "ML-DSA-65": {
        "security_level": 3,
        "public_key_size": 1952,
        "secret_key_size": 4000,
        "signature_size": 3293,
        "description": "NIST Security Level 3 (equivalent to AES-192)",
    },
    "ML-DSA-87": {
        "security_level": 5,
        "public_key_size": 2592,
        "secret_key_size": 4864,
        "signature_size": 4595,
        "description": "NIST Security Level 5 (equivalent to AES-256)",
    },
}

DEFAULT_KEM_PARAM = "ML-KEM-768"
DEFAULT_DSA_PARAM = "ML-DSA-65"
