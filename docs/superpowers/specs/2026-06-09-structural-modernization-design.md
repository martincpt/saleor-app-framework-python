# Structural Modernization Design

**Goal:** Remove the `src` layout, move tests to a top-level `tests/` directory, enforce relative imports within the package hierarchy, clean up unused dependencies, and add a `py.typed` marker.

**Architecture:** Pure structural refactor — no behavioral changes. Files move, import paths update, and tooling config is tightened. All existing tests must pass unchanged after the restructure.

**Tech Stack:** Python 3.12+, uv, ruff, black, pytest

---

## 1. File Layout

### Before
```
src/
  saleor_app/
    __init__.py
    app.py
    deps.py
    endpoints.py
    errors.py
    install.py
    settings.py
    webhook.py
    client/
      __init__.py
      client.py
      exceptions.py
      mutations.py
      utils.py
    core/
      __init__.py
      enums.py
      exception_handlers.py
      install.py
      manifest.py
      sqs.py
      types.py
      utils.py
      webhook.py
    tests/
      __init__.py
      conftest.py
      test_app.py
      test_deps.py
      test_endpoints.py
      test_install.py
      client/
        __init__.py
        test_client.py
```

### After
```
saleor_app/                     ← moved from src/saleor_app/
  py.typed                      ← new, empty, PEP 561
  __init__.py
  app.py
  deps.py
  endpoints.py
  errors.py
  install.py
  settings.py
  webhook.py
  client/
    __init__.py
    client.py
    exceptions.py
    mutations.py
    utils.py
  core/
    __init__.py
    enums.py
    exception_handlers.py
    install.py
    manifest.py
    sqs.py
    types.py
    utils.py
    webhook.py
tests/                          ← moved from src/saleor_app/tests/
  __init__.py
  conftest.py
  test_app.py
  test_deps.py
  test_endpoints.py
  test_install.py
  client/
    __init__.py
    test_client.py
```

The `src/` directory is deleted after the move.

---

## 2. Relative Import Rule

| File location | Import target | Required style |
|---------------|--------------|----------------|
| `saleor_app/*.py` | `saleor_app.core.*` or `saleor_app.client.*` | `from .core.x import Y` (relative — direct children) |
| `saleor_app/core/*.py` | sibling in `core/` | `from .x import Y` (relative — siblings) |
| `saleor_app/client/*.py` | sibling in `client/` | `from .x import Y` (relative — siblings) |
| `saleor_app/core/*.py` | `saleor_app.errors` (parent-level module) | `from saleor_app.errors import Y` (absolute — no `..`) |
| `saleor_app/client/*.py` | `saleor_app.core.*` (sibling package) | `from saleor_app.core.x import Y` (absolute — cross-package) |
| `tests/*.py` | anything in `saleor_app` | always absolute (external consumer) |

### Specific changes required

**`saleor_app/deps.py`** — three absolute imports become relative:
- `from saleor_app.client.exceptions import GraphQLError` → `from .client.exceptions import GraphQLError`
- `from saleor_app.client.mutations import VERIFY_TOKEN` → `from .client.mutations import VERIFY_TOKEN`
- `from saleor_app.client.utils import get_client_for_app` → `from .client.utils import get_client_for_app`
- `from saleor_app.core.types import DomainName` → `from .core.types import DomainName`

**`saleor_app/webhook.py`** — four absolute imports become relative:
- `from saleor_app.core.enums import SaleorEventType` → `from .core.enums import SaleorEventType`
- `from saleor_app.core.sqs import SQSHandler, SQSUrl` → `from .core.sqs import SQSHandler, SQSUrl`
- `from saleor_app.core.types import WebHookHandlerSignature` → `from .core.types import WebHookHandlerSignature`
- `from saleor_app.core.webhook import Webhook` → `from .core.webhook import Webhook`

**`saleor_app/core/__init__.py`** — all eight absolute imports become relative siblings:
- `from saleor_app.core.enums import (...)` → `from .enums import (...)`
- `from saleor_app.core.exception_handlers import ...` → `from .exception_handlers import ...`
- `from saleor_app.core.install import ...` → `from .install import ...`
- `from saleor_app.core.manifest import ...` → `from .manifest import ...`
- `from saleor_app.core.sqs import ...` → `from .sqs import ...`
- `from saleor_app.core.types import (...)` → `from .types import (...)`
- `from saleor_app.core.utils import ...` → `from .utils import ...`
- `from saleor_app.core.webhook import (...)` → `from .webhook import (...)`

**`saleor_app/core/manifest.py`**:
- `from saleor_app.core.enums import MountType, TargetType` → `from .enums import MountType, TargetType`
- `from saleor_app.core.utils import LazyPath, LazyUrl` → `from .utils import LazyPath, LazyUrl`

**`saleor_app/core/webhook.py`**:
- `from saleor_app.core.enums import PrincipalType` → `from .enums import PrincipalType`

**`saleor_app/core/types.py`**:
- `from saleor_app.core.enums import SaleorEventType` → `from .enums import SaleorEventType`
- `from saleor_app.core.install import WebhookCredentials` → `from .install import WebhookCredentials`
- `from saleor_app.core.webhook import Webhook` → `from .webhook import Webhook`

**`saleor_app/core/sqs.py`**:
- `from saleor_app.core.types import WebHookHandlerSignature` → `from .types import WebHookHandlerSignature`

**`saleor_app/client/client.py`**:
- `from saleor_app.client.exceptions import GraphQLError` → `from .exceptions import GraphQLError`

**`saleor_app/client/utils.py`**:
- `from saleor_app.client.client import SaleorClient` → `from .client import SaleorClient`
- `from saleor_app.core.manifest import Manifest` → stays absolute (cross-package)

**`saleor_app/core/utils.py`**:
- `from saleor_app.errors import ConfigurationError` → stays absolute (parent-level, no `..`)

**`saleor_app/core/exception_handlers.py`**:
- `from saleor_app.client.exceptions import IgnoredPrincipalError` → stays absolute (cross-package)

---

## 3. pyproject.toml Changes

| Setting | Before | After |
|---------|--------|-------|
| `[tool.pytest.ini_options] testpaths` | `["src/saleor_app/tests"]` | `["tests"]` |
| `[tool.coverage.run] source` | `["src"]` | `["saleor_app"]` |
| `[tool.coverage.run] omit` | `['src/saleor_app/tests/']` | `['tests/']` |
| `[tool.ruff.lint.per-file-ignores]` key | `"src/saleor_app/tests/*"` | `"tests/*"` |
| `[tool.isort]` section | present | removed entirely |
| `[project.dependencies]` | includes `aiofiles`, `jinja2`, `uvicorn` | those three removed |

---

## 4. Dependency Cleanup

Remove from `[project.dependencies]` — not imported anywhere in the source:
- `aiofiles`
- `jinja2`
- `uvicorn`

---

## 5. py.typed Marker

Create empty `saleor_app/py.typed` file (PEP 561). This signals to mypy, pyright, and Pylance that the package ships its own type information and they should use inline annotations rather than stubs.

---

## Out of Scope

- Docstrings and type annotations (Plan 2)
- Any behavioral changes
- Changes to `mkdocs.yml` or docs content
