"""Test reading and writing Kaestchen XML files."""

import logging
from typing import cast
from pathlib import Path

import pytest
import xmltodict
from pydantic import ValidationError

from kaestchen.config_parser import io
from kaestchen.config_parser.model import XMLKaestchen


LOGGER: logging.Logger = logging.getLogger(__name__)


def test_read_write_invalid_xml_tag(tmp_path: Path):
    """Test if a kaestchen xml with additional elements can be parsed without issue

    Feature List:

    * :feature-test:`extensions.kaestchen.io.read.invalid_tag`
    * :feature-test:`extensions.kaestchen.io.write.invalid_tag`

    Args:
        tmp_path (Path): ``pytest`` fixture for a temporary directory
    """

    ###################################
    ### Prep temporary file content ###
    ###################################

    xml_path: Path = tmp_path / "read_encodings.xml"

    additional_xml: str = (
        '<tag1 attribute1="attr1value">'
        '   <tag2 attribute2="attr2value">tag2 content</tag2>'
        "   attr1 raw content"
        "</tag1>"
    )

    additional_xml_dict: dict = xmltodict.parse(additional_xml)

    xml_content: str = (
        f"<kaestchen><format_version>1.0</format_version>{additional_xml}</kaestchen>"
    )

    xml_path.write_text(xml_content)

    #####################
    ### Read the file ###
    #####################

    model: XMLKaestchen = io.read_kaestchen_file(xml_path)
    extra_fields: dict = cast(dict, model.kaestchen.model_extra)

    assert extra_fields == additional_xml_dict

    ######################
    ### Write the file ###
    ######################

    io.write_kaestchen_file(xml_path, model)

    # If the test above of reading the extra fields, worked, it should do so
    # now aswell.

    model = io.read_kaestchen_file(xml_path)
    extra_fields = cast(dict, model.kaestchen.model_extra)

    assert extra_fields == additional_xml_dict


def test_missing_mandatory_tag(tmp_path: Path):
    """Test if a kaestchen file can only be read with the few mandatory tags.

    Feature List:

    * :feature-test:`extensions.kaestchen.io.read.missing_tag`
    * :feature-test:`extensions.kaestchen.io.read.missing_tag.mandatory`

    Args:
        tmp_path (Path): ``pytest`` fixture for a temporary directory
    """

    xml_path: Path = tmp_path / "missing_tag.xml"

    #########################
    ### No format_version ###
    #########################

    xml_content: str = "<kaestchen></kaestchen>"
    xml_path.write_text(xml_content)

    with pytest.raises(ValidationError):
        _ = io.read_kaestchen_file(xml_path)

    ############################
    ### Empty format_version ###
    ############################

    xml_content_empty_version: str = (
        "<kaestchen><format_version></format_version></kaestchen>"
    )
    xml_path.write_text(xml_content_empty_version)

    with pytest.raises(ValidationError):
        _ = io.read_kaestchen_file(xml_path)

    ################################
    ### Non-Empty format_version ###
    ################################

    format_version: str = "1.0"
    xml_content_with_version: str = (
        f"<kaestchen><format_version>{format_version}</format_version></kaestchen>"
    )
    validated_model: XMLKaestchen = io.read_kaestchen_file(xml_content_with_version)
    assert validated_model.kaestchen.format_version == format_version


def test_read_write_encodings(tmp_path: Path):
    """Test if the file can be read with the specified encoding

    Feature List:

    * :feature-test:`extensions.kaestchen.io.read.encoding`
    * :feature-test:`extensions.kaestchen.io.write.encoding`

    This function relies on the correct implementation of
    :feature:`extensions.kaestchen.io.read.invalid_tag`.

    Args:
        tmp_path (Path): ``pytest`` fixture for a temporary directory
    """

    # The general idea is to write the minimal kaestchen-xml format
    # with an additional tag to the file.
    # Assuming extensions.kaestchen.io.read.invalid_tag still allows
    # unknown tags to be accessible through pydantic.BaseModel.model_extra,
    # the content is checked there.

    xml_path: Path = tmp_path / "read_encodings.xml"

    #################
    ### Read File ###
    #################

    special_chars_str: str = "Kästchen 😀"
    test_tag_name: str = "some_test_tag"
    xml_content_with_special: str = (
        "<kaestchen>"
        "<format_version>1.0</format_version>"
        f"<{test_tag_name}>{special_chars_str}</{test_tag_name}>"
        "</kaestchen>"
    )

    xml_path.write_text(xml_content_with_special, encoding="utf-8")
    validated_model: XMLKaestchen = io.read_kaestchen_file(xml_path, encoding="utf-8")

    # Casting the type here is necessary because as of pydantic version '2.11.7'
    # the return value of model_extra is 'TO DO|None'.
    # To avoid linting errors, the typing.cast method is used.
    extra_fields: dict = cast(dict, validated_model.kaestchen.model_extra)
    assert extra_fields.get(test_tag_name) == special_chars_str

    validated_model = io.read_kaestchen_file(xml_path, encoding="cp1252")
    extra_fields = cast(dict, validated_model.kaestchen.model_extra)
    assert extra_fields.get(test_tag_name) != special_chars_str

    ##################
    ### Write File ###
    ##################

    # The section only works if the tests above worked without issue.
    # The io.read_keastchen_file() needs to deal with encodings correctly.
    # Additionally, we also assume the `extensions.kaestchen.io.read.invalid_tag`
    # feature is implemented correctly.

    validated_model = io.read_kaestchen_file(xml_path, encoding="utf-8")

    # The emoji in the string to write is an issue, since it does not have a valid
    # cp1252 encoding. Python strings are always unicode, meaning that when we try to
    # write this character to a file, the conversion will ultimately fail, resulting
    # in an error. This is fine and accepted behaviour.

    with pytest.raises(UnicodeEncodeError):
        io.write_kaestchen_file(xml_path, validated_model, encoding="cp1252")

    io.write_kaestchen_file(xml_path, validated_model, encoding="utf-8")

    validated_model = io.read_kaestchen_file(xml_path, encoding="cp1252")
    extra_fields = cast(dict, validated_model.kaestchen.model_extra)
    assert extra_fields.get(test_tag_name) != special_chars_str

    validated_model = io.read_kaestchen_file(xml_path, encoding="utf-8")
    extra_fields = cast(dict, validated_model.kaestchen.model_extra)
    assert extra_fields.get(test_tag_name) == special_chars_str
