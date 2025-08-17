"""Validates a *.kaestchen XML file.

While the content and structure of the XML file is validated by the
pydantic models, this module ensures consistency with the actual data.
F.e. the XML format can contain a ``<column_config>`` element, which
contains setting for a specific column. The mapping to the actual data
is done via the column's name. Since the data might be changed externally,
this module checks if the settings are still valid.

Note that the idea is to have the methods defined in this module called in the
``pydantic`` model validations, so no additional function calls are needed.
"""
