"""Implements an Extension to ``pydantic`` for interaction with XML documents.

The :py:class:`BaseXmlModel` adds an addition function
:py:meth:`BaseXmlModel.model_dump_xml` to
dump its content to an ``.xml`` file. How the json and xml conversion work
is detailed in the class' docstring.

To more easily implement Models with the correct json formatting,
the :py:func:`xml_attr` and :py:func:`xml_text` fuctions can be used.
F.e. an xml-attribute is defined by a key in the form of ``@ATTRIBUTE_NAME``.
:py:func:`xml_attr` generates a ``pydantic.Field`` which can be read and saved
with the ``@`` modifier.

The following class setup

.. code-block:: python

    from pydantic import Field
    from kaestchen.config_parser.pydantic_xml import BaseXmlModel, xml_attr, xml_text
    from kaestchen.config_parser.model import default_model

    class SubTag(BaseXmlModel):
        another_attribute: str = xml_attr(name="another_attribute", default="0")
        text_content: str = xml_text(default="Some default Text")

    class BaseTag(BaseXmlModel):

        some_attribute_name: str = xml_attr(name="attribute_name", default="value")
        sub_tag: SubTag = default_model(SubTag)

    class RootObj(BaseXmlModel):

        base_tag: BaseTag = default_model(BaseTag)

    model: RootObj = RootObj()

    xml_text = model.model_dump_xml()
    json_text = model.model_dump_json(indent=4)

defines the xml

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <base_tag attribute_name="value">
            <sub_tag another_attribute="0">Some default Text</sub_tag>
    </base_tag>

and the json

.. code-block:: json

    {
    "base_tag": {
        "@attribute_name": "value",
        "sub_tag": {
            "@another_attribute": "0",
            "#text": "Some default Text"
        }
    }

"""

import logging
from typing import override, TypeVar, Type, Any

import xmltodict
from pydantic import BaseModel, Field, AliasChoices


LOGGER: logging.Logger = logging.getLogger(__name__)  #:


#: Type for any variable bound to BoundBaseXmlModel
#:
#: Is used vor typehinting child classes being returned in inherited functions.
#: An example of this is currently used in
#: :py:meth:`BaseXmlModel.model_validate_xml`.
BoundBaseXmlModel = TypeVar("BoundBaseXmlModel", bound="BaseXmlModel", covariant=True)


class BaseXmlModel(BaseModel, extra="allow"):
    """Extend ``pydantic.BaseModel`` to interact with XML.

    The general format for handling XML is defined by the ``xmltodict`` library.
    Main idea for the format:

    * Every key, having a dictionary as value, represents a tag. ``"key": {...}``
    * Keys starting with ``@`` are interpreted as attributes.
    * A ``"#text": "..."`` defines Text content of the tag.
    * ``null`` values define an empty tag (``"empty_tag": null`` :math:`\\rightarrow` ``<empty_tag />``)

    .. code-block:: xml

        {
            "some_tag": {
                "@some_attribute": "some_value",
                "#text": "some_text",
                "empty_tag": null
            }
        }
    """

    def __set_model_dump_defaults(self, **kwargs) -> dict:
        """Extend and modify ``kwargs`` with default values needed for XML parsing.

        Returns:
            dict: ``kwargs`` which can be passed a
                ``pydantic.BaseModel.model_dump*()`` function
        """
        kwargs["by_alias"] = kwargs.get("by_alias", True)
        kwargs["exclude_none"] = kwargs.get("exclude_none", True)
        return kwargs

    @override
    def model_dump_json(self, **kwargs) -> str:
        """Dump the model context to a json string

        Returns:
            str:
        """
        kwargs = self.__set_model_dump_defaults(**kwargs)
        model_json: str = super(BaseXmlModel, self).model_dump_json(**kwargs)
        return model_json

    @override
    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Dump the model context to a dictionary

        Returns:
            dict: Content of the model as a dictionary, can be dumped to
                a valid json file.
        """
        kwargs = self.__set_model_dump_defaults(**kwargs)
        model_dict: dict[str, Any] = super(BaseXmlModel, self).model_dump(**kwargs)
        return model_dict

    def model_dump_xml(self, **kwargs) -> str:
        """Dump the model context to a xml string

        Returns:
            str:
        """
        model_dict: dict = self.model_dump(**kwargs)
        model_xml_str: str = xmltodict.unparse(model_dict, pretty=True)
        return model_xml_str

    @classmethod
    def model_validate_xml(
        cls: Type[BoundBaseXmlModel], xml_str: str, *args, **kwargs
    ) -> "BoundBaseXmlModel":
        """Validate the model based on an xml formatted string

        Args:
            cls (Type[BoundBaseXmlModel]):
            xml_str (str): xml formatted string

        Returns:
            BoundBaseXmlModel: validated model
        """
        model_dict: dict = xmltodict.parse(xml_str)
        new_model: "BoundBaseXmlModel" = cls.model_validate(model_dict, *args, **kwargs)
        return new_model


def xml_attr(name: str, *args, **kwargs):
    """Generate a ``pydantic.Field`` describing an xml attribute

    See :py:mod:`kaestchen.config_parser.pydantic_xml` for examples.
    See :py:class:`BaseXmlModel` for details on the format.

    Args:
        name (str): Name of the xml-attribute
        *args: Passed to ``pydantic.Field``
        **kwargs: Passed to ``pydantic.Field``

    Returns:
        pydnatic.Field:
    """

    alias: str = f"@{name}"
    alias_choice: AliasChoices = AliasChoices(name, alias)
    return Field(
        validation_alias=alias_choice, serialization_alias=alias, *args, **kwargs
    )


def xml_text(*args, **kwargs):
    """Generate a ``pydantic.Field`` describing the text content of an xml tag

    See :py:mod:`kaestchen.config_parser.pydantic_xml` for examples.
    See :py:class:`BaseXmlModel` for details on the format.

    Args:
        *args: Passed to ``pydantic.Field``
        **kwargs: Passed to ``pydantic.Field``

    Returns:
        pydnatic.Field:
    """

    name: str = "text"
    alias: str = "#text"
    alias_choice: AliasChoices = AliasChoices(name, alias)
    return Field(
        validation_alias=alias_choice, serialization_alias=alias, *args, **kwargs
    )
