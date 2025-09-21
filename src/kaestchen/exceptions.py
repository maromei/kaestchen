"""Custom Exceptions for the Kaestchen application."""


class DotEnvFileDoesNotExist(Exception):
    """Inidcates that some ``.env`` file  does not exist."""

    pass


class InvalidPath(Exception):
    """Indicates an invalid path."""

    pass
