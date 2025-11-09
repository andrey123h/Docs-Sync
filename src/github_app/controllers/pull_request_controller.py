from fastapi import Request, Header
from github_app.handlers.pull_request_handler import PullRequestEventHandler
from github_app.services.pull_request_service import PullRequestService
from github_app.handlers.git_hub_client import GitHubClient
from github_app.security.auth import GitHubAuth


class PullRequestController:

    def __init__(self):
        auth = GitHubAuth()
        github_client = GitHubClient(auth)
        service = PullRequestService(github_client)
        self.handler = PullRequestEventHandler(service)

    async def handle_pull_request_webhook(
        self,
        request: Request,
        x_github_event: str = Header(None),
        x_hub_signature_256: str = Header(None)
    ):
        # Delegate to the handler
        return await self.handler.handle_pull_request_event(
            request, x_github_event, x_hub_signature_256
        )
