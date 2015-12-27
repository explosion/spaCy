from __future__ import unicode_literals
import pytest
import gc

from spacy.en import English
import os

# Let this have its own instances, as we have to be careful about memory here
# that's the point, after all

@pytest.mark.models
def get_orphan_token(text, i):
    nlp = English()
    tokens = nlp(text)
    gc.collect()
    token = tokens[i]
    del tokens
    return token


@pytest.mark.models
def test_orphan():
    orphan = get_orphan_token('An orphan token', 1)
    gc.collect()
    dummy = get_orphan_token('Load and flush the memory', 0)
    dummy = get_orphan_token('Load again...', 0)
    assert orphan.orth_ == 'orphan'
    assert orphan.pos_ in ('ADJ', 'NOUN')
    assert orphan.head.orth_ == 'token'


def _orphan_from_list(toks):
    ''' Take the tokens from nlp(), append them to a list, return the list '''
    lst = []
    for tok in toks:
        lst.append(tok)
    return lst


@pytest.mark.models
def test_list_orphans():
    # Test case from NSchrading
    nlp = English()
    samples = ["a", "test blah wat okay"]
    lst = []
    for sample in samples:
        # Go through all the samples, call nlp() on each to get tokens,
        # pass those tokens to the _orphan_from_list() function, get a list back
        # and put all results in another list
        lst.extend(_orphan_from_list(nlp(sample)))
    # go through the list of all tokens and try to print orth_
    orths = ['a', 'test', 'blah', 'wat', 'okay']
    for i, l in enumerate(lst):
        assert l.orth_  == orths[i]
