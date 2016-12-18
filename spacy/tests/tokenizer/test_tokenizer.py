# coding: utf-8
from __future__ import unicode_literals

import pytest
import io
import pickle
import cloudpickle
import tempfile

from ... import util
from ...language_data import TOKENIZER_PREFIXES

en_search_prefixes = util.compile_prefix_regex(TOKENIZER_PREFIXES).search

# @pytest.mark.xfail
# def test_pickle(en_tokenizer):
#     file_ = io.BytesIO()
#     cloudpickle.dump(en_tokenizer, file_)
#     file_.seek(0)
#     loaded = pickle.load(file_)
#     assert loaded is not None

def test_pre_punct_regex():
    string = "(can't"
    match = en_search_prefixes(string)
    assert match.group() == "("

def test_no_word(en_tokenizer):
    tokens = en_tokenizer(u'')
    assert len(tokens) == 0


def test_single_word(en_tokenizer):
    tokens = en_tokenizer(u'hello')
    assert tokens[0].orth_ == 'hello'


def test_two_words(en_tokenizer):
    tokens = en_tokenizer('hello possums')
    assert len(tokens) == 2
    assert tokens[0].orth_ != tokens[1].orth_


def test_punct(en_tokenizer):
    tokens = en_tokenizer('hello, possums.')
    assert len(tokens) == 4
    assert tokens[0].orth_ == 'hello'
    assert tokens[1].orth_ == ','
    assert tokens[2].orth_ == 'possums'
    assert tokens[1].orth_ != 'hello'


def test_digits(en_tokenizer):
    tokens = en_tokenizer('The year: 1984.')
    assert len(tokens) == 5
    assert tokens[0].orth == en_tokenizer.vocab['The'].orth
    assert tokens[3].orth == en_tokenizer.vocab['1984'].orth


def test_contraction(en_tokenizer):
    tokens = en_tokenizer("don't giggle")
    assert len(tokens) == 3
    assert tokens[1].orth == en_tokenizer.vocab["n't"].orth
    tokens = en_tokenizer("i said don't!")
    assert len(tokens) == 5
    assert tokens[4].orth == en_tokenizer.vocab['!'].orth

def test_contraction_punct(en_tokenizer):
    tokens = [w.text for w in en_tokenizer("(can't")]
    assert tokens == ['(', 'ca', "n't"]
    tokens = en_tokenizer("`ain't")
    assert len(tokens) == 3
    tokens = en_tokenizer('''"isn't''')
    assert len(tokens) == 3
    tokens = en_tokenizer("can't!")
    assert len(tokens) == 3


def test_sample(en_tokenizer):
    text = """Tributes pour in for late British Labour Party leader

Tributes poured in from around the world Thursday
to the late Labour Party leader John Smith, who died earlier from a massive
heart attack aged 55.

In Washington, the US State Department issued a statement regretting "the
untimely death" of the rapier-tongued Scottish barrister and parliamentarian.

"Mr. Smith, throughout his distinguished"""

    tokens = en_tokenizer(text)
    assert len(tokens) > 5


def test_cnts1(en_tokenizer):
    text = u"""The U.S. Army likes Shock and Awe."""
    tokens = en_tokenizer(text)
    assert len(tokens) == 8


def test_cnts2(en_tokenizer):
    text = u"""U.N. regulations are not a part of their concern."""
    tokens = en_tokenizer(text)
    assert len(tokens) == 10


def test_cnts3(en_tokenizer):
    text = u"“Isn't it?”"
    tokens = en_tokenizer(text)
    words = [t.orth_ for t in tokens]
    assert len(words) == 6


def test_cnts4(en_tokenizer):
    text = u"""Yes! "I'd rather have a walk", Ms. Comble sighed. """
    tokens = en_tokenizer(text)
    words = [t.orth_ for t in tokens]
    assert len(words) == 15


def test_cnts5(en_tokenizer):
    text = """'Me too!', Mr. P. Delaware cried. """
    tokens = en_tokenizer(text)
    assert len(tokens) == 11


@pytest.mark.xfail
def test_mr(en_tokenizer):
    text = """Today is Tuesday.Mr."""
    tokens = en_tokenizer(text)
    assert len(tokens) == 5
    assert [w.orth_ for w in tokens] == ['Today', 'is', 'Tuesday', '.', 'Mr.']


def test_cnts6(en_tokenizer):
    text = u'They ran about 10km.'
    tokens = en_tokenizer(text)
    words = [t.orth_ for t in tokens]
    assert len(words) == 6

def test_bracket_period(en_tokenizer):
    text = u'(And a 6a.m. run through Washington Park).'
    tokens = en_tokenizer(text)
    assert tokens[len(tokens) - 1].orth_ == u'.'


def test_ie(en_tokenizer):
    text = u"It's mediocre i.e. bad."
    tokens = en_tokenizer(text)
    assert len(tokens) == 6
    assert tokens[3].orth_ == "i.e."


def test_two_whitespace(en_tokenizer):
    orig_str = u'there are 2 spaces after this  '
    tokens = en_tokenizer(orig_str)
    assert repr(tokens.text_with_ws) == repr(orig_str)


@pytest.mark.xfail
def test_em_dash_infix(en_tokenizer):
    # Re Issue #225
    tokens = en_tokenizer('''Will this road take me to Puddleton?\u2014No, '''
                          '''you'll have to walk there.\u2014Ariel.''')
    assert tokens[6].text == 'Puddleton'
    assert tokens[7].text == '?'
    assert tokens[8].text == '\u2014'

#def test_cnts7():
#    text = 'But then the 6,000-year ice age came...'
#    tokens = EN.tokenize(text)
#    assert len(tokens) == 10
