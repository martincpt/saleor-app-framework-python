"""Tests for SaleorClient HTTP client."""

from unittest.mock import AsyncMock

import aiohttp
import pytest
from aiohttp import ClientTimeout
from pytest_mock import MockerFixture

from saleor_app.client.client import SaleorClient
from saleor_app.client.exceptions import GraphQLError


@pytest.mark.parametrize(
    ("auth_token", "timeout_seconds"),
    [
        (None, None),
        (None, 5),
        ("token", None),
        ("token", 10),
    ],
)
async def test__init__(auth_token: str | None, timeout_seconds: int | None) -> None:
    """SaleorClient.__init__ sets base URL, auth header, and timeout correctly."""
    kwargs: dict = {
        "url": "http://saleor.local",
        "user_agent": "saleor_client/test-0.0.1",
    }
    if auth_token is not None:
        kwargs["auth_token"] = auth_token
    if timeout_seconds is not None:
        kwargs["timeout"] = timeout_seconds

    client = SaleorClient(**kwargs)

    assert str(client.session._base_url) == kwargs["url"]

    if auth_token is not None:
        assert client.session.headers["Authorization"] == f"Bearer {auth_token}"
    if timeout_seconds is not None:
        assert client.session.timeout == ClientTimeout(timeout_seconds)


async def test_close(mocker: MockerFixture) -> None:
    """close() awaits the underlying session close method."""
    client = SaleorClient(url="http://saleor.local", user_agent="test")
    spy = mocker.spy(client, "close")

    await client.close()

    spy.assert_awaited_once_with()


async def test_context_manager(mocker: MockerFixture) -> None:
    """Using SaleorClient as an async context manager closes the session on exit."""
    async with SaleorClient(
        url="http://saleor.local",
        user_agent="test",
    ) as saleor:
        spy = mocker.spy(saleor, "close")
        assert isinstance(saleor, SaleorClient)

    spy.assert_awaited_once_with()


async def test_execute(monkeypatch: pytest.MonkeyPatch) -> None:
    """execute() returns the data field from a successful GraphQL response."""
    mock_session = AsyncMock(aiohttp.ClientSession)
    mock_session.post.return_value.__aenter__.return_value.json.return_value = {
        "data": "response_data",
    }
    async with SaleorClient(
        url="http://saleor.local",
        user_agent="test",
    ) as saleor:
        monkeypatch.setattr(saleor, "session", mock_session, raising=True)
        assert (
            await saleor.execute("QUERY", variables={"test": "value"})
            == "response_data"
        )

    mock_session.post.assert_called_once_with(
        url="/graphql/",
        json={"query": "QUERY", "variables": {"test": "value"}},
    )


async def test_execute_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """execute() raises GraphQLError when the response contains errors."""
    mock_session = AsyncMock(aiohttp.ClientSession)
    mock_session.post.return_value.__aenter__.return_value.json.return_value = {
        "data": "response_data",
        "errors": [{"message": "there are errors"}],
    }
    async with SaleorClient(
        url="http://saleor.local",
        user_agent="test",
    ) as saleor:
        monkeypatch.setattr(saleor, "session", mock_session, raising=True)
        with pytest.raises(GraphQLError) as excinfo:
            await saleor.execute("QUERY", variables={"test": "value"})

    assert excinfo.value.errors == [{"message": "there are errors"}]
    assert excinfo.value.response_data == "response_data"
