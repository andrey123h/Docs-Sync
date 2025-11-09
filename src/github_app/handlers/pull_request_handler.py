from fastapi import Request, HTTPException
from typing import Dict, Any
from github_app.security.webhook_security import WebhookSecurity
from github_app.services.pull_request_service import PullRequestService


class PullRequestEventHandler:
    """Entrypoint for handling opened pull request webhook events"""

    def __init__(self, service: PullRequestService):
        self.service = service

    async def handle_pull_request_event(
        self,
        request: Request,
        x_github_event: str,
        x_hub_signature_256: str
    ) -> Dict[str, Any]:

        body = await request.body()
        WebhookSecurity.verify_signature(body, x_hub_signature_256)

        if x_github_event != "pull_request":
            return {"message": f"Event {x_github_event} not handled by this endpoint"}
        try:
            event_data = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        action = event_data.get("action")
        if action == "opened":
            # delegate to service layer
            return await self.service.process_opened(event_data)

        return {"message": f"Pull request {action} event received but not processed"}
