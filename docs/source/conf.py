# Configuration file for the Sphinx documentation builder.

import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------

project = 'GEEpy'
author = 'Zhang Lei'

version_path = Path(__file__).parents[2] / 'geepy' / '__version__.py'
exec(version_path.read_text(), version_dict := {})
version = release = version_dict['__version__']

copyright = '2025, Zhang Lei'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
]

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': True,
    'special-members': '__init__',
    'inherited-members': True,
    'show-inheritance': True,
}
autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = []

language = 'zh_CN'

# -- HTML output -------------------------------------------------------------

html_theme = 'furo'

html_theme_options = {
    # 🌞 亮色主题下的配色
    "light_css_variables": {
        "color-brand-primary": "#2a6ee8",
        "color-brand-content": "#2a6ee8",
        "color-background-primary": "#ffffff",
        "color-background-secondary": "#f6f8fa",
        "color-foreground-primary": "#0a2540",
    },
    # 🌚 暗色主题下的配色
    "dark_css_variables": {
        "color-brand-primary": "#4ea1ff",
        "color-brand-content": "#4ea1ff",
        "color-background-primary": "#0f172a",
        "color-background-secondary": "#1e293b",
        "color-foreground-primary": "#cbd5e1",
    },
    # 🔗 GitHub 链接信息（可选）
    "navigation_with_keys": True,
    "sidebar_hide_name": False,
    "source_repository": "https://github.com/gg-zl/GEE_py/",
    "source_branch": "main",
    "source_directory": "docs/source/",
}

html_logo = "_static/logo.png"
html_static_path = ['_static']
html_css_files = ['custom.css']  # 如果你有自定义 CSS，可启用

# -- Copy button configuration -----------------------------------------------

copybutton_prompt_text = r">>> |\.\.\. "
copybutton_prompt_is_regexp = True
