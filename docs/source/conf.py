import os
import sys
sys.path.insert(0, os.path.abspath('./../..'))
sys.path.insert(0, os.path.abspath('./../../ptmd'))

project = 'Precision Toxixology Metadata Manager'
copyright = '2022, Dominique Batista'
author = 'Dominique Batista'
version = '0.0.1'
release = '0.0.1'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx_rtd_dark_mode'
]
templates_path = ['_templates']
exclude_patterns = []
source_suffix = '.rst'
master_doc = 'index'

pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
default_dark_mode = True
html_static_path = ['_static']
html_css_files = ['custom.css']
