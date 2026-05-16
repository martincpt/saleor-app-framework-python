"""Saleor App for the Saleor App Framework."""

from fastapi import APIRouter, FastAPI

from .endpoints import install, manifest
from .schemas.core import (
    GetWebhookDetails,
    SaveAppData,
    ValidateDomain,
)
from .schemas.manifest import Manifest
from .webhook import WebhookRoute, WebhookRouter


class SaleorApp(FastAPI):
    """Saleor App main class."""

    manifest: Manifest
    validate_domain: ValidateDomain
    save_app_data: SaveAppData
    use_insecure_saleor_http: bool
    development_auth_token: str | None
    configuration_router: APIRouter

    get_webhook_details: GetWebhookDetails
    webhook_router: WebhookRouter

    def __init__(
        self,
        *,
        manifest: Manifest,
        validate_domain: ValidateDomain,
        save_app_data: SaveAppData,
        use_insecure_saleor_http: bool = False,
        development_auth_token: str | None = None,
        **kwargs,
    ) -> None:
        """Initialize SaleorApp instance."""
        super().__init__(**kwargs)

        self.manifest = manifest

        self.validate_domain = validate_domain
        self.save_app_data = save_app_data

        self.use_insecure_saleor_http = use_insecure_saleor_http
        self.development_auth_token = development_auth_token

        self.configuration_router = APIRouter(
            prefix="/configuration",
            tags=["configuration"],
        )

    def include_saleor_app_routes(self) -> None:
        """Include Saleor app routes."""
        self.configuration_router.get(
            "/manifest",
            response_model=Manifest,
            name="manifest",
        )(manifest)
        self.configuration_router.post(
            "/install",
            responses={
                400: {"description": "Missing required header"},
                403: {"description": "Incorrect token or not enough permissions"},
            },
            name="app-install",
        )(install)

        self.include_router(self.configuration_router)

    def include_webhook_router(self, get_webhook_details: GetWebhookDetails) -> None:
        """Include Saleor webhook routes."""
        self.get_webhook_details = get_webhook_details
        self.webhook_router = WebhookRouter(
            prefix="/webhook",
            responses={
                400: {"description": "Missing required header"},
                401: {"description": "Incorrect signature"},
                404: {"description": "Incorrect saleor event"},
            },
            route_class=WebhookRoute,
        )

        self.include_router(self.webhook_router)
