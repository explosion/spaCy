# coding: utf-8
from __future__ import unicode_literals

from ...tokens import Doc
from ..util import get_doc, apply_transition_sequence

import pytest


@pytest.mark.parametrize('text', ["A test sentence"])
@pytest.mark.parametrize('punct', ['.', '!', '?', ''])
def test_parser_sbd_single_punct(en_tokenizer, text, punct):
    heads = [2, 1, 0, -1] if punct else [2, 1, 0]
    tokens = en_tokenizer(text + punct)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads)
    assert len(doc) == 4 if punct else 3
    assert len(list(doc.sents)) == 1
    assert sum(len(sent) for sent in doc.sents) == len(doc)


def test_parser_sentence_breaks(en_tokenizer, en_parser):
    text = "This is a sentence . This is another one ."
    heads = [1, 0, 1, -2, -3, 1, 0, 1, -2, -3]
    deps = ['nsubj', 'ROOT', 'det', 'attr', 'punct', 'nsubj', 'ROOT', 'det',
            'attr', 'punct']
    transition = ['L-nsubj', 'S', 'L-det', 'R-attr', 'D', 'R-punct', 'B-ROOT',
                  'L-nsubj', 'S', 'L-attr', 'R-attr', 'D', 'R-punct']

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads, deps=deps)
    apply_transition_sequence(en_parser, doc, transition)

    assert len(list(doc.sents)) == 2
    for token in doc:
        assert token.dep != 0 or token.is_space
    assert [token.head.i for token in doc ] == [1, 1, 3, 1, 1, 6, 6, 8, 6, 6]


# Currently, there's no way of setting the serializer data for the parser
# without loading the models, so we can't remove the model dependency here yet.

@pytest.mark.models
def test_parser_sbd_serialization_projective(EN):
    """Test that before and after serialization, the sentence boundaries are
    the same."""

    text = "I bought a couch from IKEA It wasn't very comfortable."
    transition = ['L-nsubj', 'S', 'L-det', 'R-dobj', 'D', 'R-prep', 'R-pobj',
                  'B-ROOT', 'L-nsubj', 'R-neg', 'D', 'S', 'L-advmod',
                  'R-acomp', 'D', 'R-punct']

    doc = EN.tokenizer(text)
    apply_transition_sequence(EN.parser, doc, transition)
    doc_serialized = Doc(EN.vocab).from_bytes(doc.to_bytes())
    assert doc.is_parsed == True
    assert doc_serialized.is_parsed == True
    assert doc.to_bytes() == doc_serialized.to_bytes()
    assert [s.text for s in doc.sents] == [s.text for s in doc_serialized.sents]
