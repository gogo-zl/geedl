# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../../'))  # 项目根目录
print(f"Current sys.path: {sys.path}")

project = 'geepy'
copyright = '2025, Zhang Lei'
author = 'Zhang Lei'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',      # 自动生成 API 文档
    'sphinx.ext.napoleon',     # 支持 Google 和 NumPy 风格的 docstring
    'sphinx.ext.viewcode',     # 提供源码链接
]

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'private-members': True,
    'special-members': '__init__',
    'inherited-members': True,
}

html_theme_options = {
    'collapse_navigation': False,  # 禁止菜单折叠，默认展开
    'navigation_depth': 4,         # 设置导航的深度，4 表示最多显示 4 层
}

html_context = {
    'current_version': release,
}

autodoc_mock_imports = ['geemap', 'earthengine-api', 'numpy', 'pandas']

templates_path = ['_templates']
exclude_patterns = []

language = 'zh_CN'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
