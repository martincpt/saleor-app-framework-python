# saleor-app-framework-python

Saleor App Framework (Python) provides an easy way to install Your app into the [Saleor Commerce](https://github.com/saleor/saleor).

Supported features:

- Installation
- Webhooks handling (HTTP and SQS)

More on usage You can find in the official [Documentation](https://mirumee.github.io/saleor-app-framework-python/)

## Installation

To use saleor app framework simply install it by

Using [uv](https://docs.astral.sh/uv/)

```
uv add git+https://github.com/martincpt/saleor-app-framework-python.git@main
```

Using [poetry](https://python-poetry.org/)

```
poetry add git+https://github.com/martincpt/saleor-app-framework-python.git@main
```

Using pip

```
pip install git+https://github.com/martincpt/saleor-app-framework-python.git@main
```

## Fork notes

The original repository is pretty much stale and unmaintained. This fork aims to bring it up to date with the latest changes in the Saleor ecosystem.

### Important changes

- **Dependency Management**
  - The project now uses uv for dependency management, replacing poetry.
  - Removed unused runtime dependencies: `aiofiles`, `jinja2`, `uvicorn`.

- **Python Version**
  - The minimum required Python version is now 3.12.

- **Pydantic**
  - Updated to version 2.

- **Package Layout**
  - Removed the `src/` layout. `saleor_app/` now lives at the project root.
  - Tests moved from `saleor_app/tests/` to a top-level `tests/` directory.
  - Added `py.typed` marker (PEP 561) for typed package support.

- **Package Structure**
  - `saleor_app.schemas` renamed to `saleor_app.core`, with internal modules split by domain (`enums`, `types`, `install`, `manifest`, `webhook`, `sqs`).
  - `saleor_app.saleor` renamed to `saleor_app.client`.
  - All enums consolidated into `saleor_app.core.enums`.
  - All type aliases consolidated into `saleor_app.core.types`.
  - Intra-package imports converted to relative imports.

- **SaleorClient**
  - `SaleorClient.for_app(url, manifest, **kwargs)` factory classmethod replaces the standalone `get_client_for_app` helper.

- **Pre-commit Configuration**
  - Flake8 and isort have been replaced by Ruff.
  - MyPy has been added.
  - Resolved all previously suppressed lint ignores (ANN, D-series).

- **GitHub CI**
  - Now configured to use pre-commit.

- **Tox**
  - Tox has been removed.

### Minimum working example

Here is a minimum working example I was able to install my app and receive webhooks.

Manifest URL for local Docker access:

    http://host.docker.internal:5001/configuration/manifest

```python
from pathlib import Path

from fastapi.param_functions import Depends
from fastapi.responses import PlainTextResponse

from saleor_app.app import SaleorApp
from saleor_app.core.enums import SaleorEventType
from saleor_app.core.install import WebhookCredentials
from saleor_app.core.manifest import Manifest
from saleor_app.core.types import DomainName
from saleor_app.core.utils import LazyUrl
from saleor_app.core.webhook import Webhook
from saleor_app.deps import ConfigurationFormDeps, saleor_domain_header

WEBHOOK_CREDENTIALS_FILE = Path("webhook_credentials.json")


async def validate_domain(saleor_domain: DomainName) -> bool:
    print("Called validate_domain", saleor_domain)
    return True


async def store_app_data(
    saleor_domain: DomainName,
    auth_token: str,
    webhook_credentials: WebhookCredentials,
) -> None:
    print("Called store_app_data", saleor_domain, auth_token, webhook_credentials)
    WEBHOOK_CREDENTIALS_FILE.write_text(webhook_credentials.model_dump_json())


async def get_webhook_credentials(saleor_domain: DomainName) -> WebhookCredentials:
    print("Called get_webhook_credentials", saleor_domain)
    return WebhookCredentials.model_validate_json(WEBHOOK_CREDENTIALS_FILE.read_text())


manifest = Manifest(
    id="saleor-simple-sample",
    name="Sample Saleor App",
    version="0.1.0",
    about="Sample Saleor App seving as an example.",
    app_url=LazyUrl("get_data_placeholder"),
    data_privacy_url=LazyUrl("get_data_placeholder"),
    homepage_url=LazyUrl("get_data_placeholder"),
    support_url=LazyUrl("get_data_placeholder"),
    permissions=["MANAGE_PRODUCTS", "MANAGE_USERS"],
    extensions=[],
)


app = SaleorApp(
    manifest=manifest,
    validate_domain=validate_domain,
    store_app_data=store_app_data,
    get_webhook_credentials=get_webhook_credentials,
    # more arguments to come
    use_insecure_saleor_http=True,
    development_auth_token="dev_token",
    servers=[
        {
            "url": "http://host.docker.internal:5001",
            "description": "Local Docker access",
            "public_url": "http://0.0.0.0:5001",
        },
        {
            "url": "http://0.0.0.0:5001",
            "description": "Local development server",
        },
    ],
)


@app.router.get("/data-placeholder", response_class=PlainTextResponse)
async def get_data_placeholder(commons: ConfigurationFormDeps = Depends()) -> str:
    return "This is a placeholder page for data privacy, homepage, and support page."


# ---- Webhooks ----
@app.webhook_router.http_event_route(SaleorEventType.PRODUCT_CREATED)
async def product_created(
    payload: list[Webhook],
    saleor_domain=Depends(saleor_domain_header),
) -> None:
    print("Product created", payload, saleor_domain)


@app.webhook_router.http_event_route(SaleorEventType.PRODUCT_UPDATED)
async def product_updated(
    payload: list[Webhook],
    saleor_domain=Depends(saleor_domain_header),
) -> None:
    print("Product updated", payload, saleor_domain)


@app.webhook_router.http_event_route(SaleorEventType.PRODUCT_DELETED)
async def product_deleted(
    payload: list[Webhook],
    saleor_domain=Depends(saleor_domain_header),
) -> None:
    print("Product deleted", payload, saleor_domain)

```

### For developers

#### Install environment

    uv sync --all-extras --all-groups

#### Install pre-commit hooks

    uv run pre-commit install
