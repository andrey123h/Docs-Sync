import hmac
import hashlib
from fastapi import HTTPException
from config import config

class WebhookSecurity:
    """Handle webhook security and signature verification."""

    @staticmethod
    def verify_signature(payload: bytes, signature: str) -> None:
        """Verify the webhook signature to ensure the request is from GitHub.
         Verifies that incoming webhook requests are authentic and originate from GitHub. It implements HMAC-SHA256
        signature verification using a shared secret configured in the application settings: GITHUB_WEBHOOK_SECRET."""

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

        # Compare signatures
        if not hmac.compare_digest(expected_signature, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

