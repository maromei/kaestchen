"""Kaestchen Settings

Implements settings for developing and using Kaestchen.
The core of the functionality is `pydantic-settings`.

For more information about the idea behind the configuration setup, see the
:ref:`architecture reference <architecture_configuration>`.
"""

import os
import logging
from typing import Final, ClassVar
from enum import StrEnum
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from kaestchen.exceptions import DotEnvFileDoesNotExist


LOGGER: logging.Logger = logging.getLogger(__name__)


class EnvKeys(StrEnum):
    """String enum for environment variable names

    This enum is supposed to have an explicit typing for potentiel environment
    variable names. The ``pydantic-settings`` model
    (:py:class:`kaestchen.conf.EnvironmentSettings`) splits the requirement for
    the prefix ``KAESTCHEN_`` and the actual environment variable names. In addition,
    the names are not case sensitive. This enum tries to give an explicit list
    of environment variable names.
    """

    #: Path to a ``.env`` file.
    KAESTCHEN_DOTENV_FILE = "KAESTCHEN_DOTENV_FILE"

    #: Directory for logging files.
    KAESTCHEN_LOGDIR = "KAESTCHEN_LOGDIR"


class EnvironmentSettings(BaseSettings):
    """Defines a pydantic model for options specified through environment variables.

    This class is immutable. Environment variables have to be prefixed with
    ``KAESTCHEN_`` to be mapped to the class attributes. While the mapping is
    technically not case-sensitiv, it is recommended to specify them in ALL CAPS.

    By default a `.env` file is searched for in the current working directory.
    If :py:attr:`EnvKeys.KAESTCHEN_DOTENV_FILE` is specified in the environment,
    it will be used instead. Should the given filepath be invalid,
    :py:class:`kaestchen.exceptions.DotEnvFileDoesNotExist` will be raised.
    """

    #: ``pydantic-settings`` configuration.
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="kaestchen_",
        env_file="DUMMY: value set in __init__ via __update_model_config_env_path()",
        frozen=True,
        case_sensitive=False,
        extra="ignore",
    )

    def __update_model_config_env_path(self) -> None:
        """Set the ``env_file`` path for the ``model_config``

        Since the ``env_file`` path can be set / overridden via an environment variable,
        it cannot be set as a default value in the inline ``model_config`` definition.
        The definition will be evaluated once on first import of the class.

        Since we want the current value on instantiation, we need to update that
        variable via the ``__init__()`` function. This is inline with the
        ``pydantic-settings`` documentation, which advises to reload the values
        by simply calling the ``__init__()`` method.

        Additionally, we need to make sure that the path passed is always relative
        to the current working directory. If an absolute path is passed via the
        environment variable, it needs to be transformed.
        """

        env_path_str: str = os.environ.get(
            EnvKeys.KAESTCHEN_DOTENV_FILE.value, default=".env"
        )
        env_path: Path = Path(env_path_str)
        env_path = env_path.resolve()
        env_path = env_path.relative_to(Path.cwd())
        self.model_config.update(SettingsConfigDict(env_file=env_path))

    def __init__(self, *args, **kwargs):
        self.__update_model_config_env_path()
        super().__init__(*args, **kwargs)

    @field_validator("dotenv_file", mode="after")
    @classmethod
    def check_dotenvpath(cls, dotenv_file: str | None) -> str | None:
        """Raises an error if an explicit ``.env`` filepath is invalid.

        The function utilizes :py:attr:`dotenv_file` to check if it was explicitely
        defined on class initialization, as the actual environment value might
        have changed between initilization and now.

        If the given path is valid, the absolute path will be returned.

        Features:

        * :feature:`kaestchen.conf.EnvironmentSettings.dotenv.invalid_path`

        Raises:
            DotEnvFileDoesNotExist: If the explicitely defined ``.env`` filepath
                is invalid.

        Returns:
            str | None: The validated, absolute path, or ``None`` if no
                custom ``.env`` file was specified.
        """

        if dotenv_file is None:
            return None

        env_path: Path = Path(dotenv_file).resolve()
        if env_path.is_file():
            LOGGER.info(f"Loading .env file from environment variable '{env_path}'")
            return str(env_path)

        msg: Final[str] = (
            "Tried to initialized class 'EnvironmentSettings'.\n"
            "An environment variable was found defining the path to an .env file:\n"
            f"{EnvKeys.KAESTCHEN_DOTENV_FILE}={dotenv_file}\n"
            f"which was resolved to '{env_path}'\n"
            "The file does not seem to exist.\n"
            "Removing the explicit path declaration via the environment variable will "
            "get rid of this error."
        )

        LOGGER.error(msg)
        raise DotEnvFileDoesNotExist(msg)

    #: Absolute path to a ``.env`` file.
    #:
    #: If specified in the environment, but the file it points to is invalid,
    #: an error will be raised.
    #: See :py:meth:`EnvironmentSettings.check_dotenvpath` for the
    #: validator function and feature
    #: :feature:`kaestchen.conf.EnvironmentSettings.dotenv.invalid_path`.
    #: Note that the specified path will always be absolute, regardless of
    #: how it was specified in the environment to make it explicit which
    #: `.env` file was used on instantiation.
    dotenv_file: str | None = None

    #: Directory for logging files.
    logdir: str = "logs"


class Settings:
    pass
