from fastapi import APIRouter, Request, Header
from github_app.controllers.pull_request_controller import PullRequestController


class PullRequestRoutes:

    def __init__(self):
        self.router = APIRouter(prefix="/github/pr", tags=["pull-requests"])
        self.controller = PullRequestController()
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/events")
        async def handle_pull_request_webhook(
            request: Request,
            x_github_event: str = Header(None),
            x_hub_signature_256: str = Header(None)
        ):
            return await self.controller.handle_pull_request_webhook(
                request,
                x_github_event,
                x_hub_signature_256
            )
