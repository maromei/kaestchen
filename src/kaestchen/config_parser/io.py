"""Simple read and write functions for the Kaestchen XML format.

Most fundamental functions are:

* :py:func:`read_kaestchen_file`
* :py:func:`write_kaestchen_file`

"""

import logging
from pathlib import Path

from kaestchen.config_parser.model import XMLKaestchen


LOGGER: logging.Logger = logging.getLogger(__name__)


def read_kaestchen_file(
    file_path_or_content: Path | str, encoding: str = "utf-8"
) -> XMLKaestchen:
    """Reads a Kaestchen XML file and returns the parsed model.

    Args:
        file_path_or_content (Path|str): Either a path to a ``*.kaestchen`` file,
            or the content of the file as a string.
        encoding (str): Encoding of the file. Defaults to ``utf-8``.

    Returns:
        XMLKaestchen: The parsed XML model.
    """

    file_content: str
    if isinstance(file_path_or_content, Path):
        file_path: Path = file_path_or_content
        file_content = file_path.read_text(encoding=encoding)
    elif isinstance(file_path_or_content, str):
        file_content = str(file_path_or_content)
    else:
        msg: str = (
            f"Invalid type '{str(type(file_path_or_content))}' passed to "
            "'file_path_or_content' in read_kaestchen_file(). "
            "Only Path or str are allowed."
        )
        LOGGER.error(msg)
        raise TypeError(msg)

    model: XMLKaestchen = XMLKaestchen.model_validate_xml(file_content)
    return model


def write_kaestchen_file(
    file_path: Path, model: XMLKaestchen, encoding: str = "utf-8"
) -> None:
    """Writes the Kaestchen XML model to a file.

    Args:
        file_path (Path): The path where the XML file will be written.
        model (XMLKaestchen): The XML model to write.
        encoding (str): Encoding of the file. Defaults to ``utf-8``.
    """

    xml_content: str = model.model_dump_xml()
    with file_path.open("w", encoding=encoding) as file:
        file.write(xml_content)
    LOGGER.info(f"Kaestchen XML file written to {file_path}")
