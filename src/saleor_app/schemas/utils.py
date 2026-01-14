from fastapi import Request
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from starlette.routing import NoMatchFound

from saleor_app.errors import ConfigurationError


class LazyUrl(str):
    """
    Used to declare a fully qualified url that is to be resolved when the
    request is available.
    """

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler):
        python_schema = core_schema.union_schema(
            [
                core_schema.is_instance_schema(cls),
                core_schema.str_schema(),
            ]
        )

        return core_schema.no_info_after_validator_function(
            cls.validate,
            python_schema,
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, cls):
            return v
        return cls(v)

    def resolve(self):
        return self.request.url_for(self.name)

    def __call__(self, request: Request):
        self.request = request
        try:
            return str(self.resolve())
        except NoMatchFound:
            raise ConfigurationError(
                f"Failed to resolve a lazy url, check if an endpoint named '{self.name}' is defined."
            )

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not (self.name == other.name)

    def __str__(self):
        return f"LazyURL('{self.name}')"

    def __repr__(self):
        return str(self)


class LazyPath(LazyUrl):
    """
    Much like LazyUrl but resolves only to the path part of an url.
    The lazy aspect of this class is very redundant but is built like so to
    maintain the same usage as the LazyUrl class.
    """

    def resolve(self):
        return self.request.app.url_path_for(self.name)

    def __str__(self):
        return f"LazyPath('{self.name}')"
