from fastapi import Request, HTTPException
from typing import Dict, Any
from github_app.security.webhook_security import WebhookSecurity
from github_app.handlers.pull_request_service import PullRequestService


class PullRequestEventHandler:
    """Entrypoint for handling pull request webhook events"""

    def __init__(self, service: PullRequestService):
        self.service = service

    async def handle_pull_request_event(
        self,
        request: Request,
        x_github_event: str,
        x_hub_signature_256: str
    ) -> Dict[str, Any]:
        """Process pull request webhook event."""
        # Verify GitHub signature
        body = await request.body()
        WebhookSecurity.verify_signature(body, x_hub_signature_256)

        # Only handle pull_request events
        if x_github_event != "pull_request":
            return {"message": f"Event {x_github_event} not handled by this endpoint"}

        # Parse request body
        try:
            event_data = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # Handle pull request opened action
        action = event_data.get("action")
        if action == "opened":
            return await self.service.process_opened(event_data)

        return {"message": f"Pull request {action} event received but not processed"}
