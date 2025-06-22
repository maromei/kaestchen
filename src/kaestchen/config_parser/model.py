"""Pydantic XML models for Kaestchen file configuration.

This module defines the XML structure for Kaestchen's configuration files,
including CSV data, sheets, columns, and their rendering options.
"""

from enum import Enum

from pydantic_xml import BaseXmlModel
from pydantic_xml import attr as xml_attr
from pydantic_xml import element as xml_element

from kaestchen.__about__ import __xml_format_version__


class XMLCSVType(Enum):
    """Enum for CSV types."""

    inline = "inline"
    external = "external"


class XMLCSV(BaseXmlModel, tag="csv"):
    """Model for CSV configuration in XML.

    Attributes:
        type (XMLCSVType): The type of CSV, either
            ``inline`` or ``external``.
        content (str): The content of the CSV, either inline data or a file path.
            How the content is interpreted depends on the ``type``.
    """

    type: XMLCSVType = xml_attr(name="type", default=XMLCSVType.inline)
    content: str = ""


class XMLRendererType(Enum):
    """Enum for renderer types."""

    default = "default"
    markdown = "markdown"


class XMLColumnRenderer(BaseXmlModel, tag="renderer"):
    """Defines how cells in a column should be rendered.

    Attributes:
        type (XMLRendererType): The type of renderer to use. Defaults to
            :py:attr:`XMLRendererType.default`, meaning no special rendering.
    """

    type: XMLRendererType = xml_attr(name="type", default=XMLRendererType.default)


class XMLColumnExpandCell(BaseXmlModel, tag="expand_cell"):
    """Defines whether a cell in a column can be expanded.

    Attributes:
        enabled (bool): Whether the expand cell feature is enabled.
    """

    enabled: bool = xml_attr(name="enabled", default=False)


class XMLColumn(BaseXmlModel, tag="column"):
    """Defines a column in the XML configuration.

    Attributes:
        name (str): The name of the column. It needs to match a column name
            in the csv data (see :py:class:`XMLCSV`).
        renderer (XMLColumnRenderer): The renderer configuration for the column.
        expand_cell (XMLColumnExpandCell): Configuration for expanding
            cells in the column.
    """

    name: str = xml_attr(name="name")
    renderer: XMLColumnRenderer = xml_element(tag="renderer", default=None)
    expand_cell: XMLColumnExpandCell = xml_element(tag="expand_cell", default=None)


class XMLSheet(BaseXmlModel, tag="sheet"):
    """Defines a sheet in the XML configuration.

    Attributes:
        name (str): The name of the sheet.
        order (int): The order of the sheet in the configuration. Lower numbers
            appear first.
        column_config (list[XMLColumn]): Specific configs for the given columns.
        csv (XMLCSV): The actual CSV data to be displayed.
    """

    name: str = xml_attr(name="name")
    order: int = xml_attr(name="order")

    column_config: list[XMLColumn] = xml_element(
        tag="column_config", default_factory=list
    )
    csv: XMLCSV = xml_element(tag="csv", default_factory=XMLCSV)


def generate_default_xml_sheets() -> list[XMLSheet]:
    """Default factory generator for XMLSheet

    Returns:
        list[XMLSheet]: A list containing a single default XMLSheet instance.
    """

    default_sheet: XMLSheet = XMLSheet(name="sheet1", order=1)
    return [default_sheet]


class XMLKaestchen(BaseXmlModel, tag="kaestchen"):
    """Model for the Kaestchen XML configuration.

    Attributes:
        format_version (str): The version of the XML format, defaults to
            the value of :py:attr:`kaestchen.__about__.__xml_format_version__`.
        sheets (list[XMLSheet]): A list of sheets defined in the configuration.
            Each sheet contains its own CSV data and column configurations.
    """

    format_version: str = xml_element(
        tag="format_version", default=__xml_format_version__, regex=r"^\d+\.\d+$"
    )

    sheets: list[XMLSheet] = xml_element(
        tag="sheet", default_factory=generate_default_xml_sheets
    )
