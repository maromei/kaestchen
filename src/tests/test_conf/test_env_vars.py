"""Test the basic functionality of adjusting settings via environment variables.

Specifically test the loading of environment variables via the
:py:class:`kaestchen.conf.EnvironmentSettings` class. With and without
``.env`` files.

For more information on the configuration settings see
the :ref:`architecture reference <architecture_configuration>`.
"""

import os
import logging
from typing import Final
from pathlib import Path

import pytest
from pytest import MonkeyPatch
from pydantic.dataclasses import FieldInfo

from kaestchen import conf
from kaestchen.exceptions import DotEnvFileDoesNotExist


LOGGER: logging.Logger = logging.getLogger(__name__)


def test_dotenv_default_nothing_to_load(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    """Test default case of no ``.env`` file being present to be loaded

    Test the most basic case of no ``.env`` file being present.
    Eventhough the default value is set to ``.env``, since no explicit
    ``KAESTCHEN_DOTENV_FILE`` environment variable is specified, no
    error should be generated eventhough the file does not exist.

    Feature List:

    * :feature-test:`kaestchen.conf.EnvironmentSettings.dotenv`

    Args:
        monkeypatch (MonkeyPatch): ``pytest`` fixture for setting environment variables
            and changing the working directory.
        tmp_path (Path): ``pytest`` fixture for a temporary directory
    """

    # Verify that we are in a directory where infact no ".env" file exists.
    # This should avoid potential ".env" files being present in the development
    # directory.
    monkeypatch.chdir(tmp_path)
    assert len(os.listdir(".")) == 0

    settings = conf.EnvironmentSettings()

    model_fields: dict[str, FieldInfo] = conf.EnvironmentSettings.model_fields
    default_logdir: str = model_fields["logdir"].default

    conf.EnvironmentSettings.model_fields

    assert settings.dotenv_file is None
    assert settings.logdir == default_logdir


def test_dotenv_custom_path(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test if a dotenv file can be loaded if a ``KAESTCHEN_DOTENV_FILE`` env-var is set

    Additionally, it tests whether an absolute path is transformed to a relative one
    on :py:class:`kaestchen.conf.EnvironmentSettings` instantiation.
    Otherwise, `pydantic-settings` cannot use the path specified.

    Additionally, it is also tested that the
    :py:attr:`kaestchen.conf.EnvironmentSettings.dotenv_file`` attribute
    always contains the absolute path.

    Feature List:

    * :feature-test:`kaestchen.conf.EnvironmentSettings.dotenv`

    Args:
        monkeypatch (MonkeyPatch): ``pytest`` fixture for setting environment variables
            and changing the working directory.
        tmp_path (Path): ``pytest`` fixture for a temporary directory
    """

    # Verify that we are in a directory where infact no ".env" file exists.
    # This should avoid potential ".env" files being present in the development
    # directory.
    monkeypatch.chdir(tmp_path)
    assert len(os.listdir(".")) == 0

    # Write a .env file with additional keys

    custom_logdir: str = "some_custom_logdir/"
    dotenv_string: str = f"{conf.EnvKeys.KAESTCHEN_LOGDIR}={custom_logdir}"

    subdir: Path = tmp_path / "subdir"
    subdir.mkdir()

    dotenv_path: Path = subdir / ".env"
    dotenv_path.write_text(dotenv_string)
    dotenv_path_str: str = str(dotenv_path.resolve())

    monkeypatch.setenv(conf.EnvKeys.KAESTCHEN_DOTENV_FILE.value, dotenv_path_str)

    settings = conf.EnvironmentSettings()
    assert settings.dotenv_file == dotenv_path_str
    assert settings.logdir == custom_logdir


def test_dotenv_invalid_path(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test if an error is raised if an invalid ``KAESTCHEN_DOTENV_FILE`` env-var is set

    Feature List:

    * :feature-test:`kaestchen.conf.EnvironmentSettings.dotenv`
    * :feature-test:`kaestchen.conf.EnvironmentSettings.dotenv.invalid_path`

    Args:
        monkeypatch (MonkeyPatch): ``pytest`` fixture for setting environment variables
        tmp_path (Path): ``pytest`` fixture for a temporary directory
    """

    # Verify that we are in a directory where infact no ".env" file exists.
    # This should avoid potential ".env" files being present in the development
    # directory.
    monkeypatch.chdir(tmp_path)
    assert len(os.listdir(".")) == 0

    # Test that the default values do not raise any errors if no explicit
    # .env filepath was set.
    conf.EnvironmentSettings()

    invalid_dotenv_path: Final[str] = "invalidpath/.env"
    monkeypatch.setenv(conf.EnvKeys.KAESTCHEN_DOTENV_FILE, invalid_dotenv_path)

    with pytest.raises(DotEnvFileDoesNotExist):
        conf.EnvironmentSettings()


def test_dotenv_default_workdir_load(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test if a ``.env`` file is loaded if it is placed in the working directory

    Feature List:

    * :feature-test:`kaestchen.conf.EnvironmentSettings.dotenv`
    * :feature-test:`kaestchen.conf.EnvironmentSettings.dotenv.default_path`

    Args:
        monkeypatch (MonkeyPatch): ``pytest`` fixture for setting the working directory
        tmp_path (Path): ``pytest`` fixture for a temporary directory
    """

    # Verify that we are in a directory where infact no ".env" file exists.
    # This should avoid potential ".env" files being present in the development
    # directory.
    monkeypatch.chdir(tmp_path)
    assert len(os.listdir(".")) == 0

    # Write a .env file with additional keys

    custom_logdir: str = "some_custom_logdir/"
    dotenv_string: str = f"{conf.EnvKeys.KAESTCHEN_LOGDIR}={custom_logdir}"

    dotenv_path: Path = tmp_path / ".env"
    dotenv_path.write_text(dotenv_string)

    settings = conf.EnvironmentSettings()
    assert settings.logdir == custom_logdir
    assert settings.dotenv_file is None


def test_dotenv_path_extra_variables(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test if a ``.env`` file is loaded without error if additional keys are defined

    Feature List:

    * :feature-test:`kaestchen.conf.EnvironmentSettings.dotenv`
    * :feature-test:`kaestchen.conf.EnvironmentSettings.dotenv.default_path`
    * :feature-test:`kaestchen.conf.EnvironmentSettings.dotenv.extra_keys`

    Args:
        monkeypatch (MonkeyPatch): ``pytest`` fixture for setting the working directory
        tmp_path (Path): ``pytest`` fixture for a temporary directory
    """

    # Verify that we are in a directory where infact no ".env" file exists.
    # This should avoid potential ".env" files being present in the development
    # directory.
    monkeypatch.chdir(tmp_path)
    assert len(os.listdir(".")) == 0

    # Write a .env file with additional keys

    custom_logdir: str = "some_custom_logdir/"
    dotenv_string: str = (
        f"{conf.EnvKeys.KAESTCHEN_LOGDIR}={custom_logdir}\n"
        "KAESTCHEN_ADDITIONAL_KEY=some_value1\n"
        "ADDITIONAL_KEY2=some_value2"
    )

    dotenv_path: Path = tmp_path / ".env"
    dotenv_path.write_text(dotenv_string)

    # The assumption is that no error is raised.
    settings = conf.EnvironmentSettings()
    assert settings.logdir == custom_logdir


def test_env_different_dotenv(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Test if environment variables are preferred over values in the ``.env`` file

    Feature List:

    * :feature-test:`kaestchen.conf.EnvironmentSettings.dotenv`
    * :feature-test:`kaestchen.conf.EnvironmentSettings.dotenv.priority`

    Args:
        monkeypatch (MonkeyPatch): ``pytest`` fixture for setting environment variables
            and changing the working directory.
        tmp_path (Path): ``pytest`` fixture for a temporary directory
    """

    # Verify that we are in a directory where infact no ".env" file exists.
    # This should avoid potential ".env" files being present in the development
    # directory.
    monkeypatch.chdir(tmp_path)
    assert len(os.listdir(".")) == 0

    dotenv_logdir: str = "logdir_dotenv_file/"
    dotenv_string: str = f"{conf.EnvKeys.KAESTCHEN_LOGDIR}={dotenv_logdir}"

    dotenv_path: Path = tmp_path / ".env"
    dotenv_path.write_text(dotenv_string)

    # First test that the value in the .env file can actually be loaded
    # and that there is no issue with the created file.
    env_settings = conf.EnvironmentSettings()
    assert env_settings.logdir == dotenv_logdir

    # Now we modify the env variable and reload the EnvironmentSettings
    env_logdir: str = "logdir_env_variable/"
    monkeypatch.setenv(conf.EnvKeys.KAESTCHEN_LOGDIR, env_logdir)

    env_settings = conf.EnvironmentSettings()
    assert env_settings.logdir == env_logdir
