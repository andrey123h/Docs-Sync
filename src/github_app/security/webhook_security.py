import hmac
import hashlib
from fastapi import HTTPException
from configure.config import Config


class WebhookSecurity:
    """Handle webhook security and signature verification."""

    @staticmethod
    def verify_signature(payload: bytes, signature: str) -> None:
        """Verify incoming webhook requests with HMAC-SHA256 signature check."""

        if not signature:
            raise HTTPException(status_code=401, detail="Missing signature")

        if signature.startswith("sha256="):
            signature = signature[7:]


        secret = Config.GITHUB_WEBHOOK_SECRET

        expected_signature = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
