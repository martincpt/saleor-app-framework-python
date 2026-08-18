"""HTTP client for the Saleor GraphQL API."""

import logging
import types
from typing import Any, Self

import aiohttp
from aiohttp.client import ClientTimeout

from saleor_app.core.manifest import Manifest

from .exceptions import GraphQLError

logger = logging.getLogger("saleor.client")


class SaleorClient:
    """Async HTTP client for the Saleor GraphQL API."""

    @classmethod
    def for_app(cls, url: str, manifest: Manifest, **kwargs: Any) -> "SaleorClient":
        """Create a SaleorClient configured for a specific installed app.

        Args:
        ----
            url: Base URL of the Saleor instance (e.g. ``https://store.example.com``).
            manifest: The app manifest, used to derive the User-Agent header.
            **kwargs: Additional arguments forwarded to ``__init__`` (e.g. ``auth_token``, ``timeout``).

        Returns:
        -------
            A configured SaleorClient ready for use as a context manager.

        """
        user_agent = f"saleor_client/{manifest.id}-{manifest.version}"
        return cls(url=url, user_agent=user_agent, **kwargs)

    def __init__(
        self,
        url: str,
        user_agent: str,
        auth_token: str | None = None,
        timeout: int = 15,
    ) -> None:
        """Initialize a SaleorClient session."""
        headers = {"User-Agent": user_agent}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        self.session = aiohttp.ClientSession(
            base_url=url,
            headers=headers,
            raise_for_status=True,
            timeout=ClientTimeout(total=timeout),
        )

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        await self.session.close()

    async def __aenter__(self) -> Self:
        """Enter the async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exit the async context manager and close the session."""
        await self.close()

    async def execute(self, query: str, variables: dict[str, Any] | None = None) -> Any:
        """Execute a GraphQL query or mutation against the Saleor API.

        Args:
        ----
            query: The GraphQL query or mutation string.
            variables: Optional mapping of variable names to values.

        Returns:
        -------
            The ``data`` field of the GraphQL response.

        Raises:
        ------
            GraphQLError: If the response contains a top-level ``errors`` field.

        """
        async with self.session.post(
            url="/graphql/",
            json={"query": query, "variables": variables},
        ) as resp:
            response_data = await resp.json()
            if errors := response_data.get("errors"):
                exc = GraphQLError(
                    errors=errors,
                    response_data=response_data.get("data"),
                )
                logger.error("Error when executing a GraphQL call to Saleor")
                logger.debug(str(exc))
                raise exc
            return response_data.get("data")
