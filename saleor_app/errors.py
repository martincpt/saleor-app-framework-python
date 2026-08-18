"""Error classes for the Saleor App Framework."""


class SaleorAppError(Exception):
    """Base error for all Saleor App Framework exceptions."""


class InstallAppError(SaleorAppError):
    """Raised when webhook installation fails during app setup."""


class ConfigurationError(SaleorAppError):
    """Raised when the app is configured incorrectly."""
