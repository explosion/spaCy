from __future__ import unicode_literals
import pytest

from spacy.strings import StringStore
from spacy.matcher import *
from spacy.attrs import LOWER
from spacy.tokens.doc import Doc
from spacy.vocab import Vocab
from spacy.en import English


@pytest.fixture
def matcher():
    patterns = {
        'JS': ['PRODUCT', {}, [[{'ORTH': 'JavaScript'}]]],
        'GoogleNow':  ['PRODUCT', {}, [[{'ORTH': 'Google'}, {'ORTH': 'Now'}]]],
        'Java':       ['PRODUCT', {}, [[{'LOWER': 'java'}]]],
    }
    return Matcher(Vocab(lex_attr_getters=English.Defaults.lex_attr_getters), patterns)


def test_compile(matcher):
    assert matcher.n_patterns == 3


def test_no_match(matcher):
    doc = Doc(matcher.vocab, words=['I', 'like', 'cheese', '.'])
    assert matcher(doc) == []


def test_match_start(matcher):
    doc = Doc(matcher.vocab, words=['JavaScript', 'is', 'good'])
    assert matcher(doc) == [(matcher.vocab.strings['JS'],
                             matcher.vocab.strings['PRODUCT'], 0, 1)]


def test_match_end(matcher):
    doc = Doc(matcher.vocab, words=['I', 'like', 'java'])
    assert matcher(doc) == [(doc.vocab.strings['Java'],
                             doc.vocab.strings['PRODUCT'], 2, 3)]


def test_match_middle(matcher):
    doc = Doc(matcher.vocab, words=['I', 'like', 'Google', 'Now', 'best'])
    assert matcher(doc) == [(doc.vocab.strings['GoogleNow'],
                             doc.vocab.strings['PRODUCT'], 2, 4)]


def test_match_multi(matcher):
    doc = Doc(matcher.vocab, words='I like Google Now and java best'.split())
    assert matcher(doc) == [(doc.vocab.strings['GoogleNow'],
                             doc.vocab.strings['PRODUCT'], 2, 4),
                            (doc.vocab.strings['Java'],
                             doc.vocab.strings['PRODUCT'], 5, 6)]

def test_match_zero(matcher):
    matcher.add('Quote', '', {}, [
        [
            {'ORTH': '"'},
            {'OP': '!', 'IS_PUNCT': True},
            {'OP': '!', 'IS_PUNCT': True},
            {'ORTH': '"'}
        ]])
    doc = Doc(matcher.vocab, words='He said , " some words " ...'.split())
    assert len(matcher(doc)) == 1
    doc = Doc(matcher.vocab, words='He said , " some three words " ...'.split())
    assert len(matcher(doc)) == 0
    matcher.add('Quote', '', {}, [
        [
            {'ORTH': '"'},
            {'IS_PUNCT': True},
            {'IS_PUNCT': True},
            {'IS_PUNCT': True},
            {'ORTH': '"'}
        ]])
    assert len(matcher(doc)) == 0


def test_match_zero_plus(matcher):
    matcher.add('Quote', '', {}, [
        [
            {'ORTH': '"'},
            {'OP': '*', 'IS_PUNCT': False},
            {'ORTH': '"'}
        ]])
    doc = Doc(matcher.vocab, words='He said , " some words " ...'.split())
    assert len(matcher(doc)) == 1


def test_phrase_matcher():
    vocab = Vocab(lex_attr_getters=English.Defaults.lex_attr_getters)
    matcher = PhraseMatcher(vocab, [Doc(vocab, words='Google Now'.split())])
    doc = Doc(vocab, words=['I', 'like', 'Google', 'Now', 'best'])
    assert len(matcher(doc)) == 1


#@pytest.mark.models
#def test_match_preserved(EN):
#    patterns = {
#        'JS': ['PRODUCT', {}, [[{'ORTH': 'JavaScript'}]]],
#        'GoogleNow':  ['PRODUCT', {}, [[{'ORTH': 'Google'}, {'ORTH': 'Now'}]]],
#        'Java':       ['PRODUCT', {}, [[{'LOWER': 'java'}]]],
#    }
#    matcher = Matcher(EN.vocab, patterns)
#    doc = EN.tokenizer('I like java.')
#    EN.tagger(doc)
#    assert len(doc.ents) == 0
#    doc = EN.tokenizer('I like java.')
#    doc.ents += tuple(matcher(doc))
#    assert len(doc.ents) == 1
#    EN.tagger(doc)
#    EN.entity(doc)
#    assert len(doc.ents) == 1
