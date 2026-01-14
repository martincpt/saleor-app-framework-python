from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict
from pydantic.fields import Field


class WebhookV1(BaseModel):
    model_config: ConfigDict = ConfigDict(
        extra="allow",
        frozen=True,
    )


class PrincipalType(str, Enum):
    app = "app"
    user = "user"


class Principal(BaseModel):
    id: str = Field(..., description="Unique identifier of the principal")
    type: PrincipalType = Field(..., description="Defines the principal type")


class WebhookMeta(BaseModel):
    issuing_principal: Principal
    issued_at: datetime
    cipher_spec: Optional[str]
    format: Optional[str]


class WebhookV2(BaseModel):
    meta: WebhookMeta

    model_config: ConfigDict = ConfigDict(
        extra="allow",
        frozen=True,
    )


class WebhookV3(BaseModel):
    meta: WebhookMeta
    payload: Any

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        frozen=True,
    )


Webhook = Union[WebhookV3, WebhookV2, WebhookV1]
