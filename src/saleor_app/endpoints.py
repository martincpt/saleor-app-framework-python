import logging
from collections import defaultdict
from typing import TYPE_CHECKING

from fastapi import Depends, Request
from fastapi.exceptions import HTTPException

from .client.exceptions import GraphQLError
from .deps import saleor_app, saleor_domain_header, verify_saleor_domain
from .errors import InstallAppError
from .install import install_app
from .schemas.core import InstallData
from .schemas.manifest import Manifest
from .schemas.utils import LazyUrl

if TYPE_CHECKING:
    from .app import SaleorApp
    from .schemas.handlers import WebhookSubscriptionMap

logger = logging.getLogger(__name__)


async def manifest(
    request: Request,
    saleor_app: "SaleorApp" = Depends(saleor_app),
) -> Manifest:
    """Manifest endpoint."""
    for name, field in saleor_app.manifest:
        if isinstance(field, LazyUrl):
            setattr(saleor_app.manifest, name, field(request))

    for extension in saleor_app.manifest.extensions:
        if isinstance(extension.url, LazyUrl):
            extension.url = extension.url(request)

    return saleor_app.manifest


async def install(
    request: Request,
    data: InstallData,
    saleor_app: "SaleorApp" = Depends(saleor_app),
    _domain_is_valid=Depends(verify_saleor_domain),
    saleor_domain=Depends(saleor_domain_header),
) -> None:
    events: WebhookSubscriptionMap = defaultdict(list)

    if hasattr(saleor_app, "webhook_router"):
        for event_type in saleor_app.webhook_router.http_routes:
            subscription_query = (
                saleor_app.webhook_router.http_routes_subscriptions.get(
                    event_type,
                )
            )
            key = str(request.url_for("handle-webhook"))
            events[key].append((event_type, subscription_query))

        for event_type, sqs_handler in saleor_app.webhook_router.sqs_routes.items():
            key = str(sqs_handler.target_url)
            events[key].append((event_type, None))

    if not events:
        return

    try:
        webhook_credentials = await install_app(
            saleor_domain=saleor_domain,
            auth_token=data.auth_token,
            manifest=saleor_app.manifest,
            events=events,
            use_insecure_saleor_http=saleor_app.use_insecure_saleor_http,
        )
    except (InstallAppError, GraphQLError) as exc:
        logger.debug(str(exc), exc_info=True)
        raise HTTPException(
            status_code=403,
            detail="Incorrect token or not enough permissions",
        ) from exc

    await saleor_app.store_app_data(
        saleor_domain,
        data.auth_token,
        webhook_credentials,
    )
