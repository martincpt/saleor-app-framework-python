import hashlib
import hmac
import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

import jwt
from fastapi import Depends, Header, HTTPException, Query, Request

from saleor_app.saleor.exceptions import GraphQLError
from saleor_app.saleor.mutations import VERIFY_TOKEN
from saleor_app.saleor.utils import get_client_for_app
from saleor_app.schemas.core import DomainName

from .schemas.core import SaleorPermissions

if TYPE_CHECKING:
    from .app import SaleorApp


logger = logging.getLogger(__name__)

SALEOR_DOMAIN_HEADER = "x-saleor-domain"
SALEOR_TOKEN_HEADER = "x-saleor-token"  # noqa: S105
SALEOR_SIGNATURE_HEADER = "x-saleor-signature"


def saleor_app(request: Request) -> "SaleorApp":
    """Get the SaleorApp instance from the request."""
    return request.app


async def saleor_domain_header(
    saleor_domain: str | None = Header(None, alias=SALEOR_DOMAIN_HEADER),
) -> DomainName:
    if not saleor_domain:
        logger.warning(f"Missing {SALEOR_DOMAIN_HEADER.upper()} header.")
        raise HTTPException(
            status_code=400,
            detail=f"Missing {SALEOR_DOMAIN_HEADER.upper()} header.",
        )
    return saleor_domain


async def saleor_token(
    saleor_app: "SaleorApp" = Depends(saleor_app),
    token: str | None = Header(None, alias=SALEOR_TOKEN_HEADER),
) -> str:
    """Get the Saleor token from the request headers.

    I'm still trying to figure out what is `saleor_token` and how does it differ
    from `saleor_domain_header`, and wether `development_auth_token`
    makes any sense here.
    """
    if saleor_app.development_auth_token:
        token = token or saleor_app.development_auth_token

    if not token:
        message = f"Missing {SALEOR_TOKEN_HEADER.upper()} header."
        logger.warning(message)
        raise HTTPException(status_code=400, detail=message)

    return token


async def verify_saleor_token(
    saleor_app: "SaleorApp" = Depends(saleor_app),
    saleor_domain: DomainName = Depends(saleor_domain_header),
    token: str = Depends(saleor_token),
) -> bool:
    schema = "http" if saleor_app.use_insecure_saleor_http else "https"
    url = f"{schema}://{saleor_domain}"

    async with get_client_for_app(url, manifest=saleor_app.manifest) as saleor_client:
        try:
            response = await saleor_client.execute(
                query=VERIFY_TOKEN,
                variables={"token": token},
            )
        except GraphQLError:
            return False

    try:
        is_valid = response["tokenVerify"]["isValid"] is True
    except KeyError:
        is_valid = False

    if not is_valid:
        message = (
            f"Provided {SALEOR_DOMAIN_HEADER.upper()} and "
            f"{SALEOR_TOKEN_HEADER.upper()} are incorrect."
        )
        logger.warning(message)
        raise HTTPException(status_code=400, detail=message)

    return True


async def verify_saleor_domain(
    saleor_app: "SaleorApp" = Depends(saleor_app),
    saleor_domain: DomainName = Depends(saleor_domain_header),
) -> bool:
    domain_is_valid = await saleor_app.validate_domain(saleor_domain)

    if not domain_is_valid:
        logger.warning(f"Provided domain {saleor_domain} is invalid.")
        raise HTTPException(
            status_code=400,
            detail=f"Provided domain {saleor_domain} is invalid.",
        )

    return True


async def verify_webhook_signature(
    request: Request,
    saleor_app: "SaleorApp" = Depends(saleor_app),
    signature: str | None = Header(None, alias=SALEOR_SIGNATURE_HEADER),
    domain_name: DomainName = Depends(saleor_domain_header),
) -> None:
    if not signature:
        raise HTTPException(
            status_code=401,
            detail=(f"Missing signature header - {SALEOR_SIGNATURE_HEADER}"),
        )

    webhook_details = await saleor_app.get_webhook_details(domain_name)
    content = await request.body()
    webhook_signature_bytes = bytes(signature, "utf-8")

    secret_key_bytes = bytes(webhook_details.webhook_secret_key, "utf-8")
    content_signature_str = hmac.new(
        secret_key_bytes,
        content,
        hashlib.sha256,
    ).hexdigest()
    content_signature = bytes(content_signature_str, "utf-8")

    if not hmac.compare_digest(content_signature, webhook_signature_bytes):
        raise HTTPException(
            status_code=401,
            detail=f"Invalid webhook signature for {SALEOR_SIGNATURE_HEADER}",
        )


def require_permission(permissions: list[SaleorPermissions]) -> Callable[..., None]:
    """Validates is the requesting principal is authorized for the specified action

    Usage:

    ```
    Depends(require_permission([SaleorPermissions.MANAGE_PRODUCTS]))
    ```
    """

    def func(
        saleor_token: str = Depends(saleor_token),
        _saleor_domain: DomainName = Depends(saleor_domain_header),
        _token_is_valid: bool = Depends(verify_saleor_token),
    ) -> None:
        jwt_payload = jwt.decode(
            saleor_token,
            algorithms=["RS256"],
            options={"verify_signature": False},
        )
        user_permissions = set(jwt_payload.get("permissions", []))

        if not {p.value for p in permissions} - user_permissions:
            return

        raise HTTPException(status_code=403, detail="Unauthorized user")

    return func


class ConfigurationFormDeps:
    def __init__(
        self,
        request: Request,
        domain=Query(...),
    ):
        self.request = request
        self.saleor_domain = domain


class ConfigurationDataDeps:
    def __init__(
        self,
        request: Request,
        saleor_domain=Depends(saleor_domain_header),
        _domain_is_valid=Depends(verify_saleor_domain),
        _token_is_valid=Depends(verify_saleor_token),
        token=Depends(saleor_token),
    ):
        self.request = request
        self.saleor_domain = saleor_domain
        self.token = token
