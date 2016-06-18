import sys
import os

sys.path.insert(0, os.path.abspath('..'))
from fysql import __version__


extensions = [
    'sphinx.ext.viewcode'
]

templates_path      = ['_templates']
source_suffix       = '.rst'
master_doc          = 'index'
project             = u'fysql'
copyright           = u'2016, Florian Gasquez'
author              = u'Florian Gasquez'
version             = __version__
release             = __version__
language            = None
exclude_patterns    = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style      = 'alabaster.support.Alabaster'
todo_include_todos  = False
html_theme          = 'alabaster'
html_theme_options  = {
    'show_powered_by': False,
    'github_user': 'Fy-Network',
    'github_repo': 'fysql',
    'github_banner': True,
    'show_related': False
}
html_sidebars = {
    'index':    ['about.html', 'navigation.html', 'sourcelink.html', 'searchbox.html'],
    '**':       ['about.html', 'navigation.html', 'localtoc.html', 'relations.html','sourcelink.html', 'searchbox.html']
}
html_show_sourcelink = False
html_show_sphinx     = False
html_show_copyright  = True


html_static_path    = ['_static']
htmlhelp_basename   = 'fysqldoc'
latex_elements      = {}
latex_documents     = [
    (master_doc, 'fysql.tex', u'fysql Documentation',
     u'Florian Gasquez', 'manual'),
]
man_pages           = [
    (master_doc, 'fysql', u'fysql Documentation',
     [author], 1)
]

texinfo_documents   = [
    (master_doc, 'fysql', u'fysql Documentation',
     author, 'fysql', 'fysql is a small ORM inpired by peewee.',
     'Miscellaneous'),
]
