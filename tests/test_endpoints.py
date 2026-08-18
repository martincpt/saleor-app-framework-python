"""Tests for the Saleor App configuration endpoint handlers."""

from collections import defaultdict
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from saleor_app.app import SaleorApp
from saleor_app.core.enums import SaleorEventType
from saleor_app.deps import SALEOR_DOMAIN_HEADER


async def test_manifest(client: TestClient, saleor_app: SaleorApp) -> None:
    """GET /configuration/manifest returns the serialised manifest JSON."""
    response = client.get("configuration/manifest")

    assert response.status_code == 200

    result = response.json()
    expected = saleor_app.manifest.model_dump(mode="json", by_alias=True)

    assert result == expected


async def test_install(
    client: TestClient,
    saleor_app_with_webhooks: SaleorApp,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """POST /configuration/install registers webhooks and calls store_app_data."""
    install_app_mock = AsyncMock()
    monkeypatch.setattr("saleor_app.endpoints.install_app", install_app_mock)

    saleor_app_with_webhooks.validate_domain = AsyncMock(return_value=True)

    response = client.post(
        url="configuration/install",
        json={"auth_token": "saleor-app-token"},
        headers={SALEOR_DOMAIN_HEADER: "example.com"},
    )

    assert response.status_code == 200

    install_app_mock.assert_awaited_once_with(
        saleor_domain="example.com",
        auth_token="saleor-app-token",
        manifest=saleor_app_with_webhooks.manifest,
        events=defaultdict(
            list,
            {
                "awssqs://username:password@localstack:4566/account_id/order_created": [
                    (SaleorEventType.ORDER_CREATED, None),
                ],
                "awssqs://username:password@localstack:4566/account_id/order_updated": [
                    (SaleorEventType.ORDER_UPDATED, None),
                ],
                "http://testserver/webhook": [
                    (SaleorEventType.PRODUCT_CREATED, None),
                    (SaleorEventType.PRODUCT_UPDATED, None),
                    (SaleorEventType.PRODUCT_DELETED, None),
                ],
            },
        ),
        use_insecure_saleor_http=False,
    )
