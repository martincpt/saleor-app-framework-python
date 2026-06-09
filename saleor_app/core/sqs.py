"""SQS schemas for the Saleor App Framework."""

from typing import Annotated

from pydantic import AnyUrl, BaseModel, UrlConstraints

from saleor_app.core.types import WebHookHandlerSignature

SQSUrl = Annotated[AnyUrl, UrlConstraints(allowed_schemes=["awssqs"])]


class SQSHandler(BaseModel):
    """SQS handler for the Saleor App Framework."""

    target_url: SQSUrl
    handler: WebHookHandlerSignature
