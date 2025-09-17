# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add Python package path
conf_dir = os.path.dirname(__file__)
package_dir = os.path.abspath(os.path.join(conf_dir, '../bellhop'))

# -- Project information -----------------------------------------------------
project = 'BELLHOP Python API'
copyright = '2025, Will Robertson, Mandar Chitre'
author = 'Will Robertson, Mandar Chitre'
release = '0.1'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_mock_imports = ["matplotlib", "gcovr", "numpy", "scipy", "pandas", "bokeh"]

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
}
