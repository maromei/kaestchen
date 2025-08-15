# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
from typing import Final
from pathlib import Path

project_root: Path = Path(__file__).parent.parent.parent


project: str = "kaestchen"
copyright: str = "2025, maromei"
author: str = "maromei"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list[str] = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "myst_parser",
    "sphinx_rtd_theme",
    "sphinxcontrib.plantuml",
    "sphinx_feature_reference",
]

templates_path: list[str] = ["_templates"]
exclude_patterns: list[str] = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme: str = "sphinx_rtd_theme"
html_static_path: list[str] = ["_static"]

# -- Plantuml Settings -------------------------------------------------------

plantuml_dir: str | None = os.getenv("PLANTUML_OUTPUT_PATH")
if plantuml_dir is None:
    raise ValueError("PLANTUML_OUTPUT_PATH not set in environment.")

plantuml_jar_path: Path = project_root / plantuml_dir / "plantuml.jar"
if not plantuml_jar_path.exists():
    raise FileNotFoundError(
        f"plantuml.jar not found at '{plantuml_jar_path}'. "
        "Try running 'hatch run docs:install-plantuml'."
    )
plantuml: Final[str] = f"java -jar {plantuml_jar_path}"
