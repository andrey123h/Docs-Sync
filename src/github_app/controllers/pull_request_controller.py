from fastapi import APIRouter, Request, Header
from github_app.handlers.pull_request_handler import PullRequestEventHandler
from services.pull_request_service import PullRequestService
from github_app.handlers.git_hub_client import GitHubClient
from github_app.security.auth import GitHubAuth


class PullRequestController:
    """Controller for pull request webhook endpoint"""

    def __init__(self):
        self.router = APIRouter(prefix="/github/pr", tags=["pull-requests"])

        # Build dependency chain
        auth = GitHubAuth()
        github_client = GitHubClient(auth)
        service = PullRequestService(github_client)
        self.handler = PullRequestEventHandler(service)

        self._setup_routes()

    def _setup_routes(self):
        """Setup router endpoint.
        Registers the POST endpoint at '/github/pr/events' that receives and processes
        GitHub webhook events. Extracts required headers for event type
        identification and signature verification."""

        @self.router.post("/events")
        async def handle_pull_request_webhook(
            request: Request,
            x_github_event: str = Header(None), # GitHub event type
            x_hub_signature_256: str = Header(None) # HMAC SHA-256 signature for verification
        ):
            """Handle pull request webhook events."""
            return await self.handler.handle_pull_request_event(request, x_github_event, x_hub_signature_256)

