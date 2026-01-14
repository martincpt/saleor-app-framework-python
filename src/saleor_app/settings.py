"""Settings for the Saleor App Framework."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class AWSSettings(BaseSettings):
    """AWS settings for the Saleor App Framework.

    Disclaimer: Not sure why are these relevant.
    Since they are not really used, it will maybe be deprecated.
    """

    account_id: str
    access_key_id: str
    secret_access_key: str
    region: str
    endpoint_url: Optional[str] = None

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="AWS_",
    )
