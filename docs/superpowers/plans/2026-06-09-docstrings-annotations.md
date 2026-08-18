# Docstrings and Annotations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add consistent docstrings and type annotations throughout the package, then remove the 12 corresponding lint ignores from `pyproject.toml`.

**Architecture:** Pure documentation and annotation additions — no behavioral changes. Each task targets one or two files, ending with a lint + test verification. The lint ignores are removed last, after all content is in place.

**Tech Stack:** Python 3.12+, ruff (pre-commit v0.2.2), pytest

---

## Files Modified

| File | Changes |
|------|---------|
| `saleor_app/errors.py` | Module docstring, fix 3 existing docstrings |
| `saleor_app/client/exceptions.py` | Module docstring, fix punctuation, add `-> None` / `-> str` |
| `saleor_app/install.py` | Module docstring, one-line `install_app` docstring |
| `saleor_app/endpoints.py` | Module docstring, one-line `install` docstring |
| `saleor_app/client/client.py` | Class docstring, detailed method docstrings, all annotations |
| `saleor_app/webhook.py` | Module docstring, class/method docstrings |
| `saleor_app/deps.py` | 4 function docstrings, replace `require_permission` docstring, 2 class docstrings + `__init__` annotations |
| `saleor_app/app.py` | Replace `__init__` one-liner with detailed docstring |
| `pyproject.toml` | Remove 12 lint ignores |

---

## Task 1: errors.py and client/exceptions.py

**Files:**
- Modify: `saleor_app/errors.py`
- Modify: `saleor_app/client/exceptions.py`

- [ ] **Step 1: Update errors.py**

Replace the entire file:

```python
"""Error classes for the Saleor App Framework."""


class SaleorAppError(Exception):
    """Base error for all Saleor App Framework exceptions."""


class InstallAppError(SaleorAppError):
    """Raised when webhook installation fails during app setup."""


class ConfigurationError(SaleorAppError):
    """Raised when the app is configured incorrectly."""
```

- [ ] **Step 2: Update client/exceptions.py**

Replace the entire file:

```python
"""Exception classes for the Saleor GraphQL client."""

from collections.abc import Sequence
from typing import Any


class GraphQLError(Exception):
    """Raised when the Saleor GraphQL API returns errors."""

    def __init__(
        self,
        errors: Sequence[dict[str, Any]],
        response_data: dict[str, Any] | None = None,
    ) -> None:
        self.errors = errors
        self.response_data = response_data

    def __str__(self) -> str:
        return (
            f"GraphQLError: {', '.join([error['message'] for error in self.errors])}."
        )


class IgnoredPrincipalError(Exception):
    message = "Ignore webhook with {} principal ids."

    def __init__(self, principal_ids: list[str]) -> None:
        super().__init__(self.message.format(",".join(principal_ids)))
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest --tb=short -q
```

Expected: `26 passed`

- [ ] **Step 4: Commit**

```bash
git add saleor_app/errors.py saleor_app/client/exceptions.py
git commit -m "docs: fix docstrings in errors and exceptions modules"
```

---

## Task 2: install.py and endpoints.py

**Files:**
- Modify: `saleor_app/install.py`
- Modify: `saleor_app/endpoints.py`

- [ ] **Step 1: Add module docstring and function docstring to install.py**

Add `"""App installation logic for the Saleor App Framework."""` as the first line of `saleor_app/install.py`.

Then add a one-line docstring to `install_app`:

```python
async def install_app(
    saleor_domain: DomainName,
    auth_token: AppToken,
    manifest: Manifest,
    events: WebhookSubscriptionMap,
    use_insecure_saleor_http: bool,
) -> WebhookCredentials:
    """Register webhooks with Saleor and return the resulting credentials."""
    alphabet = string.ascii_letters + string.digits
```

- [ ] **Step 2: Add module docstring and function docstring to endpoints.py**

Add `"""FastAPI endpoint handlers for the Saleor App configuration routes."""` as the first line of `saleor_app/endpoints.py`.

Then add a one-line docstring to `install`:

```python
async def install(
    request: Request,
    data: InstallData,
    saleor_app: "SaleorApp" = Depends(saleor_app),
    _domain_is_valid=Depends(verify_saleor_domain),
    saleor_domain=Depends(saleor_domain_header),
) -> None:
    """Handle app installation by registering webhooks with Saleor."""
    events: WebhookSubscriptionMap = defaultdict(list)
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest --tb=short -q
```

Expected: `26 passed`

- [ ] **Step 4: Commit**

```bash
git add saleor_app/install.py saleor_app/endpoints.py
git commit -m "docs: add module and function docstrings to install and endpoints"
```

---

## Task 3: client/client.py and client/mutations.py

**Files:**
- Modify: `saleor_app/client/client.py`
- Modify: `saleor_app/client/mutations.py`

- [ ] **Step 1: Add module docstring to mutations.py**

Add `"""GraphQL mutation strings for the Saleor API."""` as the very first line of `saleor_app/client/mutations.py`.

- [ ] **Step 2: Replace client/client.py**

```python
"""HTTP client for the Saleor GraphQL API."""

import logging
import types
from typing import Any

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
            url: Base URL of the Saleor instance (e.g. ``https://store.example.com``).
            manifest: The app manifest, used to derive the User-Agent header.
            **kwargs: Additional arguments forwarded to ``__init__`` (e.g. ``auth_token``, ``timeout``).

        Returns:
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

    async def __aenter__(self) -> "SaleorClient":
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
            query: The GraphQL query or mutation string.
            variables: Optional mapping of variable names to values.

        Returns:
            The ``data`` field of the GraphQL response.

        Raises:
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
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest --tb=short -q
```

Expected: `26 passed`

- [ ] **Step 4: Commit**

```bash
git add saleor_app/client/client.py saleor_app/client/mutations.py
git commit -m "docs: add docstrings and annotations to SaleorClient"
```

---

## Task 4: webhook.py

**Files:**
- Modify: `saleor_app/webhook.py`

- [ ] **Step 1: Add module docstring**

Add `"""Webhook routing infrastructure for the Saleor App Framework."""` as the very first line of `saleor_app/webhook.py`.

- [ ] **Step 2: Add class and method docstrings**

Add a docstring to `WebhookRoute`:

```python
class WebhookRoute(APIRoute):
    """Custom APIRoute that dispatches requests by the x-saleor-event header."""

    def get_route_handler(self) -> Callable[[Request], Awaitable[Response]]:
        """Return a handler that reads the event header and dispatches to the registered route."""
        async def custom_route_handler(request: Request) -> Response:
```

Add a docstring to `WebhookRouter` and its `__init__`:

```python
class WebhookRouter(APIRouter):
    """APIRouter that manages HTTP and SQS webhook route registration."""

    http_routes: dict[SaleorEventType, APIRoute]
    http_routes_subscriptions: dict[SaleorEventType, str]
    sqs_routes: dict[SaleorEventType, SQSHandler]

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the router and register the OpenAPI stub endpoint."""
        super().__init__(*args, **kwargs)
```

- [ ] **Step 3: Add detailed docstrings to http_event_route and sqs_event_route**

Replace the `http_event_route` method signature and add docstring:

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
        def decorator(func: WebHookHandlerSignature) -> None:
            """Register func as the handler for this event type."""
            self.http_routes[event_type] = APIRoute(
```

Replace the `sqs_event_route` method signature and add docstring:

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
        def decorator(func: WebHookHandlerSignature) -> None:
            """Register func as the SQS handler for this event type."""
            self.sqs_routes[event_type] = SQSHandler(
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest --tb=short -q
```

Expected: `26 passed`

- [ ] **Step 5: Commit**

```bash
git add saleor_app/webhook.py
git commit -m "docs: add docstrings to webhook routing classes"
```

---

## Task 5: deps.py — docstrings and annotations

**Files:**
- Modify: `saleor_app/deps.py`

- [ ] **Step 1: Add module docstring**

Add `"""FastAPI dependency functions and classes for the Saleor App Framework."""` as the very first line of `saleor_app/deps.py`.

- [ ] **Step 2: Add one-line docstrings to the four undocumented functions**

Add docstrings after each `async def` signature (before the body):

```python
async def saleor_domain_header(
    saleor_domain: str | None = Header(None, alias=SALEOR_DOMAIN_HEADER),
) -> DomainName:
    """Extract and validate the x-saleor-domain header."""
    if not saleor_domain:
```

```python
async def verify_saleor_token(
    saleor_app: "SaleorApp" = Depends(saleor_app),
    saleor_domain: DomainName = Depends(saleor_domain_header),
    token: str = Depends(saleor_token),
) -> bool:
    """Verify the Saleor auth token against the Saleor API."""
    schema = "http" if saleor_app.use_insecure_saleor_http else "https"
```

```python
async def verify_saleor_domain(
    saleor_app: "SaleorApp" = Depends(saleor_app),
    saleor_domain: DomainName = Depends(saleor_domain_header),
) -> bool:
    """Verify the Saleor domain using the app's validate_domain callback."""
    domain_is_valid = await saleor_app.validate_domain(saleor_domain)
```

```python
async def verify_webhook_signature(
    request: Request,
    saleor_app: "SaleorApp" = Depends(saleor_app),
    signature: str | None = Header(None, alias=SALEOR_SIGNATURE_HEADER),
    domain_name: DomainName = Depends(saleor_domain_header),
) -> None:
    """Verify the HMAC-SHA256 webhook signature from the request header."""
    if not signature:
```

- [ ] **Step 3: Replace the require_permission docstring and add docstring to inner func**

Change the existing multi-line docstring on `require_permission` from:

```python
    """Validates is the requesting principal is authorized for the specified action

    Usage:

    ```
    Depends(require_permission([SaleorPermissions.MANAGE_PRODUCTS]))
    ```
    """
```

To:

```python
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

    def func(
        saleor_token: str = Depends(saleor_token),
        _saleor_domain: DomainName = Depends(saleor_domain_header),
        _token_is_valid: bool = Depends(verify_saleor_token),
    ) -> None:
        """Check that the JWT permissions satisfy the required set."""
        jwt_payload = jwt.decode(
```

- [ ] **Step 4: Add class docstrings and annotate both __init__ methods**

Replace `ConfigurationFormDeps`:

```python
class ConfigurationFormDeps:
    """FastAPI dependency bundle for configuration form endpoints."""

    def __init__(
        self,
        request: Request,
        domain: str = Query(...),
    ) -> None:
        self.request = request
        self.saleor_domain = domain
```

Replace `ConfigurationDataDeps`:

```python
class ConfigurationDataDeps:
    """FastAPI dependency bundle for authenticated configuration data endpoints."""

    def __init__(
        self,
        request: Request,
        saleor_domain: str = Depends(saleor_domain_header),
        _domain_is_valid: bool = Depends(verify_saleor_domain),
        _token_is_valid: bool = Depends(verify_saleor_token),
        token: str = Depends(saleor_token),
    ) -> None:
        self.request = request
        self.saleor_domain = saleor_domain
        self.token = token
```

- [ ] **Step 5: Run tests**

```bash
uv run pytest --tb=short -q
```

Expected: `26 passed`

- [ ] **Step 6: Commit**

```bash
git add saleor_app/deps.py
git commit -m "docs: add docstrings and annotations to deps module"
```

---

## Task 6: app.py — detailed SaleorApp.__init__ docstring

**Files:**
- Modify: `saleor_app/app.py`

- [ ] **Step 1: Replace the __init__ docstring**

Change the existing one-liner:

```python
        """Initialize SaleorApp instance."""
```

To:

```python
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

- [ ] **Step 2: Run tests**

```bash
uv run pytest --tb=short -q
```

Expected: `26 passed`

- [ ] **Step 3: Commit**

```bash
git add saleor_app/app.py
git commit -m "docs: add detailed docstring to SaleorApp.__init__"
```

---

## Task 7: Remove lint ignores and verify

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Remove the 12 lint ignores from pyproject.toml**

In `[tool.ruff]` → `lint.ignore`, remove these 12 lines (keep all other ignores):

```toml
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

Also remove the comment above them:
```toml
    # Most common errors from forked project, we surpress for now,
    # but they are planned to be addressed in the future:
```

- [ ] **Step 2: Run ruff to verify no violations remain**

```bash
uv tool run ruff check .
```

Expected: output showing only warnings (incompatible rule notices), zero errors. If any errors appear, fix them before proceeding.

- [ ] **Step 3: Run full test suite**

```bash
uv run pytest --tb=short -q
```

Expected: `26 passed`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "refactor: remove resolved lint ignores (docstrings and annotations)"
```
