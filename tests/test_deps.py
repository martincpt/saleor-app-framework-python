"""Tests for FastAPI dependency functions in saleor_app.deps."""

import hashlib
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, Request
from pytest_mock import MockerFixture

from saleor_app.app import SaleorApp
from saleor_app.client.client import SaleorClient
from saleor_app.client.exceptions import GraphQLError
from saleor_app.core.install import WebhookCredentials
from saleor_app.core.types import GetWebhookCredentials
from saleor_app.deps import (
    saleor_domain_header,
    saleor_token,
    verify_saleor_domain,
    verify_saleor_token,
    verify_webhook_signature,
)


async def test_saleor_domain_header_missing() -> None:
    """Raises HTTPException when the domain header is absent."""
    with pytest.raises(HTTPException) as excinfo:
        await saleor_domain_header(None)

    assert str(excinfo.value.detail) == "Missing X-SALEOR-DOMAIN header."


async def test_saleor_domain_header() -> None:
    """Returns the domain string when the header is present."""
    assert await saleor_domain_header("saleor_domain") == "saleor_domain"


async def test_saleor_token(saleor_app: SaleorApp) -> None:
    """Returns the token when explicitly provided."""
    assert await saleor_token(saleor_app, "token") == "token"


async def test_saleor_token_from_settings(saleor_app: SaleorApp) -> None:
    """Falls back to development_auth_token when no token header is present."""
    assert await saleor_token(saleor_app, None) == "test_token"


async def test_saleor_token_missing(saleor_app: SaleorApp) -> None:
    """Raises HTTPException when no token is available at all."""
    saleor_app.development_auth_token = None

    with pytest.raises(HTTPException) as excinfo:
        assert await saleor_token(saleor_app, None) == "test_token"

    assert str(excinfo.value.detail) == "Missing X-SALEOR-TOKEN header."


async def test_verify_saleor_token(
    saleor_app: SaleorApp,
    mocker: MockerFixture,
) -> None:
    """Returns True when Saleor confirms the token is valid."""
    mock_saleor_client = AsyncMock(SaleorClient)
    mock_saleor_client.__aenter__.return_value.execute.return_value = {
        "tokenVerify": {"isValid": True},
    }
    mocker.patch(
        "saleor_app.deps.SaleorClient.for_app",
        return_value=mock_saleor_client,
    )
    assert await verify_saleor_token(saleor_app, "saleor_domain", "token")


async def test_verify_saleor_token_invalid(
    saleor_app: SaleorApp,
    mocker: MockerFixture,
) -> None:
    """Raises HTTPException when Saleor reports the token as invalid."""
    mock_saleor_client = AsyncMock(SaleorClient)
    mock_saleor_client.__aenter__.return_value.execute.return_value = {
        "tokenVerify": {"isValid": False},
    }
    mocker.patch(
        "saleor_app.deps.SaleorClient.for_app",
        return_value=mock_saleor_client,
    )
    with pytest.raises(HTTPException) as excinfo:
        await verify_saleor_token(saleor_app, "saleor_domain", "token")

    assert (
        excinfo.value.detail
        == "Provided X-SALEOR-DOMAIN and X-SALEOR-TOKEN are incorrect."
    )


async def test_verify_saleor_token_saleor_error(
    saleor_app: SaleorApp,
    mocker: MockerFixture,
) -> None:
    """Returns False when the Saleor API raises a GraphQL error."""
    mock_saleor_client = AsyncMock(SaleorClient)
    mock_saleor_client.__aenter__.return_value.execute.side_effect = GraphQLError(
        errors=[{"message": "Invalid token", "locations": [{"line": 1, "column": 2}]}],
    )
    mocker.patch(
        "saleor_app.deps.SaleorClient.for_app",
        return_value=mock_saleor_client,
    )
    assert not await verify_saleor_token(saleor_app, "saleor_domain", "token")


async def test_verify_saleor_domain(saleor_app: SaleorApp) -> None:
    """Returns True when validate_domain callback accepts the domain."""
    saleor_app.validate_domain.return_value = True  # type: ignore[attr-defined]
    assert await verify_saleor_domain(saleor_app, "saleor_domain")


async def test_verify_saleor_domain_invalid(saleor_app: SaleorApp) -> None:
    """Raises HTTPException when validate_domain callback rejects the domain."""
    saleor_app.validate_domain.return_value = False  # type: ignore[attr-defined]
    with pytest.raises(HTTPException) as excinfo:
        await verify_saleor_domain(saleor_app, "saleor_domain")

    assert excinfo.value.detail == "Provided domain saleor_domain is invalid."


async def test_verify_webhook_signature(
    get_webhook_credentials: GetWebhookCredentials,
    mock_request: Request,
    mocker: MockerFixture,
) -> None:
    """Passes without error when the HMAC signature matches."""
    mock_request.app.include_webhook_router(get_webhook_credentials)
    mock_request.app.get_webhook_credentials.return_value = WebhookCredentials(
        webhook_id="webhook_id",
        webhook_secret_key="webhook_secret_key",
    )
    mock_hmac_new = mocker.patch("saleor_app.deps.hmac.new")
    mock_hmac_new.return_value.hexdigest.return_value = "test_signature"

    await verify_webhook_signature(
        request=mock_request,
        saleor_app=mock_request.app,
        signature="test_signature",
        domain_name="saleor_domain",
    )

    mock_hmac_new.assert_called_once_with(
        b"webhook_secret_key",
        b"request_body",
        hashlib.sha256,
    )


async def test_verify_webhook_signature_invalid(
    get_webhook_credentials: GetWebhookCredentials,
    mock_request: Request,
    mocker: MockerFixture,
) -> None:
    """Raises HTTPException when the HMAC signature does not match."""
    mock_request.app.include_webhook_router(get_webhook_credentials)
    mock_request.app.get_webhook_credentials.return_value = WebhookCredentials(
        webhook_id="webhook_id",
        webhook_secret_key="webhook_secret_key",
    )
    mock_hmac_new = mocker.patch("saleor_app.deps.hmac.new")
    mock_hmac_new.return_value.hexdigest.return_value = "test_signature"

    with pytest.raises(HTTPException) as excinfo:
        await verify_webhook_signature(
            request=mock_request,
            saleor_app=mock_request.app,
            signature="BAD_signature",
            domain_name="saleor_domain",
        )

    assert excinfo.value.detail == "Invalid webhook signature for x-saleor-signature"
