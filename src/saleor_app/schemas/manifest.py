"""Manifest schemas for the Saleor App Framework."""

from enum import Enum
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from saleor_app.schemas.utils import LazyPath, LazyUrl


class TargetType(str, Enum):
    """Target types for the Saleor App Framework."""

    POPUP = "POPUP"
    APP_PAGE = "APP_PAGE"


class MountType(str, Enum):
    """Mount types for the Saleor App Framework."""

    CUSTOMER_DETAILS_MORE_ACTIONS = "CUSTOMER_DETAILS_MORE_ACTIONS"
    CUSTOMER_OVERVIEW_CREATE = "CUSTOMER_OVERVIEW_CREATE"
    CUSTOMER_OVERVIEW_MORE_ACTIONS = "CUSTOMER_OVERVIEW_MORE_ACTIONS"

    NAVIGATION_CATALOG = "NAVIGATION_CATALOG"
    NAVIGATION_CUSTOMERS = "NAVIGATION_CUSTOMERS"
    NAVIGATION_DISCOUNTS = "NAVIGATION_DISCOUNTS"
    NAVIGATION_ORDERS = "NAVIGATION_ORDERS"
    NAVIGATION_PAGES = "NAVIGATION_PAGES"
    NAVIGATION_TRANSLATIONS = "NAVIGATION_TRANSLATIONS"

    ORDER_DETAILS_MORE_ACTIONS = "ORDER_DETAILS_MORE_ACTIONS"
    ORDER_OVERVIEW_CREATE = "ORDER_OVERVIEW_CREATE"
    ORDER_OVERVIEW_MORE_ACTIONS = "ORDER_OVERVIEW_MORE_ACTIONS"

    PRODUCT_DETAILS_MORE_ACTIONS = "PRODUCT_DETAILS_MORE_ACTIONS"
    PRODUCT_OVERVIEW_CREATE = "PRODUCT_OVERVIEW_CREATE"
    PRODUCT_OVERVIEW_MORE_ACTIONS = "PRODUCT_OVERVIEW_MORE_ACTIONS"


class Extension(BaseModel):
    """Extension for the Saleor App Framework."""

    label: str
    mount: MountType
    target: TargetType
    permissions: List[str]
    url: Union[AnyHttpUrl, LazyUrl, LazyPath] = Field(
        union_mode="left_to_right",
    )

    model_config: ConfigDict = ConfigDict(
        populate_by_name=True,
        validate_by_name=True,
    )


class Manifest(BaseModel):
    """Manifest for the Saleor App Framework."""

    id: str
    permissions: List[str]
    name: str
    version: str
    about: str
    extensions: List[Extension]
    data_privacy: str = Field(..., alias="dataPrivacy")
    data_privacy_url: Union[AnyHttpUrl, LazyUrl] = Field(
        alias="dataPrivacyUrl",
        union_mode="left_to_right",
    )
    homepage_url: Union[AnyHttpUrl, LazyUrl] = Field(
        alias="homepageUrl",
        union_mode="left_to_right",
    )
    support_url: Union[AnyHttpUrl, LazyUrl] = Field(
        alias="supportUrl",
        union_mode="left_to_right",
    )
    configuration_url: Optional[Union[AnyHttpUrl, LazyUrl]] = Field(
        default=None,
        alias="configurationUrl",
        union_mode="left_to_right",
    )
    app_url: Union[AnyHttpUrl, LazyUrl] = Field(
        alias="appUrl",
        union_mode="left_to_right",
    )
    token_target_url: Union[AnyHttpUrl, LazyUrl] = Field(
        default=LazyUrl("app-install"),
        alias="tokenTargetUrl",
        union_mode="left_to_right",
    )

    model_config: ConfigDict = ConfigDict(
        populate_by_name=True,
        validate_by_name=True,
    )
