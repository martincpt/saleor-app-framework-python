# saleor-app-framework-python

Saleor App Framework (Python) provides an easy way to install Your app into the [Saleor Commerce](https://github.com/saleor/saleor).

Supported features:

- Installation
- Webhooks handling
- Exception handling
- Ignoring Webhooks triggered by your app

More on usage You can find in the official [Documentation](https://mirumee.github.io/saleor-app-framework-python/)

## Fork notes

The original repository is pretty much stale and unmaintained. This fork aims to bring it up to date with the latest changes in the Saleor ecosystem.

### Important changes

- Project now uses uv instead of poetry
- Minimum python version is now 3.12
- Pydantic has been updated to v2
- Pre-commit configuration has been changed
  - Flake8 and isort is replaced by Ruff
  - MyPy has been added
- Github ci is planned to be changed to use pre-commit
- Tox has been removed a while ago (not sure if it will be re-enabled)

### TODO

- Change github ci
- Following annotation related ruff ignores should be resolved and removed from pyproject.toml
  - ANN001
  - ANN201
  - ANN202
  - ANN204
- Following docstring related ruff ignores should be resolved and removed from pyproject.toml
  - D100
  - D101
  - D102
  - D103
  - D105
  - D107
  - D400
  - D415
- Documentation should be updated

### Minimum working example

Here is a minimum working example I was able to install my app and receive webhooks:

```python
import json

from fastapi.param_functions import Depends
from fastapi.responses import HTMLResponse, PlainTextResponse

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
    name="Sample Saleor App",
    version="0.1.0",
    about="Sample Saleor App seving as an example.",
    app_url="get_data_placeholder",
    data_privacy="Data privacy for manifest",
    data_privacy_url="get_data_placeholder",
    homepage_url="get_data_placeholder",
    support_url="get_data_placeholder",
    id="saleor-simple-sample",
    permissions=["MANAGE_PRODUCTS", "MANAGE_USERS"],
    configuration_url=LazyUrl("configuration-form"),
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
        }
    ],
)


@app.route("/data-placeholder")
async def get_data_placeholder() -> str:
    return "This is a placeholder page for data privacy, homepage, and support page."


@app.configuration_router.get(
    "/",
    response_class=HTMLResponse,
    name="configuration-form",
)
async def get_public_form(commons: ConfigurationFormDeps = Depends()):
    context = {
        "request": str(commons.request),
        "form_url": str(commons.request.url),
        "saleor_domain": commons.saleor_domain,
    }
    return PlainTextResponse(json.dumps(context, indent=4))


app.include_saleor_app_routes()


# ---- WEBHOOK -----
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

### Fork notes end

The rest of the read me from this point is the original one.

## Installation

To use saleor app framework simply install it by

Using [poetry](https://python-poetry.org/)

```
poetry add git+https://github.com/saleor/saleor-app-framework-python.git@main
```

Using pip

```
pip install git+https://github.com/saleor/saleor-app-framework-python.git@main
```

## Usage

The recommended way of building Saleor Python Applications using this framework, is to use project template from [saleor-app-template](https://github.com/mirumee/saleor-app-template). This template will save You a lot of time configuring Your project.

It is preconfigured to use:

- uvicorn [[and gunicorn](https://gunicorn.org/)] - as HTTP server
- [SQLAlchemy](https://docs.sqlalchemy.org/en/14/core/) - as an ORM
- [alembic](https://alembic.sqlalchemy.org/en/latest/) - as a database migration tool with configured migration names, black and isort
- [encode/databases](https://www.encode.io/databases/) - as an asyncio support for SQLAlchemy
- [pytest](https://docs.pytest.org/en/7.1.x/) - for unit tests
- [poetry](https://python-poetry.org/) - as python package manager

With this template You will get:

- working Dockerfile and docker-compose.yaml
- working database with async support
- working configured tests
- working Saleor installation process

You can always develop Your own application from scratch, basing on the steps from [Documentation](https://mirumee.github.io/saleor-app-framework-python/) or change any of the existing tools.

<br/>

## Development

### Tox

To execeute tests with tox just invoke `tox` or `tox -p`. The tox-poetry plugin will read pyproject.toml and handle the envs creation. In case of a change in the dependencies you can force a recreation of the envs with `tox -r`.

One might also want to just run a specific testenv like: `tox -e coverage`.
To reduce the noisy output use `-q` like: `tox -p -q`

<br/>

## Deployment

#### Gunicorn

Here's an example `gunicorn.conf.py` file:

```python
from my_app.settings import LOGGING

workers = 2
keepalive = 30
worker_class = "uvicorn.workers.UvicornH11Worker"
bind = ["0.0.0.0:8080"]

accesslog = "-"
errorlog = "-"
loglevel = "info"
logconfig_dict = LOGGING

forwarded_allow_ips = "*"
```

It's a good starting point, keeps the log config in one place and includes the very important (`forwarded_allow_ips` flag)[https://docs.gunicorn.org/en/stable/settings.html#forwarded-allow-ips] **this flag needs to be understood when deploying your app** - it's not always safe to set it to `*` but in some setups it's the only option to allow FastAPI to generate proper urls with `url_for`.
