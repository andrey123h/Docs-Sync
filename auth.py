import time
import jwt
import requests
from pathlib import Path
from fastapi import HTTPException
from config import config

class GitHubAuth:
    """Handle GitHub App authentication."""

    @staticmethod
    def load_private_key() -> str:
        """Load the private key from the specified file path."""
        key_path = Path(config.GITHUB_PRIVATE_KEY_PATH)
        if not key_path.exists():
            raise FileNotFoundError(f"Private key file not found: {config.GITHUB_PRIVATE_KEY_PATH}")
        return key_path.read_text()

    @staticmethod
    def generate_jwt() -> str:
        """Generate a JWT token for GitHub App authentication."""
        private_key = GitHubAuth.load_private_key()
        payload = {
            "iat": int(time.time()) - 60,
            "exp": int(time.time()) + (10 * 60),
            "iss": config.GITHUB_APP_ID
        }
        return jwt.encode(payload, private_key, algorithm="RS256")

    @staticmethod
    def get_installation_access_token(installation_id: int) -> str:
        """Get an installation access token for the GitHub App."""
        jwt_token = GitHubAuth.generate_jwt()
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": config.GITHUB_API_VERSION
        }
        url = f"{config.GITHUB_API_BASE_URL}/app/installations/{installation_id}/access_tokens"
        response = requests.post(url, headers=headers)

        if response.status_code != 201:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get access token: {response.text}"
            )
        return response.json()["token"]

