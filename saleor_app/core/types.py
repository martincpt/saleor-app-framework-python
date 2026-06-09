"""Type aliases for the Saleor App Framework."""

from collections.abc import Awaitable, Callable

from saleor_app.core.enums import SaleorEventType
from saleor_app.core.install import WebhookCredentials
from saleor_app.core.webhook import Webhook

DomainName = str
AppToken = str
Url = str

ValidateDomain = Callable[[DomainName], Awaitable[bool]]
StoreAppData = Callable[[DomainName, AppToken, WebhookCredentials], Awaitable[None]]
GetWebhookCredentials = Callable[[DomainName], Awaitable[WebhookCredentials]]

WebhookSubscription = tuple[SaleorEventType, str | None]
WebhookSubscriptionMap = dict[str, list[WebhookSubscription]]
WebHookHandlerSignature = Callable[[list[Webhook], DomainName], Awaitable] | None
