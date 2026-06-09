import logging

import aiohttp
from aiohttp.client import ClientTimeout

from saleor_app.core.manifest import Manifest

from .exceptions import GraphQLError

logger = logging.getLogger("saleor.client")


class SaleorClient:
    @classmethod
    def for_app(cls, url: str, manifest: Manifest, **kwargs) -> "SaleorClient":
        user_agent = f"saleor_client/{manifest.id}-{manifest.version}"
        return cls(url=url, user_agent=user_agent, **kwargs)

    def __init__(self, url, user_agent, auth_token=None, timeout=15):
        headers = {"User-Agent": user_agent}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        self.session = aiohttp.ClientSession(
            base_url=url,
            headers=headers,
            raise_for_status=True,
            timeout=ClientTimeout(total=timeout),
        )

    async def close(self):
        await self.session.close()

    async def __aenter__(self) -> "SaleorClient":
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        await self.close()

    async def execute(self, query, variables=None):
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
