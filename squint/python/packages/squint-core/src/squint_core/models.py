from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """A model exchanged with TypeScript through Temporal: snake_case in Python, camelCase on
    the wire in both directions."""

    model_config = ConfigDict(
        frozen=True,
        alias_generator=to_camel,
        validate_by_name=True,
        serialize_by_alias=True,
    )
