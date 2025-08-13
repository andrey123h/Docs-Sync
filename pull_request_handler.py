import requests
from fastapi import APIRouter, Request, Header, HTTPException
from typing import Dict, Any
from github.GithubException import GithubException
from webhook_security import WebhookSecurity
from auth import GitHubAuth
from config import config

class PullRequestHandler:
    """Handler for pull request events"""

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

            # Validate required data
            if not all([installation_id, owner, repo, pr_number]):
                raise HTTPException(
                    status_code=400,
                    detail="Missing required data: installation_id, owner, repo, or pr_number"
                )

            # Post comment to PR
            comment_body = "👋 Hello from Docs-Sync! Your PR has been received."
            comment_url = await self.post_pr_comment(installation_id, owner, repo, pr_number, comment_body)

            return {
                "message": "Comment posted successfully",
                "installation_id": installation_id,
                "repository": f"{owner}/{repo}",
                "pr_number": pr_number,
                "comment_url": comment_url
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
    ) -> str:
        """Post a comment to a pull request"""
        try:
            # Get authenticated GitHub instance
            github = self.auth.get_github_instance(installation_id)

            # Get the repository
            repository = github.get_repo(f"{owner}/{repo}")

            # Get the pull request (issue in GitHub API terms)
            pull_request = repository.get_issue(pr_number)

            # Create the comment
            comment = pull_request.create_comment(body)

            return comment.html_url

        except GithubException as e:
            error_message = e.data.get('message', str(e)) if hasattr(e, 'data') and e.data else str(e)
            raise HTTPException(
                status_code=e.status if hasattr(e, 'status') else 500,
                detail=f"GitHub API error: {error_message}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error posting comment to PR: {str(e)}"
            )

