# saleor-app-framework-python

Saleor App Framework (Python) provides an easy way to install Your app into the [Saleor Commerce](https://github.com/saleor/saleor).

Supported features:

- Installation
- Webhooks handling
- Exception handling
- Ignoring Webhooks triggered by your app

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
  - The project now utilizes uv for dependency management, replacing poetry.

- **Python Version**
  - The minimum required Python version is now 3.12.

- **Pydantic**:
  - Updated to version 2.

- **Pre-commit Configuration**:
  - Flake8 and isort have been replaced by Ruff.
  - MyPy has been added.

- **GitHub CI**
  - Now configured to use pre-commit.

- **Tox**
  - Tox has been removed, with possible future reconsideration for re-enablement.

### TODO

- Resolve and Remove Ruff Ignores in pyproject.toml
  - Annotation-related: ANN001, ANN201, ANN202, ANN204
  - Docstring-related: D100, D101, D102, D103, D105, D107, D400, D415

- Update documentation and README.md

### Minimum working example

Here is a minimum working example I was able to install my app and receive webhooks.

Manifest URL for local Docker access:

    http://host.docker.internal:5001/configuration/manifest

```python
from fastapi.param_functions import Depends
from fastapi.responses import PlainTextResponse

from saleor_app.app import SaleorApp
from saleor_app.deps import saleor_domain_header
from saleor_app.schemas.handlers import SaleorEventType
from saleor_app.schemas.webhook import Webhook
from saleor_app.deps import ConfigurationFormDeps
from saleor_app.schemas.core import DomainName, WebhookData
from saleor_app.schemas.manifest import Manifest
from saleor_app.schemas.utils import LazyUrl


async def validate_domain(saleor_domain: DomainName) -> bool:
    print("Called validate_domain", saleor_domain)
    return True


stored_webhook: WebhookData


async def store_app_data(
    saleor_domain: DomainName,
    auth_token: str,
    webhook_data: WebhookData,
):
    print("Called store_app_data", saleor_domain, auth_token, webhook_data)
    global stored_webhook
    stored_webhook = webhook_data


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
    save_app_data=store_app_data,
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


app.include_saleor_app_routes()


# ---- WEBHOOK ----
async def get_webhook_details(saleor_domain: DomainName) -> WebhookData:
    return stored_webhook


app.include_webhook_router(get_webhook_details=get_webhook_details)


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
