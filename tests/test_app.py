"""Tests for the SaleorApp class."""

import pytest
from starlette.routing import NoMatchFound

from saleor_app.app import Manifest, SaleorApp
from saleor_app.core.types import GetWebhookCredentials
from saleor_app.webhook import WebhookRouter


async def test_saleor_app_init(
    saleor_app: SaleorApp,
    manifest: Manifest,
) -> None:
    """SaleorApp registers manifest and install routes but not the webhook route."""
    assert saleor_app.manifest == manifest

    assert saleor_app.url_path_for("manifest") == "/configuration/manifest"
    assert saleor_app.url_path_for("app-install") == "/configuration/install"

    with pytest.raises(NoMatchFound):
        saleor_app.url_path_for("handle-webhook")


async def test_include_webhook_router(
    saleor_app: SaleorApp,
    get_webhook_credentials: GetWebhookCredentials,
) -> None:
    """include_webhook_router mounts the webhook router and stores credentials."""
    saleor_app.include_webhook_router(get_webhook_credentials)

    assert saleor_app.get_webhook_credentials == get_webhook_credentials
    assert saleor_app.url_path_for("handle-webhook") == "/webhook"
    assert isinstance(saleor_app.webhook_router, WebhookRouter)
