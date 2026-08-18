"""Exception classes for the Saleor GraphQL client."""

from collections.abc import Sequence
from typing import Any


class GraphQLError(Exception):
    """Raised when the Saleor GraphQL API returns errors."""

    def __init__(
        self,
        errors: Sequence[dict[str, Any]],
        response_data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize GraphQLError with the list of errors and optional response data."""
        self.errors = errors
        self.response_data = response_data

    def __str__(self) -> str:
        """Return a human-readable string of all error messages."""
        return (
            f"GraphQLError: {', '.join([error['message'] for error in self.errors])}."
        )


class IgnoredPrincipalError(Exception):
    """Raised when a webhook event is ignored due to principal ID filtering."""

    message = "Ignore webhook with {} principal ids."

    def __init__(self, principal_ids: list[str]) -> None:
        """Initialize with the list of principal IDs that triggered the ignore."""
        super().__init__(self.message.format(",".join(principal_ids)))
