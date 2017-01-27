# inspired from:

# https://python-packaging-user-guide.readthedocs.org/en/latest/single_source_version/
# https://github.com/pypa/warehouse/blob/master/warehouse/__about__.py

__title__ = 'spacy'
__version__ = '1.6.0'
__summary__ = 'Industrial-strength Natural Language Processing (NLP) with Python and Cython'
__uri__ = 'https://spacy.io'
__author__ = 'Matthew Honnibal'
__email__ = 'matt@explosion.ai'
__license__ = 'MIT'
__models__ = {
    'en': 'en>=1.1.0,<1.2.0',
    'de': 'de>=1.0.0,<1.1.0',
}
