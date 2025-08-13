import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""

    # GitHub App credentials
    GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
    GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

    # API settings
    GITHUB_API_BASE_URL = "https://api.github.com"
    GITHUB_API_VERSION = "2022-11-28"

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        required_vars = [
            "GITHUB_APP_ID",
            "GITHUB_PRIVATE_KEY_PATH",
            "GITHUB_WEBHOOK_SECRET"
        ]

        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Validate private key file exists
        key_path = Path(cls.GITHUB_PRIVATE_KEY_PATH)
        if not key_path.exists():
            raise FileNotFoundError(f"Private key file not found: {cls.GITHUB_PRIVATE_KEY_PATH}")

config = Config()

