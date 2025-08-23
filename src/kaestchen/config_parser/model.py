"""Defines the Kaestchen XML configuration model.

This file describes the pydantic structure of the Kaestchen XML configuration.
The main object is :py:class:`XMLKaestchen`, which inherits from
:py:class:`BaseXmlModel` with all its functionality.
"""

import logging
from enum import Enum
from typing import Union, Type, Optional

from pydantic import BaseModel, Field

from kaestchen.__about__ import __xml_format_version__
from kaestchen.config_parser.pydantic_xml import BaseXmlModel, xml_attr, xml_text


LOGGER: logging.Logger = logging.getLogger(__name__)


def default_model(model_class: Type, *args, **kwargs):
    """A shorthand function for assigning an empty class initializer as a pydantic field default value

    Effectively a shorthand for ``Field(default_factory=lambda: model_class())``.
    It is supposed to be a simple way of assigning a default value as a field.

    Args:
        model_class (Type): The type of the model to initalize. The class
            needs to have no mandatory arguments in its constructor.
        *args: Passed to ``pydantic.Field``
        **kwargs: Passed to ``pydantic.Field``

    Returns:
        pydantic.Field: With ``default_factor=lambda: model_class()``
    """

    def default_factory():
        return model_class()

    return Field(default_factory=default_factory, *args, **kwargs)


class XMLCSVType(Enum):
    """Enum for CSV types."""

    inline = "inline"  #:
    external = "external"  #:


class XMLCSV(BaseModel, use_enum_values=True, validate_default=True):
    """Model for CSV configuration in XML."""

    #: The type of CSV, either ``inline`` or ``external``.
    type: XMLCSVType = xml_attr(name="type", default=XMLCSVType.inline)

    #: The content of the CSV, either inline data or a file path.
    #: How the content is interpreted depends on the ``type``.
    content: str = xml_text(default="")


class XMLRendererType(Enum):
    """Enum for renderer types."""

    default = "default"  #:
    markdown = "markdown"  #:


class XMLColumnRenderer(BaseXmlModel, use_enum_values=True, validate_default=True):
    """Defines how cells in a column should be rendered."""

    #: The type of renderer to use. Defaults to :py:attr:`XMLRendererType.default`,
    #: meaning no special rendering.
    type: XMLRendererType = xml_attr(name="type", default=XMLRendererType.default)


class XMLColumnExpandCell(BaseXmlModel):
    """Defines whether a cell in a column can be expanded."""

    #: Whether the expand cell feature is enabled.
    enabled: bool = xml_attr(name="enabled", default=False)


class XMLColumn(BaseXmlModel):
    """Defines a column in the XML configuration."""

    #: The name of the column. It needs to match a column name
    #: in the csv data (see :py:class:`XMLCSV`).
    name: str = xml_attr(name="name")

    #: The renderer configuration for the column.
    renderer: Optional[XMLColumnRenderer] = None

    #: Configuration for expanding cells in the column.
    expand_cell: Optional[XMLColumnExpandCell] = None


class XMLColumnConfigList(BaseXmlModel):
    """Contains the List of column configs"""

    #: A list of column configs. Can be empty.
    column: Union[XMLColumn, list[XMLColumn]]


class XMLSheet(BaseXmlModel):
    """Defines a sheet in the XML configuration."""

    #: The name of the sheet.
    name: str = xml_attr(name="name")

    #: The order of the sheet in the configuration. Lower numbers appear first.
    order: int = xml_attr(name="order")

    #: Specific configs for the given columns. Can be empty or missing.
    #: Only if configs need to be applied can they appear here.
    column_config: Optional[XMLColumnConfigList] = None

    #: The actual CSV data to be displayed.
    csv: XMLCSV = default_model(XMLCSV)


def generate_default_xml_sheets() -> list[XMLSheet]:
    """Default factory generator for XMLSheet

    Returns:
        list[XMLSheet]: A list containing a single default XMLSheet instance.
    """

    default_sheet: XMLSheet = XMLSheet(name="sheet1", order=1)
    return [default_sheet]


class XMLSheetContainer(BaseXmlModel):
    """Container for XMLSheets."""

    #: A list of sheets defined in the configuration. Each on representing one csv.
    sheet: Union[XMLSheet, list[XMLSheet]] = Field(
        default_factory=generate_default_xml_sheets
    )


class XMLKaestchenContent(BaseXmlModel):
    """Model for the Kaestchen XML configuration.

    Initializing this class without any arguments will result
    in the most minimal valid XML structure.
    (:feature:`extensions.kaestchen.default`)
    """

    #: The version of the XML format, defaults to the value of
    #: :py:attr:`kaestchen.__about__.__xml_format_version__`.
    format_version: str = Field(default=__xml_format_version__, pattern=r"^\d+\.\d+$")

    #: A list of sheets defined in the configuration. Each sheet contains
    #: its own CSV data and column configurations.
    sheets: XMLSheetContainer = default_model(XMLSheetContainer)


class XMLKaestchen(BaseXmlModel):
    """RootModel for the Kaestchen XML configuration."""

    #: The actual content of the Kaestchen XML configuration.
    #: This class merely serves as the root tag in the xml config.
    kaestchen: XMLKaestchenContent = default_model(XMLKaestchenContent)
