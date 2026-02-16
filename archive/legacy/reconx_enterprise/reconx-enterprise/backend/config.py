"""Environment configuration for ReconX Enterprise."""
import os


class Config:
    """Application configuration from environment variables."""

    DATABASE_PATH = os.getenv("DATABASE_PATH", "./reconx.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
    API_KEY_HASH_ALGORITHM = "sha256"
    RATE_LIMIT_REQUESTS_PER_HOUR = int(os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR", "1000"))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
    SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")
    DEHASHED_EMAIL = os.getenv("DEHASHED_EMAIL", "")
    DEHASHED_API_KEY = os.getenv("DEHASHED_API_KEY", "")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
