from saleor_app.client.client import SaleorClient
from saleor_app.core.manifest import Manifest


def get_client_for_app(saleor_url: str, manifest: Manifest, **kwargs) -> SaleorClient:
    return SaleorClient(
        saleor_url=saleor_url,
        user_agent=f"saleor_client/{manifest.id}-{manifest.version}",
        **kwargs,
    )
