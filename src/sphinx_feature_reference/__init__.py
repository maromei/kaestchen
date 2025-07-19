"""Custom Sphinx Extension for referencing specific features in the documentation.

This extension introduces the `feature` role and directive.
Currently it only displays the feature name in blue text.
In the future it can be extended to do more complex tasks.

Other possible tags should be:

* ``feature-test``

    * Can be used inline with the ID of a feature
      in a docstring for a test function.
"""

from sphinx.application import Sphinx
from sphinx.roles import SphinxRole
from docutils import nodes


def setup(app: Sphinx) -> dict:
    """
    Setup function for the Sphinx extension.

    Args:
        app (Sphinx): The Sphinx application object.
    """

    app.add_role("feature", FeatureReferenceRole())
    app.add_role("feature-test", FeatureTestRole())

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


class FeatureReferenceRole(SphinxRole):
    """
    Custom Sphinx role for referencing features in the documentation.
    """

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """
        Formats the diven text of the directive as a feature reference.
        Currently, it only wraps the text in a span with blue color.
        Should be expanded in the future.

        Returns:
            tuple: A tuple containing the resulting nodes.
        """
        new_text: str = (
            f"Feature Reference: <span style='color: blue;'>{self.text}</span>"
        )
        inline_node: nodes.raw = nodes.raw("", new_text, format="html")
        return [inline_node], []


class FeatureTestRole(SphinxRole):
    """Custom Sphinx role for marking a test function to be testing a feature."""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Mark a test function to be testing a feature.

        Currently, it only wraps the text in a span with blue color.
        Should be expanded in the future.

        Returns:
            tuple: A tuple containing the resulting nodes.
        """
        new_text: str = (
            f"Test for Feature: <span style='color: blue;'>{self.text}</span>"
        )
        inline_node: nodes.raw = nodes.raw("", new_text, format="html")
        return [inline_node], []
