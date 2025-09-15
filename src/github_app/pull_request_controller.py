from fastapi import APIRouter, Request, Header
from pull_request_handler import PullRequestHandler

class PullRequestController:
    """Controller for pull request webhook endpoint"""

    def __init__(self):
        self.router = APIRouter(prefix="/github/pr", tags=["pull-requests"])
        self.handler = PullRequestHandler()
        self._setup_routes()

    def _setup_routes(self):
        """Setup router endpoint."""
        @self.router.post("/events")
        async def handle_pull_request_webhook(
            request: Request,
            x_github_event: str = Header(None),
            x_hub_signature_256: str = Header(None)
        ):
            """Handle pull request webhook events."""
            return await self.handler.handle_pull_request_event(request, x_github_event, x_hub_signature_256)

