"""Handles the logging setup for the entire ``kaestchen`` application

More detailed information about the implementation of logging can be found
in the :ref:`architecture reference <architecture_logging>`.

The center piece of this module is the :py:class:`LoggingManager` class.

Examples:

    To setup logging for the entire application, you can run:

    .. code-block:: python

        from logging import LoggingManager
        LoggingManager.setup_logging()

    The method calls pythons ``logging.config.dictConfig(config)`` function
    internally.
"""

import copy
import json
import logging.config

from typing import Final, Any, cast
from pathlib import Path

from kaestchen.conf import settings
from kaestchen.exceptions import InvalidPath


#: Template for pythons logging dictconfig formatters
#:
#: This only serves as a template. While most of the configuration is done in this
#: inline data object, the :py:class:`LoggingManager` is used for adjusting and
#: initializing the logging config.
FORMATTERS_BASE: Final[dict] = {
    "default": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
}


#: Template for pythons logging dictconfig handlers
#:
#: This only serves as a template. While most of the configuration is done in this
#: inline data object, the :py:class:`LoggingManager` is used for adjusting and
#: initializing the logging config.
HANDLERS_BASE: Final[dict] = {
    "tests_file": {
        "formatter": "default",
        "level": "DEBUG",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": "kaestchen_tests.log",
        "mode": "a",
        "maxBytes": 1 * 1024 * 1024,  # 1 MB
        "backupCount": 0,
    }
}


#: Template for pythons logging dictconfig loggers
#:
#: This only serves as a template. While most of the configuration is done in this
#: inline data object, the :py:class:`LoggingManager` is used for adjusting and
#: initializing the logging config.
LOGGERS_BASE: Final[dict] = {
    "tests": {"level": "DEBUG", "handlers": ["tests_file"], "propagate": True}
}


#: Template for pythons logging dictconfig
#:
#: This only serves as a template. While most of the configuration is done in this
#: inline data object, the :py:class:`LoggingManager` is used for adjusting and
#: initializing the logging config.
LOGGING_CONFIG_BASE: Final[dict] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": FORMATTERS_BASE,
    "handlers": HANDLERS_BASE,
    "loggers": LOGGERS_BASE,
}


class LoggingManager:
    """Manages the configuration of the python logging module.

    The general idea is to have base configurations for the logging setup,
    which can be found in the :py:mod:`kaestchen.loggers` module.
    This class then takes these base configurations, and modifies them based
    on the application :py:mod:`kaestchen.conf` settings.

    The main entrypoint for using this class is the static
    :py:meth:`setup_logging` method.

    For more information on the implementation, see the
    :ref:`architecture reference <architecture_logging>`.

    Attributes:
        formatters (dict[str, Any]):
            See :py:data:`FORMATTERS_BASE`.
        handlers (dict[str, Any]): Dictionary for logging handlers.
            See :py:data:`HANDLERS_BASE`.
        loggers (dict[str, Any]): Dictionary for logging loggers.
            See :py:data:`LOGGERS_BASE`.
        logging_config (dict[str, Any]): Dictionary for the entire logging config.
            See :py:data:`LOGGING_CONFIG_BASE`.
        logdir (Path | None): Path to the directory where log files are stored.
            Is ``None`` if file logging is disabled.
    """

    #: Dictionary for logging formatters.
    #: See :py:data:`HANDLERS_BASE`.
    formatters: dict[str, Any]

    #: Dictionary for logging handlers.
    #: See :py:data:`HANDLERS_BASE`.
    handlers: dict[str, Any]

    #: Dictionary for logging loggers.
    #: See :py:data:`LOGGING_CONFIG_BASE`.
    loggers: dict[str, Any]

    #: Dictionary for the entire logging config.
    #: See :py:data:`LOGGING_CONFIG_BASE`.
    logging_config: dict[str, Any]

    #: Path to the directory where log files are stored.
    #: Is ``None`` if file logging is disabled.
    logdir: Path | None

    def is_filelogging_disabled(self) -> bool:
        """Checks if file logging is disabled.

        File logging is considered disabled if no ``logdir`` is specified in the
        settings.

        Returns:
            bool: ``True`` if file logging is disabled, ``False`` otherwise.
        """
        return self.logdir is None

    def __init__(self):
        """Initializes the LoggingManager with all its settings and data.

        Note that no modifications of the base logging configurations are made.
        The functions have to be explicitely called.

        For an entrypoint where all configurations are done, see the
        static method :py:meth:`LoggingManager.setup_logging`.
        """
        self.init_logdir()
        self.copy_default_logging_dicts()

    def copy_default_logging_dicts(self) -> None:
        """Copies the base logging configurations to the instance.

        The base configurations (:py:data:`FORMATTERS_BASE`,
        :py:data:`HANDLERS_BASE`, :py:data:`LOGGERS_BASE`,
        :py:data:`LOGGING_CONFIG_BASE`) are deep-copied to instance attributes
        to avoid modifying the original templates.
        """
        self.formatters = copy.deepcopy(FORMATTERS_BASE)
        self.handlers = copy.deepcopy(HANDLERS_BASE)
        self.loggers = copy.deepcopy(LOGGERS_BASE)
        self.logging_config = copy.deepcopy(LOGGING_CONFIG_BASE)

    def init_logdir(self) -> None:
        """Initializes the log directory.

        It retrieves the ``logdir`` from the application settings. If a ``logdir``
        is specified, it resolves the path and creates the directory if it
        doesn't exist.

        Raises:
            InvalidPath: If the ``logdir`` is specified but its parent directory
                does not exist, making it impossible to create the log directory.
        """

        self.logdir = settings.logdir
        if self.logdir is None:
            return

        self.logdir = self.logdir.resolve()

        try:
            self.logdir.mkdir(parents=False, exist_ok=True)
        except FileNotFoundError:
            # the following line should not generate an error even if the
            # logdir is the root dir '/'
            # Path('/').parent == Path('/')
            parent_dir: Path = self.logdir.parent.resolve()
            msg: Final[str] = (
                f"Could not create the logdir '{self.logdir}'.\n"
                f"The parent directory '{parent_dir}' needs to exist so "
                "the log directory can be created."
            )
            raise InvalidPath(msg)

    @staticmethod
    def replace_handler_with_nullhandler_inline(config: dict) -> None:
        """Replaces a handler configuration with a ``NullHandler`` inline.

        This is used to disable file logging for specific handlers when no
        ``logdir`` is provided. It modifies the passed dictionary in place.

        Args:
            config (dict): The handler configuration dictionary to modify.
        """

        keys_to_keep: set[str] = {"class", "formatter", "level"}
        config_keys: set[str] = set(config.keys())
        keys_to_remove: set[str] = config_keys.difference(keys_to_keep)
        for key in keys_to_remove:
            config.pop(key)
        config["class"] = "logging.NullHandler"

    def adjust_filename_on_filehandler_config(
        self, name: str, config: dict[str, Any]
    ) -> None:
        """Adjusts the filename for a file handler configuration.

        If a log directory is specified, it prepends the ``logdir`` path to the
        handler's filename. The filename is expected to be relative.

        If no log directory is specified (i.e., file logging is disabled),
        it replaces the file handler with a ``NullHandler`` using
        :py:meth:`replace_handler_with_nullhandler_inline`.

        This method only acts on handlers that are identified as file handlers
        (i.e., 'file' is in their class name).

        Args:
            name (str): The name of the handler.
            config (dict[str, Any]): The configuration dictionary for the handler.

        Raises:
            InvalidPath: If the handler is a file handler but has an empty
                ``filename``.
        """

        class_: str = config.get("class", "")
        is_filehandler: bool = "file" in class_.lower()
        if not is_filehandler:
            return

        filename: str = cast(str, config.get("filename", ""))
        filename = filename.strip()
        if filename == "":
            config_str: Final[str] = json.dumps(config, indent=4)
            msg: Final[str] = (
                f"Invalid filename in the '{name}' handler.\n"
                "It was identified as a file handler, but the filename is empty.\n"
                f"The Handler reads:\n{config_str}"
            )
            raise InvalidPath(msg)

        if self.is_filelogging_disabled() or self.logdir is None:
            LoggingManager.replace_handler_with_nullhandler_inline(config)
            return

        # The condition above should rule out None
        self.logdir = cast(Path, self.logdir)

        adjusted_filepath: Path = self.logdir / filename
        adjusted_filepath = adjusted_filepath.resolve()
        new_filename: str = str(adjusted_filepath)
        config["filename"] = new_filename

    def assemble_handlers(self) -> None:
        """Assembles the final handler configurations.

        Iterates through all handlers and adjusts their configurations,
        particularly for file handlers, using
        :py:meth:`adjust_filename_on_filehandler_config`.
        """

        name: str
        config: dict[str, Any]
        for name, config in self.handlers.items():
            self.adjust_filename_on_filehandler_config(name, config)

    def assemble_formatters(self) -> None:
        """Assembles the final formatter configurations.

        Currently, no modifications are made to the base formatters.
        """
        pass

    def assemble_loggers(self) -> None:
        """Assembles the final logger configurations.

        Currently, no modifications are made to the base loggers.
        """
        pass

    def assemble_config(self) -> None:
        """Assembles the complete logging configuration dictionary.

        This method calls the individual assembly methods for formatters,
        handlers, and loggers, and then populates the main ``logging_config``
        dictionary with the assembled parts.
        """
        self.assemble_formatters()
        self.assemble_handlers()
        self.assemble_loggers()
        self.logging_config["formatters"] = self.formatters
        self.logging_config["handlers"] = self.handlers
        self.logging_config["loggers"] = self.loggers

    def get_logging_config(self) -> dict[str, Any]:
        """Builds and returns the final logging configuration.

        Returns:
            dict[str, Any]: The complete logging configuration dictionary,
                ready to be used with ``logging.config.dictConfig``.
        """
        self.assemble_config()
        return self.logging_config

    @staticmethod
    def setup_logging() -> None:
        """Initializes and configures the application-wide logging.

        This static method is the main entry point for setting up logging.
        It creates a :py:class:`LoggingManager` instance, builds the
        configuration, and then applies it using Python's
        ``logging.config.dictConfig``.
        """
        logging_manager: LoggingManager = LoggingManager()
        config: dict[str, Any] = logging_manager.get_logging_config()
        logging.config.dictConfig(config)
