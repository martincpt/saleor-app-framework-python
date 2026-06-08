"""Installation schemas for the Saleor App Framework."""

from pydantic import BaseModel


class WebhookCredentials(BaseModel):
    """Webhook credentials for the Saleor App Framework."""

    webhook_id: str
    webhook_secret_key: str


class InstallData(BaseModel):
    """Installation data for the Saleor App Framework."""

    auth_token: str
