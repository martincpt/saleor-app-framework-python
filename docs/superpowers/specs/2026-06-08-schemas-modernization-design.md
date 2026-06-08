# Schemas Modernization Design

**Goal:** Rename `saleor_app.schemas` to `saleor_app.core` and `saleor_app.saleor` to `saleor_app.client`, consolidate all enums into `core.enums` and all type aliases into `core.types`, and re-export everything from `core/__init__.py` for clean imports.

**Architecture:** Two packages are renamed and `core/` is internally restructured by domain boundary — each submodule owns one Saleor concept (manifest, webhook, install, sqs) rather than one Python construct type. Enums and type aliases are cross-cutting concerns so they each get a dedicated module. All internal imports are updated; `core/__init__.py` becomes the single public surface.

**Tech Stack:** Python 3.12+, Pydantic v2, FastAPI

---

## Package Renames

| Before | After |
|--------|-------|
| `saleor_app/schemas/` | `saleor_app/core/` |
| `saleor_app/saleor/` | `saleor_app/client/` |

## New `saleor_app/core/` Structure

| File | Contents | Source |
|------|----------|--------|
| `enums.py` | `SaleorPermissions`, `SaleorEventType`, `TargetType`, `MountType`, `PrincipalType` | consolidated from `core.py`, `handlers.py`, `manifest.py`, `webhook.py` |
| `types.py` | `DomainName`, `AppToken`, `Url`, `ValidateDomain`, `StoreAppData`, `GetWebhookCredentials`, `WebhookSubscription`, `WebhookSubscriptionMap`, `WebHookHandlerSignature` | consolidated from `core.py`, `handlers.py` |
| `install.py` | `WebhookCredentials`, `InstallData` | renamed from `core.py` (models only) |
| `manifest.py` | `Extension`, `Manifest` | from `manifest.py` (enums removed) |
| `webhook.py` | `Principal`, `WebhookMeta`, `WebhookV1`, `WebhookV2`, `WebhookV3`, `Webhook` | from `webhook.py` (enum removed) |
| `sqs.py` | `SQSUrl`, `SQSHandler` | renamed from `handlers.py` (enums + type aliases removed) |
| `utils.py` | `LazyUrl`, `LazyPath` | unchanged |
| `exception_handlers.py` | `IgnoredIssuingPrincipalChecker` | unchanged (internal import updated) |
| `__init__.py` | re-exports all public symbols | new |

## New `saleor_app/client/` Structure

All files moved verbatim from `saleor_app/saleor/`. No renames, no content changes — only internal import paths updated from `saleor_app.saleor.*` to `saleor_app.client.*`.

| File | Contents |
|------|----------|
| `__init__.py` | unchanged |
| `client.py` | `SaleorClient` |
| `exceptions.py` | `IgnoredPrincipalError`, others |
| `mutations.py` | GraphQL mutations |
| `utils.py` | utilities |

## Public Import API

After the change, consumers can import from either the flat `core` namespace or directly from submodules:

```python
# flat (preferred for users)
from saleor_app.core import SaleorEventType, SaleorPermissions, Manifest, Webhook

# explicit submodule (acceptable, stable)
from saleor_app.core.enums import SaleorEventType
from saleor_app.core.manifest import Manifest
```

## Files Outside `core/` and `client/` That Need Import Updates

| File | Current import | New import |
|------|---------------|-----------|
| `deps.py` | `from saleor_app.schemas.core import DomainName` | `from saleor_app.core.types import DomainName` |
| `saleor/utils.py` → `client/utils.py` | `from saleor_app.schemas.manifest import Manifest` | `from saleor_app.core.manifest import Manifest` |
| `webhook.py` | `from saleor_app.schemas.handlers import ...` | `from saleor_app.core.sqs import ...` |
| `webhook.py` | `from saleor_app.schemas.webhook import Webhook` | `from saleor_app.core.webhook import Webhook` |
| `core/exception_handlers.py` | `from saleor_app.saleor.exceptions import ...` | `from saleor_app.client.exceptions import ...` |
| all tests | `from saleor_app.schemas.*` | `from saleor_app.core.*` |

## Out of Scope

- No behavioral changes — this is a pure restructure
- No changes to `app.py`, `endpoints.py`, `install.py`, `settings.py`, `errors.py`, `webhook.py` logic
- `saleor_app/__init__.py` still only exports `SaleorApp`
