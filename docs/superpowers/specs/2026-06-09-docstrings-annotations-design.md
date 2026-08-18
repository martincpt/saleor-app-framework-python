# Docstrings and Annotations Design

**Goal:** Add consistent docstrings and type annotations throughout the package to satisfy D100–D107, D400, D415, ANN001, ANN201, ANN202, ANN204, and then remove those rules from the global lint ignore list.

**Architecture:** No behavioral changes. Every function, method, and class receives at minimum a one-line docstring ending with a period. Six high-value public API objects receive detailed Google-style docstrings with `Args:` / `Returns:`. All unannotated parameters and return types are filled in.

**Tech Stack:** Python 3.12+, Pydantic v2, FastAPI, ruff

---

## Docstring Tiers

### Tier 1 — Detailed (Google-style with Args / Returns)

| Object | File |
|--------|------|
| `SaleorApp.__init__` | `saleor_app/app.py` |
| `SaleorClient.for_app` | `saleor_app/client/client.py` |
| `SaleorClient.execute` | `saleor_app/client/client.py` |
| `require_permission` | `saleor_app/deps.py` |
| `WebhookRouter.http_event_route` | `saleor_app/webhook.py` |
| `WebhookRouter.sqs_event_route` | `saleor_app/webhook.py` |

### Tier 2 — One-line (single sentence, ends with `.`)

All other objects that are currently missing a docstring. Listed per file below.

---

## File-by-File Changes

### `saleor_app/errors.py`

Add module docstring. Fix all three existing docstrings (typo + missing periods):

```python
"""Error classes for the Saleor App Framework."""


class SaleorAppError(Exception):
    """Base error for all Saleor App Framework exceptions."""


class InstallAppError(SaleorAppError):
    """Raised when webhook installation fails during app setup."""


class ConfigurationError(SaleorAppError):
    """Raised when the app is configured incorrectly."""
```

---

### `saleor_app/install.py`

Add module docstring. Add one-line docstring to `install_app`:

```python
"""App installation logic for the Saleor App Framework."""
```

```python
async def install_app(...) -> WebhookCredentials:
    """Register webhooks with Saleor and return the resulting credentials."""
```

---

### `saleor_app/endpoints.py`

Add module docstring. Add one-line docstring to `install`:

```python
"""FastAPI endpoint handlers for the Saleor App configuration routes."""
```

```python
async def install(...) -> None:
    """Handle app installation by registering webhooks with Saleor."""
```

---

### `saleor_app/webhook.py`

Add module docstring. Add class and method docstrings:

```python
"""Webhook routing infrastructure for the Saleor App Framework."""
```

```python
class WebhookRoute(APIRoute):
    """Custom APIRoute that dispatches requests by Saleor event type header."""

    def get_route_handler(self) -> Callable[[Request], Awaitable[Response]]:
        """Return a handler that dispatches to the registered event route."""
```

```python
class WebhookRouter(APIRouter):
    """APIRouter that manages HTTP and SQS webhook route registration."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the router and register the OpenAPI stub endpoint."""
```

`http_event_route` — detailed:

```python
def http_event_route(
    self,
    event_type: SaleorEventType,
    subscription_query: str | None = None,
) -> Callable[[WebHookHandlerSignature], None]:
    """Register an HTTP handler for a Saleor webhook event.

    Returns a decorator that wires the decorated function as the handler for
    ``event_type``. Domain and signature verification are injected automatically
    as FastAPI dependencies.

    Args:
        event_type: The Saleor event type to subscribe to.
        subscription_query: Optional GraphQL subscription query sent during
            webhook registration to customise the payload.

    Returns:
        A decorator that registers the handler function.
    """
```

`sqs_event_route` — detailed:

```python
def sqs_event_route(
    self,
    target_url: SQSUrl,
    event_type: SaleorEventType,
) -> Callable[[WebHookHandlerSignature], None]:
    """Register an SQS handler for a Saleor webhook event.

    Returns a decorator that stores the decorated function as the SQS handler
    for ``event_type``. The SQS URL is registered with Saleor during installation.

    Args:
        target_url: The SQS queue URL that Saleor will deliver events to.
        event_type: The Saleor event type to subscribe to.

    Returns:
        A decorator that registers the handler function.
    """
```

Inner decorators also need one-line docstrings:

```python
def decorator(func: WebHookHandlerSignature) -> None:
    """Register func as the handler for this event type."""
```
(Same one-liner for both the http and sqs inner decorators.)

---

### `saleor_app/client/client.py`

Add class docstring. Add detailed docstrings and full annotations:

Add `import types` to `client.py` imports (needed for `__aexit__` annotation). `Any` is imported from `typing`.

```python
class SaleorClient:
    """Async HTTP client for the Saleor GraphQL API."""

    @classmethod
    def for_app(cls, url: str, manifest: Manifest, **kwargs) -> "SaleorClient":
        """Create a SaleorClient configured for a specific installed app.

        Args:
            url: Base URL of the Saleor instance (e.g. ``https://store.example.com``).
            manifest: The app manifest, used to derive the User-Agent header.
            **kwargs: Additional arguments forwarded to ``__init__`` (e.g. ``auth_token``, ``timeout``).

        Returns:
            A configured SaleorClient ready for use as a context manager.
        """

    def __init__(
        self,
        url: str,
        user_agent: str,
        auth_token: str | None = None,
        timeout: int = 15,
    ) -> None:
        """Initialize a SaleorClient session."""

    async def close(self) -> None:
        """Close the underlying aiohttp session."""

    async def __aenter__(self) -> "SaleorClient":
        """Enter the async context manager."""

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exit the async context manager and close the session."""

    async def execute(self, query: str, variables: dict | None = None) -> Any:
        """Execute a GraphQL query or mutation against the Saleor API.

        Args:
            query: The GraphQL query or mutation string.
            variables: Optional mapping of variable names to values.

        Returns:
            The ``data`` field of the GraphQL response.

        Raises:
            GraphQLError: If the response contains a top-level ``errors`` field.
        """
```

---

### `saleor_app/client/exceptions.py`

Add module docstring. Fix existing docstring punctuation:

```python
"""Exception classes for the Saleor GraphQL client."""


class GraphQLError(Exception):
    """Raised when the Saleor GraphQL API returns errors."""

    def __init__(self, ...) -> None:
        ...

    def __str__(self) -> str:
        ...
```

`__init__` and `__str__` get `-> None` and `-> str` return annotations respectively. No docstrings needed on those (covered by the class docstring).

---

### `saleor_app/deps.py`

Add one-line docstrings to four functions. Add annotations to two `__init__` methods.

```python
async def saleor_domain_header(...) -> DomainName:
    """Extract and validate the x-saleor-domain header."""

async def verify_saleor_token(...) -> bool:
    """Verify the Saleor auth token against the Saleor API."""

async def verify_saleor_domain(...) -> bool:
    """Verify the Saleor domain using the app's validate_domain callback."""

async def verify_webhook_signature(...) -> None:
    """Verify the HMAC-SHA256 webhook signature from the request header."""
```

`require_permission` — detailed (already has a docstring, replace/enhance it):

```python
def require_permission(permissions: list[SaleorPermissions]) -> Callable[..., None]:
    """Return a FastAPI dependency that enforces the given Saleor permissions.

    Decodes the JWT from the request and checks that the caller holds all
    listed permissions. Raises HTTP 403 if any required permission is missing.

    Args:
        permissions: List of ``SaleorPermissions`` the caller must hold.

    Returns:
        A FastAPI dependency callable suitable for use with ``Depends()``.

    Example:
        ``Depends(require_permission([SaleorPermissions.MANAGE_PRODUCTS]))``
    """
```

`ConfigurationFormDeps.__init__` annotations:

```python
def __init__(
    self,
    request: Request,
    domain: str = Query(...),
) -> None:
```

`ConfigurationDataDeps.__init__` annotations:

```python
def __init__(
    self,
    request: Request,
    saleor_domain: str = Depends(saleor_domain_header),
    _domain_is_valid: bool = Depends(verify_saleor_domain),
    _token_is_valid: bool = Depends(verify_saleor_token),
    token: str = Depends(saleor_token),
) -> None:
```

One-line docstrings for the two classes:

```python
class ConfigurationFormDeps:
    """FastAPI dependency bundle for configuration form endpoints."""

class ConfigurationDataDeps:
    """FastAPI dependency bundle for authenticated configuration data endpoints."""
```

---

### `saleor_app/app.py`

Replace the current one-liner `__init__` docstring with a detailed one:

```python
def __init__(
    self,
    *,
    manifest: Manifest,
    validate_domain: ValidateDomain,
    store_app_data: StoreAppData,
    get_webhook_credentials: GetWebhookCredentials | None = None,
    use_insecure_saleor_http: bool = False,
    development_auth_token: str | None = None,
    include_saleor_app_routes: bool = True,
    **kwargs,
) -> None:
    """Initialize a Saleor app with the given manifest and callbacks.

    Args:
        manifest: The app manifest describing identity, permissions, and extensions.
        validate_domain: Async callback that returns True if the Saleor domain is trusted.
        store_app_data: Async callback invoked after installation to persist credentials.
        get_webhook_credentials: Async callback that retrieves stored credentials for a
            domain. Required to enable the webhook router.
        use_insecure_saleor_http: If True, connect to Saleor over HTTP instead of HTTPS.
        development_auth_token: Optional fallback token when no auth header is present,
            for use during local development.
        include_saleor_app_routes: If True, register the manifest and install endpoints.
        **kwargs: Passed directly to FastAPI.
    """
```

---

## pyproject.toml Changes

Remove these 12 entries from `lint.ignore`:

```
"D100",
"D101",
"D102",
"D103",
"D105",
"D107",
"D400",
"D415",
"ANN001",
"ANN201",
"ANN202",
"ANN204",
```

Keep all other ignores unchanged.

---

## Out of Scope

- Test files (covered by `tests/*` per-file-ignores for most rules)
- `core/utils.py` (already has comprehensive docstrings and annotations)
- `core/enums.py`, `core/install.py`, `core/manifest.py`, `core/sqs.py`, `core/types.py`, `core/webhook.py` (classes already have docstrings with periods; no unannotated methods)
- `settings.py` (already complete)
- Any behavioral changes
