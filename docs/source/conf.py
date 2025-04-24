# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations

from sphinx_gallery.sorting import FileNameSortKey


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "OptunaHub"
copyright = "2024, Optuna team"
author = "Optuna team"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_gallery.gen_gallery",
]

templates_path = ["_templates"]
exclude_patterns = ["build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_options = {"logo_only": True, "navigation_with_keys": True, "navigation_depth": 2}
html_static_path = ["_static"]
html_favicon = "_static/favicon.ico"
html_logo = "_static/optuna-logo.png"
html_css_files = ["css/custom.css"]

sphinx_gallery_conf = {
    "examples_dirs": [
        "../../recipes",
    ],
    "gallery_dirs": [
        "generated/recipes",
    ],
    "within_subsection_order": FileNameSortKey,
    "filename_pattern": r"/*\.py",
    "first_notebook_cell": None,
}
