from collections.abc import Sequence
from typing import Any


class GraphQLError(Exception):
    """Raised on Saleor GraphQL errors"""

    def __init__(
        self,
        errors: Sequence[dict[str, Any]],
        response_data: dict[str, Any] | None = None,
    ):
        self.errors = errors
        self.response_data = response_data

    def __str__(self):
        return (
            f"GraphQLError: {', '.join([error['message'] for error in self.errors])}."
        )
