# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install all dependencies (including dev)
uv sync --all-extras --all-groups

# Run tests
uv run pytest

# Run a single test file
uv run pytest src/saleor_app/tests/test_app.py

# Run a single test by name
uv run pytest -k "test_name"

# Lint (ruff + mypy)
uv run ruff check .
uv run mypy src/

# Format
uv run black .

# Install pre-commit hooks (runs black, ruff, mypy, pytest on commit)
uv run pre-commit install
```

## Architecture

This is a Python library (not a runnable app) that provides a FastAPI-based framework for building [Saleor](https://github.com/saleor/saleor) apps. It handles the Saleor app lifecycle: installation, webhook registration, and webhook dispatch.

### Entry point: `SaleorApp`

`src/saleor_app/app.py` — `SaleorApp` extends `FastAPI`. Constructing it wires up two router groups:

- **`/configuration` router** (always included): serves `GET /configuration/manifest` and `POST /configuration/install`
- **`/webhook` router** (included when `get_webhook_credentials` is passed): a single `POST /webhook` endpoint dispatched by `WebhookRoute`

The app requires three async callbacks from the caller:
- `validate_domain(domain: str) -> bool` — trusts or rejects a Saleor domain
- `store_app_data(domain, auth_token, WebhookCredentials) -> None` — persists credentials after install
- `get_webhook_credentials(domain: str) -> WebhookCredentials` — retrieves stored credentials for signature verification

### Installation flow

`POST /configuration/install` (in `endpoints.py`) receives a Saleor auth token, collects all registered webhook routes, calls `install_app()` (`install.py`), which uses `SaleorClient` to call the Saleor GraphQL API (`webhookCreate` mutation) once per event type, then calls `store_app_data` with the resulting `WebhookCredentials` (webhook_id + secret_key).

### Webhook dispatch

`WebhookRouter` (`webhook.py`) extends `APIRouter`. It registers a single stub `POST ""` endpoint for OpenAPI docs, but the actual dispatch happens in `WebhookRoute.get_route_handler()`: it reads the `x-saleor-event` header and looks up the matching handler in `WebhookRouter.http_routes[event_type]`.

Handlers are registered with `@app.webhook_router.http_event_route(SaleorEventType.PRODUCT_CREATED)`. Each registered route automatically gets `verify_saleor_domain` and `verify_webhook_signature` as FastAPI `Depends`.

SQS routes (`sqs_event_route`) are registered to `sqs_routes` dict but there is no SQS dispatch logic in the framework itself — the routes are stored and registered as webhooks pointing to the SQS URL during installation.

### Webhook signature verification

`verify_webhook_signature` in `deps.py` fetches `WebhookCredentials` via `get_webhook_credentials`, then HMAC-SHA256 signs the raw request body with the stored secret key and compares against the `x-saleor-signature` header.

### `LazyUrl` / `LazyPath`

`src/saleor_app/schemas/utils.py` — URLs in `Manifest` fields can be `LazyUrl(route_name)` instances that defer resolution until a request is available. The manifest endpoint resolves them at request time using `request.url_for(name)`. `LazyUrl` supports a `public` flag and optional `servers` config for mapping internal URLs to public ones. `LazyPath` is the same but resolves to just the path component.

### Schemas

- `schemas/manifest.py` — `Manifest` model (serializes to Saleor's expected JSON with camelCase aliases), `Extension`, `MountType`, `TargetType`
- `schemas/handlers.py` — `SaleorEventType` enum (all Saleor webhook event names), `SQSHandler`, type aliases
- `schemas/webhook.py` — `WebhookV1/V2/V3` models; `Webhook = WebhookV3 | WebhookV2 | WebhookV1` union used as handler payload type
- `schemas/core.py` — `WebhookCredentials`, `InstallData`, `SaleorPermissions` enum, callback type aliases

### Dependency injection helpers (`deps.py`)

- `saleor_domain_header` — extracts `x-saleor-domain` header, 400 if missing
- `verify_saleor_domain` — calls the app's `validate_domain` callback
- `verify_webhook_signature` — HMAC verification against stored secret
- `require_permission(permissions)` — returns a FastAPI dependency that decodes the JWT and checks permissions
- `ConfigurationFormDeps` / `ConfigurationDataDeps` — dependency classes for configuration endpoints

## Key conventions

- Python 3.12+, Pydantic v2
- `Manifest` fields use `alias` (camelCase) for Saleor API compatibility; both field name and alias are accepted via `populate_by_name=True`
- Tests use `pytest-asyncio` with `asyncio_mode = "auto"` — all async test functions run automatically
- The `sqs` optional dependency group (`boto3`) is only needed for SQS webhook support
