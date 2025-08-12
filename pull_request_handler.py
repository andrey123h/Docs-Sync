import requests
from fastapi import APIRouter, Request, Header, HTTPException
from typing import Dict, Any
from webhook_security import WebhookSecurity
from auth import GitHubAuth
from config import config

class PullRequestHandler:
    """Handler for pull request webhook events."""

    def __init__(self):
        self.router = APIRouter(prefix="/pr", tags=["pull-requests"])
        self.auth = GitHubAuth()
        self._setup_routes()

    def _setup_routes(self):
        """Setup router endpoints."""
        @self.router.post("/webhook")
        async def handle_pull_request_webhook(
            request: Request,
            x_github_event: str = Header(None),
            x_hub_signature_256: str = Header(None)
        ):
            """Handle pull request webhook events."""
            return await self._handle_pull_request_event(request, x_github_event, x_hub_signature_256)

    async def _handle_pull_request_event(
        self,
        request: Request,
        x_github_event: str,
        x_hub_signature_256: str
    ) -> Dict[str, Any]:
        """Process pull request webhook event."""
        # Get raw body for signature verification
        body = await request.body()

        # Verify webhook signature
        WebhookSecurity.verify_signature(body, x_hub_signature_256)

        # Only handle pull_request events
        if x_github_event != "pull_request":
            return {"message": f"Event {x_github_event} not handled by this endpoint"}

        # Parse the JSON body
        try:
            event_data = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # Extract event details
        action = event_data.get("action")

        # Only process opened pull requests
        if action == "opened":
            installation_id = event_data.get("installation", {}).get("id")
            repository = event_data.get("repository", {})
            pull_request = event_data.get("pull_request", {})

            owner = repository.get("owner", {}).get("login")
            repo = repository.get("name")
            pr_number = pull_request.get("number")

            # Post comment to PR
            comment_body = "👋 Hello from Docs-Sync! Your PR has been received."
            await self.post_pr_comment(installation_id, owner, repo, pr_number, comment_body)

            return {
                "message": "Comment posted successfully",
                "installation_id": installation_id,
                "repository": f"{owner}/{repo}",
                "pr_number": pr_number
            }

        return {
            "message": f"Pull request {action} event received but not processed",
            "action": action
        }

    async def post_pr_comment(
        self,
        installation_id: int,
        owner: str,
        repo: str,
        pr_number: int,
        body: str
    ) -> None:
        """Post a comment to a pull request."""
        try:
            # Get installation access token
            token = self.auth.get_installation_access_token(installation_id)

            # Prepare headers
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": config.GITHUB_API_VERSION
            }

            # Post comment
            url = f"{config.GITHUB_API_BASE_URL}/repos/{owner}/{repo}/issues/{pr_number}/comments"
            payload = {"body": body}

            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 201:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to post comment: {response.text}"
                )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error posting comment to PR: {str(e)}"
            )

