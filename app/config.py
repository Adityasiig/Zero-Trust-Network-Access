"""Application configuration."""
import os

SECRET_KEY = os.getenv("SECRET_KEY", "ztna-pqc-demo-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
TRUST_SCORE_THRESHOLD = 40
TRUST_WARNING_THRESHOLD = 60
TRUST_EVAL_INTERVAL = 30  # seconds
PQC_KEY_ROTATION_INTERVAL = 300  # seconds
SIMULATION_SPEED = 1.0  # multiplier for event generation
