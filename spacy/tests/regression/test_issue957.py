from __future__ import unicode_literals

import pytest
from ... import load as load_spacy


def test_issue957(en_tokenizer):
    '''Test that spaCy doesn't hang on many periods.'''
    string = '0'
    for i in range(1, 100):
        string += '.%d' % i
    doc = en_tokenizer(string)

# Don't want tests to fail if they haven't installed pytest-timeout plugin
try:
    test_issue913 = pytest.mark.timeout(5)(test_issue913)
except NameError:
    pass
