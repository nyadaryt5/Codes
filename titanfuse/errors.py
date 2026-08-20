class TitanFuseError(Exception):
    """Base error for user-facing failures."""


class ConfigError(TitanFuseError):
    """Invalid training configuration."""


class BackendError(TitanFuseError):
    """Unknown or unavailable training backend."""
