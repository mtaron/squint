import os


class ConfigError(RuntimeError):
    """A required setting is missing from the environment."""


def require_env(name: str) -> str:
    """Return the environment variable `name`, or raise if it is unset or empty."""
    value = os.environ.get(name)
    if not value:
        raise ConfigError(f"required environment variable {name} is not set")
    return value
