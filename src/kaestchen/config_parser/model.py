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
    type: XMLCSVType = xml_attr(name="type", default=XMLCSVType.inline)
    content: str = ""


class XMLRendererType(Enum):
    """Enum for renderer types."""

    default = "default"
    markdown = "markdown"


class XMLColumnRenderer(BaseXmlModel, tag="renderer"):
    type: XMLRendererType = xml_attr(name="type", default=XMLRendererType.default)


class XMLColumnExpandCell(BaseXmlModel, tag="expand_cell"):
    enabled: bool = xml_attr(name="enabled", default=False)


class XMLColumn(BaseXmlModel, tag="column"):
    name: str = xml_attr(name="name")
    renderer: XMLColumnRenderer = xml_element(tag="renderer", default=None)
    expand_cell: XMLColumnExpandCell = xml_element(tag="expand_cell", default=None)


class XMLSheet(BaseXmlModel, tag="sheet"):
    name: str = xml_attr(name="name")
    order: int = xml_attr(name="order")

    column_config: list[XMLColumn] = xml_element(
        tag="column_config", default_factory=list
    )
    csv: XMLCSV = xml_element(tag="csv", default_factory=XMLCSV)


def generate_default_xml_sheets() -> list[XMLSheet]:
    default_sheet: XMLSheet = XMLSheet(name="sheet1", order=1)
    return [default_sheet]


class XMLKaestchen(BaseXmlModel, tag="kaestchen"):
    format_version: str = xml_element(
        tag="format_version", default=__xml_format_version__, regex=r"^\d+\.\d+$"
    )

    sheets: list[XMLSheet] = xml_element(
        tag="sheet", default_factory=generate_default_xml_sheets
    )
