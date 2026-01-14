"""Webhook schemas for the Saleor App Framework."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict
from pydantic.fields import Field


class WebhookV1(BaseModel):
    """Webhook V1 schema for the Saleor App Framework."""

    model_config: ConfigDict = ConfigDict(
        extra="allow",
        frozen=True,
    )


class PrincipalType(str, Enum):
    """Principal types for the Saleor App Framework."""

    app = "app"
    user = "user"


class Principal(BaseModel):
    """Principal for the Saleor App Framework."""

    id: str = Field(..., description="Unique identifier of the principal")
    type: PrincipalType = Field(..., description="Defines the principal type")


class WebhookMeta(BaseModel):
    """Meta information for the Saleor App Framework Webhook."""

    issuing_principal: Principal
    issued_at: datetime
    cipher_spec: Optional[str]
    format: Optional[str]


class WebhookV2(BaseModel):
    """Webhook V2 schema for the Saleor App Framework."""

    meta: WebhookMeta

    model_config: ConfigDict = ConfigDict(
        extra="allow",
        frozen=True,
    )


class WebhookV3(BaseModel):
    """Webhook V3 schema for the Saleor App Framework."""

    meta: WebhookMeta
    payload: Any

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
    )


Webhook = Union[WebhookV3, WebhookV2, WebhookV1]
