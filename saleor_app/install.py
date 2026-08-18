"""App installation logic for the Saleor App Framework."""

import logging
import secrets
import string

from .client.client import SaleorClient
from .client.exceptions import GraphQLError
from .client.mutations import CREATE_WEBHOOK
from .core.install import WebhookCredentials
from .core.manifest import Manifest
from .core.types import AppToken, DomainName, WebhookSubscriptionMap
from .errors import InstallAppError

logger = logging.getLogger(__name__)


async def install_app(
    saleor_domain: DomainName,
    auth_token: AppToken,
    manifest: Manifest,
    events: WebhookSubscriptionMap,
    use_insecure_saleor_http: bool,
) -> WebhookCredentials:
    """Register webhooks with Saleor and return the resulting credentials."""
    alphabet = string.ascii_letters + string.digits
    secret_key = "".join(secrets.choice(alphabet) for _ in range(20))

    schema = "http" if use_insecure_saleor_http else "https"

    errors = []

    async with SaleorClient.for_app(
        url=f"{schema}://{saleor_domain}",
        manifest=manifest,
        auth_token=auth_token,
    ) as saleor_client:
        for target_url, target_events in events.items():
            for event_type, subscription_query in target_events:
                webhook_input = {
                    "targetUrl": str(target_url),
                    "events": [event_type.upper()],
                    "name": f"{manifest.name}",
                    "secretKey": secret_key,
                }

                if subscription_query:
                    webhook_input["query"] = subscription_query

                try:
                    response = await saleor_client.execute(
                        CREATE_WEBHOOK,
                        variables={"input": webhook_input},
                    )
                except GraphQLError as exc:
                    errors.append(exc)

    if errors:
        logger.error("Unable to finish installation of app for %s.", saleor_domain)
        logger.debug(
            "Unable to finish installation of app for %s. Received errors: %s",
            saleor_domain,
            list(map(str, errors)),
        )
        message = f"Failed to create webhooks for {saleor_domain}."
        raise InstallAppError(message)

    saleor_webhook_id = response["webhookCreate"]["webhook"]["id"]
    return WebhookCredentials(
        webhook_id=saleor_webhook_id,
        webhook_secret_key=secret_key,
    )
