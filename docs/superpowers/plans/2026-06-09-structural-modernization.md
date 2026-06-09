# Structural Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the `src` layout, move tests to top-level `tests/`, enforce relative imports within the package hierarchy, clean up unused dependencies, and add a `py.typed` marker.

**Architecture:** Pure structural refactor — no behavioral changes. Files are moved with `git mv` to preserve history, then `pyproject.toml` is updated, then all intra-package imports are converted to relative where appropriate.

**Tech Stack:** Python 3.12+, uv, ruff, black, pytest

---

## Files Created / Modified / Deleted

| Action | Path |
|--------|------|
| Move | `src/saleor_app/tests/` → `tests/` |
| Move | `src/saleor_app/` → `saleor_app/` |
| Delete | `src/` (empty after moves) |
| Create | `saleor_app/py.typed` |
| Modify | `pyproject.toml` |
| Modify | `saleor_app/deps.py` |
| Modify | `saleor_app/webhook.py` |
| Modify | `saleor_app/core/__init__.py` |
| Modify | `saleor_app/core/manifest.py` |
| Modify | `saleor_app/core/webhook.py` |
| Modify | `saleor_app/core/types.py` |
| Modify | `saleor_app/core/sqs.py` |
| Modify | `saleor_app/client/client.py` |
| Modify | `saleor_app/client/utils.py` |

---

## Task 1: Move files and create py.typed

**Files:**
- Move: `src/saleor_app/tests/` → `tests/`
- Move: `src/saleor_app/` → `saleor_app/`
- Delete: `src/`
- Create: `saleor_app/py.typed`

- [ ] **Step 1: Move tests out of the package first**

```bash
git mv src/saleor_app/tests tests
```

This extracts `tests/` to the project root before moving the package, so git tracks the rename correctly.

- [ ] **Step 2: Move the package to root**

```bash
git mv src/saleor_app saleor_app
```

- [ ] **Step 3: Remove the now-empty src/ directory**

```bash
rmdir src
```

- [ ] **Step 4: Create the py.typed marker**

```bash
touch saleor_app/py.typed
git add saleor_app/py.typed
```

- [ ] **Step 5: Verify the new layout**

```bash
ls saleor_app/
ls tests/
```

Expected `saleor_app/`: `__init__.py  app.py  client/  core/  deps.py  endpoints.py  errors.py  install.py  py.typed  settings.py  webhook.py`

Expected `tests/`: `__init__.py  client/  conftest.py  test_app.py  test_deps.py  test_endpoints.py  test_install.py`

---

## Task 2: Update pyproject.toml and resync

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Remove unused runtime dependencies**

In `[project]`, change `dependencies` from:
```toml
dependencies = [
    "aiofiles>=20.0.0",
    "aiohttp>=3.0.0",
    "fastapi>=0.110.0",
    "jinja2>=2.11.0",
    "PyJWT>=2.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "uvicorn>=0.35.0",
]
```
To:
```toml
dependencies = [
    "aiohttp>=3.0.0",
    "fastapi>=0.110.0",
    "PyJWT>=2.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
]
```

- [ ] **Step 2: Update pytest testpaths**

In `[tool.pytest.ini_options]`, change:
```toml
testpaths = ["src/saleor_app/tests"]
```
To:
```toml
testpaths = ["tests"]
```

- [ ] **Step 3: Update coverage source and omit**

In `[tool.coverage.run]`, change:
```toml
source = ["src"]
omit = ['src/saleor_app/tests/']
```
To:
```toml
source = ["saleor_app"]
omit = ['tests/']
```

- [ ] **Step 4: Update ruff per-file-ignores**

In `[tool.ruff.lint.per-file-ignores]`, change:
```toml
"src/saleor_app/tests/*" = ["ARG001", "PLR2004", "S106"]
```
To:
```toml
"tests/*" = ["ARG001", "PLR2004", "S106"]
```

- [ ] **Step 5: Remove the dead [tool.isort] section**

Delete the entire block from the bottom of `pyproject.toml`:
```toml
[tool.isort] # this can be removed once ruff installed
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
line_length = 88
```

- [ ] **Step 6: Resync uv to apply dependency changes**

```bash
uv sync --all-extras --all-groups
```

Expected: uv removes `aiofiles`, `jinja2`, `uvicorn` from the lock file and reinstalls the package from its new root location.

- [ ] **Step 7: Run tests to confirm the layout change works**

```bash
uv run pytest --tb=short -q
```

Expected: `28 passed` — all tests pass with new paths before any import changes.

- [ ] **Step 8: Commit the layout and config changes**

```bash
git add pyproject.toml uv.lock
git commit -m "refactor: remove src layout, move tests to root, add py.typed"
```

---

## Task 3: Update relative imports in saleor_app/*.py

**Files:**
- Modify: `saleor_app/deps.py`
- Modify: `saleor_app/webhook.py`

- [ ] **Step 1: Update deps.py — replace 4 absolute imports with relative**

In `saleor_app/deps.py`, change the import block from:
```python
from saleor_app.client.exceptions import GraphQLError
from saleor_app.client.mutations import VERIFY_TOKEN
from saleor_app.client.utils import get_client_for_app
from saleor_app.core.types import DomainName

from .core.enums import SaleorPermissions
```
To:
```python
from .client.exceptions import GraphQLError
from .client.mutations import VERIFY_TOKEN
from .client.utils import get_client_for_app
from .core.enums import SaleorPermissions
from .core.types import DomainName
```

- [ ] **Step 2: Update webhook.py — replace 4 absolute imports with relative**

In `saleor_app/webhook.py`, change:
```python
from saleor_app.core.enums import SaleorEventType
from saleor_app.core.sqs import SQSHandler, SQSUrl
from saleor_app.core.types import WebHookHandlerSignature
from saleor_app.core.webhook import Webhook
```
To:
```python
from .core.enums import SaleorEventType
from .core.sqs import SQSHandler, SQSUrl
from .core.types import WebHookHandlerSignature
from .core.webhook import Webhook
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest --tb=short -q
```

Expected: `28 passed`

---

## Task 4: Update relative imports in saleor_app/core/

**Files:**
- Modify: `saleor_app/core/__init__.py`
- Modify: `saleor_app/core/manifest.py`
- Modify: `saleor_app/core/webhook.py`
- Modify: `saleor_app/core/types.py`
- Modify: `saleor_app/core/sqs.py`

- [ ] **Step 1: Update core/__init__.py — all 7 absolute imports become relative**

Replace the import block at the top of `saleor_app/core/__init__.py` from:
```python
from saleor_app.core.enums import (
    MountType,
    PrincipalType,
    SaleorEventType,
    SaleorPermissions,
    TargetType,
)
from saleor_app.core.install import InstallData, WebhookCredentials
from saleor_app.core.manifest import Extension, Manifest
from saleor_app.core.sqs import SQSHandler, SQSUrl
from saleor_app.core.types import (
    AppToken,
    DomainName,
    GetWebhookCredentials,
    StoreAppData,
    Url,
    ValidateDomain,
    WebHookHandlerSignature,
    WebhookSubscription,
    WebhookSubscriptionMap,
)
from saleor_app.core.utils import LazyPath, LazyUrl
from saleor_app.core.webhook import (
    Principal,
    Webhook,
    WebhookMeta,
    WebhookV1,
    WebhookV2,
    WebhookV3,
)
```
To:
```python
from .enums import (
    MountType,
    PrincipalType,
    SaleorEventType,
    SaleorPermissions,
    TargetType,
)
from .install import InstallData, WebhookCredentials
from .manifest import Extension, Manifest
from .sqs import SQSHandler, SQSUrl
from .types import (
    AppToken,
    DomainName,
    GetWebhookCredentials,
    StoreAppData,
    Url,
    ValidateDomain,
    WebHookHandlerSignature,
    WebhookSubscription,
    WebhookSubscriptionMap,
)
from .utils import LazyPath, LazyUrl
from .webhook import (
    Principal,
    Webhook,
    WebhookMeta,
    WebhookV1,
    WebhookV2,
    WebhookV3,
)
```

- [ ] **Step 2: Update core/manifest.py — 2 absolute imports become relative**

In `saleor_app/core/manifest.py`, change:
```python
from saleor_app.core.enums import MountType, TargetType
from saleor_app.core.utils import LazyPath, LazyUrl
```
To:
```python
from .enums import MountType, TargetType
from .utils import LazyPath, LazyUrl
```

- [ ] **Step 3: Update core/webhook.py — 1 absolute import becomes relative**

In `saleor_app/core/webhook.py`, change:
```python
from saleor_app.core.enums import PrincipalType
```
To:
```python
from .enums import PrincipalType
```

- [ ] **Step 4: Update core/types.py — 3 absolute imports become relative**

In `saleor_app/core/types.py`, change:
```python
from saleor_app.core.enums import SaleorEventType
from saleor_app.core.install import WebhookCredentials
from saleor_app.core.webhook import Webhook
```
To:
```python
from .enums import SaleorEventType
from .install import WebhookCredentials
from .webhook import Webhook
```

- [ ] **Step 5: Update core/sqs.py — 1 absolute import becomes relative**

In `saleor_app/core/sqs.py`, change:
```python
from saleor_app.core.types import WebHookHandlerSignature
```
To:
```python
from .types import WebHookHandlerSignature
```

- [ ] **Step 6: Run tests**

```bash
uv run pytest --tb=short -q
```

Expected: `28 passed`

---

## Task 5: Update relative imports in saleor_app/client/

**Files:**
- Modify: `saleor_app/client/client.py`
- Modify: `saleor_app/client/utils.py`

- [ ] **Step 1: Update client/client.py — 1 absolute import becomes relative**

In `saleor_app/client/client.py`, change:
```python
from saleor_app.client.exceptions import GraphQLError
```
To:
```python
from .exceptions import GraphQLError
```

- [ ] **Step 2: Update client/utils.py — 1 of 2 absolute imports becomes relative**

In `saleor_app/client/utils.py`, change:
```python
from saleor_app.client.client import SaleorClient
from saleor_app.core.manifest import Manifest
```
To:
```python
from saleor_app.core.manifest import Manifest

from .client import SaleorClient
```

(`saleor_app.core.manifest` stays absolute — it is a cross-package import from `client/` into `core/`.)

- [ ] **Step 3: Run full test suite and linters**

```bash
uv run pytest --tb=short -q
uv run ruff check .
uv run mypy saleor_app/
```

Expected: `28 passed`, ruff clean, mypy clean.

- [ ] **Step 4: Commit**

```bash
git add saleor_app/
git commit -m "refactor: use relative imports within package hierarchy"
```
