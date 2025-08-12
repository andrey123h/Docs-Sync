import hmac
import hashlib
from fastapi import HTTPException
from config import config

class WebhookSecurity:
    """Handle webhook security and signature verification."""

    @staticmethod
    def verify_signature(payload: bytes, signature: str) -> None:
        """Verify the webhook signature to ensure the request is from GitHub."""
        if not config.GITHUB_WEBHOOK_SECRET:
            raise HTTPException(status_code=500, detail="Webhook secret not configured")

        if not signature:
            raise HTTPException(status_code=401, detail="Missing signature")

        # Remove 'sha256=' prefix if present
        if signature.startswith('sha256='):
            signature = signature[7:]

        # Create HMAC signature
        expected_signature = hmac.new(
            config.GITHUB_WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Compare signatures securely
        if not hmac.compare_digest(expected_signature, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

