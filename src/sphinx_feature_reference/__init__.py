"""Custom Sphinx Extension for referencing specific features in the documentation.

This extension introduces the `feature` role and directive.
Currently it only displays the feature name in blue text.
In the future it can be extended to do more complex tasks.
"""

from sphinx.application import Sphinx
from sphinx.roles import SphinxRole
from docutils import nodes


def setup(app: Sphinx) -> None:
    """
    Setup function for the Sphinx extension.

    Args:
        app (Sphinx): The Sphinx application object.
    """

    app.add_role("feature", FeatureReferenceRole())
    app.add_directive("feature", FeatureReferenceRole)
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
