from pathlib import Path
from fastapi import HTTPException
from github import GithubIntegration, Github # from PyGithub library for GitHub API interactions
from github.GithubException import GithubException
from github_app.configure.config import config


class GitHubAuth:
    """Handle GitHub App authentication"""

    def __init__(self):
        """Initialize GitHub Integration."""
        self._integration = None
        self._load_integration()

    def _load_integration(self):
        """Load GitHub Integration with private key."""
        try:
            private_key = self.load_private_key()
            self._integration = GithubIntegration(
                integration_id=config.GITHUB_APP_ID,
                private_key=private_key
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize GitHub Integration: {str(e)}"
            )

    @staticmethod
    def load_private_key() -> str:
        """Load the private key from the specified file path."""
        key_path = Path(config.GITHUB_PRIVATE_KEY_PATH)
        if not key_path.exists():
            raise FileNotFoundError(f"Private key file not found: {config.GITHUB_PRIVATE_KEY_PATH}")
        return key_path.read_text()

    def generate_jwt(self) -> str:
        """Generate a JWT token for GitHub App authentication."""
        try:
            return self._integration.create_jwt()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate JWT: {str(e)}"
            )

    def get_installation_access_token(self, installation_id: int) -> str:
        """Get an installation access token for the GitHub App."""
        try:
            access_token = self._integration.get_access_token(installation_id)
            return access_token.token
        except GithubException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get access token: {e.data.get('message', str(e))}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get access token: {str(e)}"
            )

    def get_github_instance(self, installation_id: int) -> Github:
        """Get a Github instance authenticated for the installation."""
        try:
            access_token = self.get_installation_access_token(installation_id)
            return Github(access_token)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create GitHub instance: {str(e)}"
            )
