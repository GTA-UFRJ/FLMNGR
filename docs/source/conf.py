# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys 
import os

project = 'FLMNGR'
copyright = '2024, Guilherme Araujo, Lucas Airam, Fernando Dias'
author = 'Guilherme Araujo, Lucas Airam, Fernando Dias'
release = 'v0.1'

sys.path.insert(0,os.path.abspath('../..'))
print(sys.path)
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',             # Parse Markdown with extra features: https://myst-parser.readthedocs.io/en/latest/index.html
    'sphinx.ext.autodoc', 
    'sphinx-jsonschema',       # Auto import of JSON schemas: https://github.com/lnoor/sphinx-jsonschema
    'sphinxcontrib.httpdomain' # Writing HTTP API docs: https://sphinxcontrib-httpdomain.readthedocs.io/en/stable/
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
