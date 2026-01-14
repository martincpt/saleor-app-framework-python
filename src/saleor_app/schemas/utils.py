"""Schema utilities for the Saleor App Framework."""

from typing import Any

from fastapi import FastAPI, Request
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from starlette.datastructures import URL, URLPath
from starlette.routing import NoMatchFound

from saleor_app.errors import ConfigurationError


class LazyUrl(str):
    """Lazy URL for the Saleor App Framework.

    Used to declare a fully qualified url that is to be resolved when the
    request is available.
    """

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Get Pydantic core schema for the lazy URL."""
        python_schema = core_schema.union_schema(
            [
                core_schema.is_instance_schema(cls),
                core_schema.str_schema(),
            ]
        )

        return core_schema.no_info_after_validator_function(cls.validate, python_schema)

    @classmethod
    def validate(cls, v: "str | LazyUrl") -> "LazyUrl":
        """Validate and coerce input to LazyUrl."""
        if isinstance(v, cls):
            return v

        return cls(v)

    def resolve(self) -> URL:
        """Resolve the lazy URL to a fully qualified URL."""
        return self.request.url_for(self.name)

    def __call__(self, request: Request) -> str:
        """Call the lazy URL with the request context."""
        self.request = request

        try:
            return str(self.resolve())
        except NoMatchFound:
            message = f"Failed to resolve a lazy url, check if an endpoint named '{self.name}' is defined."
            raise ConfigurationError(message)

    def __hash__(self) -> int:
        """Get the hash of the lazy URL."""
        return hash(self.name)

    def __eq__(self, other: "LazyUrl") -> bool:
        """Check equality of lazy URLs."""
        return self.name == other.name

    def __ne__(self, other: "LazyUrl") -> bool:
        """Check inequality of lazy URLs."""
        return not (self.name == other.name)

    def __str__(self) -> str:
        """String representation of the lazy URL."""
        return f"LazyURL('{self.name}')"

    def __repr__(self) -> str:
        """Representation of the lazy URL."""
        return str(self)


class LazyPath(LazyUrl):
    """Lazy path for the Saleor App Framework.

    Much like LazyUrl but resolves only to the path part of an url.
    The lazy aspect of this class is very redundant but is built like so to
    maintain the same usage as the LazyUrl class.
    """

    def resolve(self) -> URLPath:
        """Resolve the lazy path to a fully qualified path."""
        assert isinstance(self.request.app, FastAPI)
        return self.request.app.url_path_for(self.name)

    def __str__(self) -> str:
        """String representation of the lazy path."""
        return f"LazyPath('{self.name}')"
