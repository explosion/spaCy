# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Doc
from spacy.displacy import render
from spacy.gold import iob_to_biluo
from spacy.lang.it import Italian

from ..util import add_vecs_to_vocab


@pytest.mark.xfail
def test_issue2179():
    """Test that spurious 'extra_labels' aren't created when initializing NER."""
    nlp = Italian()
    ner = nlp.create_pipe('ner')
    ner.add_label('CITIZENSHIP')
    nlp.add_pipe(ner)
    nlp.begin_training()
    nlp2 = Italian()
    nlp2.add_pipe(nlp2.create_pipe('ner'))
    nlp2.from_bytes(nlp.to_bytes())
    assert 'extra_labels' not in nlp2.get_pipe('ner').cfg
    assert nlp2.get_pipe('ner').labels == ['CITIZENSHIP']


def test_issue2219(en_vocab):
    vectors = [("a", [1, 2, 3]), ("letter", [4, 5, 6])]
    add_vecs_to_vocab(en_vocab, vectors)
    [(word1, vec1), (word2, vec2)] = vectors
    doc = Doc(en_vocab, words=[word1, word2])
    assert doc[0].similarity(doc[1]) == doc[1].similarity(doc[0])


def test_issue2361(de_tokenizer):
    chars = ('&lt;', '&gt;', '&amp;', '&quot;')
    doc = de_tokenizer('< > & " ')
    doc.is_parsed = True
    doc.is_tagged = True
    html = render(doc)
    for char in chars:
        assert char in html


def test_issue2385():
    """Test that IOB tags are correctly converted to BILUO tags."""
    # fix bug in labels with a 'b' character
    tags1 = ('B-BRAWLER', 'I-BRAWLER', 'I-BRAWLER')
    assert iob_to_biluo(tags1) == ['B-BRAWLER', 'I-BRAWLER', 'L-BRAWLER']
    # maintain support for iob1 format
    tags2 = ('I-ORG', 'I-ORG', 'B-ORG')
    assert iob_to_biluo(tags2) == ['B-ORG', 'L-ORG', 'U-ORG']
    # maintain support for iob2 format
    tags3 = ('B-PERSON', 'I-PERSON', 'B-PERSON')
    assert iob_to_biluo(tags3) ==['B-PERSON', 'L-PERSON', 'U-PERSON']


@pytest.mark.parametrize('tags', [
    ('B-ORG', 'L-ORG'), ('B-PERSON', 'I-PERSON', 'L-PERSON'), ('U-BRAWLER', 'U-BRAWLER')])
def test_issue2385_biluo(tags):
    """Test that BILUO-compatible tags aren't modified."""
    assert iob_to_biluo(tags) == list(tags)

def test_issue2482():
    '''Test we can serialize and deserialize a blank NER or parser model.'''
    nlp = Italian()
    nlp.add_pipe(nlp.create_pipe('ner'))
    b = nlp.to_bytes()
    nlp2 = Italian().from_bytes(b)
