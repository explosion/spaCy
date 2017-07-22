from __future__ import unicode_literals

from ...symbols import ORTH

from ...vocab import Vocab
from ...en import English


def test_issue1061():
    '''Test special-case works after tokenizing. Was caching problem.'''
    text = 'I like _MATH_ even _MATH_ when _MATH_, except when _MATH_ is _MATH_! but not _MATH_.'
    tokenizer = English.Defaults.create_tokenizer()
    doc = tokenizer(text)
    assert 'MATH' in [w.text for w in doc]
    assert '_MATH_' not in [w.text for w in doc]

    tokenizer.add_special_case('_MATH_', [{ORTH: '_MATH_'}])
    doc = tokenizer(text)
    assert '_MATH_' in [w.text for w in doc]
    assert 'MATH' not in [w.text for w in doc]

    # For sanity, check it works when pipeline is clean.
    tokenizer = English.Defaults.create_tokenizer()
    tokenizer.add_special_case('_MATH_', [{ORTH: '_MATH_'}])
    doc = tokenizer(text)
    assert '_MATH_' in [w.text for w in doc]
    assert 'MATH' not in [w.text for w in doc]
