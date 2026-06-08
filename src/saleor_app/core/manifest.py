"""Manifest schemas for the Saleor App Framework."""

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from saleor_app.core.enums import MountType, TargetType
from saleor_app.core.utils import LazyPath, LazyUrl


class Extension(BaseModel):
    """Extension for the Saleor App Framework."""

    label: str
    mount: MountType
    target: TargetType
    permissions: list[str]
    url: AnyHttpUrl | LazyUrl | LazyPath = Field(
        union_mode="left_to_right",
    )

    model_config: ConfigDict = ConfigDict(
        populate_by_name=True,
        validate_by_name=True,
    )


class Manifest(BaseModel):
    """Manifest for the Saleor App Framework."""

    id: str
    permissions: list[str]
    name: str
    version: str
    about: str
    extensions: list[Extension]
    data_privacy_url: AnyHttpUrl | LazyUrl = Field(
        alias="dataPrivacyUrl",
        union_mode="left_to_right",
    )
    homepage_url: AnyHttpUrl | LazyUrl = Field(
        alias="homepageUrl",
        union_mode="left_to_right",
    )
    support_url: AnyHttpUrl | LazyUrl = Field(
        alias="supportUrl",
        union_mode="left_to_right",
    )
    app_url: AnyHttpUrl | LazyUrl = Field(
        alias="appUrl",
        union_mode="left_to_right",
    )
    token_target_url: AnyHttpUrl | LazyUrl = Field(
        default=LazyUrl("app-install", public=False),
        alias="tokenTargetUrl",
        union_mode="left_to_right",
    )

    model_config: ConfigDict = ConfigDict(
        populate_by_name=True,
        validate_by_name=True,
    )
