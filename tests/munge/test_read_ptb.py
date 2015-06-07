from spacy.munge import read_ptb

import pytest

from os import path

ptb_loc = path.join(path.dirname(__file__), 'wsj_0001.parse')
file3_loc = path.join(path.dirname(__file__), 'wsj_0003.parse')


@pytest.fixture
def ptb_text():
    return open(path.join(ptb_loc)).read()


@pytest.fixture
def sentence_strings(ptb_text):
    return read_ptb.split(ptb_text)


def test_split(sentence_strings):
    assert len(sentence_strings) == 2
    assert sentence_strings[0].startswith('(TOP (S (NP-SBJ')
    assert sentence_strings[0].endswith('(. .)))')
    assert sentence_strings[1].startswith('(TOP (S (NP-SBJ')
    assert sentence_strings[1].endswith('(. .)))')


def test_tree_read(sentence_strings):
    words, brackets = read_ptb.parse(sentence_strings[0])
    assert len(brackets) == 11
    string = ("Pierre Vinken , 61 years old , will join the board as a nonexecutive "
              "director Nov. 29 .")
    word_strings = string.split()
    starts = [s for l, s, e in brackets]
    ends = [e for l, s, e in brackets]
    assert min(starts) == 0
    assert max(ends) == len(words)
    assert brackets[-1] == ('S', 0, len(words))
    assert ('NP-SBJ', 0, 7) in brackets


def test_traces():
    sent_strings = sentence_strings(open(file3_loc).read())
    words, brackets = read_ptb.parse(sent_strings[0])
    assert len(words) == 36
