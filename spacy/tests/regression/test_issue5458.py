# coding: utf-8
from __future__ import unicode_literals

from spacy.lang.en import English
from spacy.lang.en.syntax_iterators import noun_chunks
from spacy.tests.util import get_doc
from spacy.vocab import Vocab


def test_issue5458():
    # Test that the noun chuncker does not generate overlapping spans
    # fmt: off
    words = ["In", "an", "era", "where", "markets", "have", "brought", "prosperity", "and", "empowerment", "."]
    vocab = Vocab(strings=words)
    dependencies = ["ROOT", "det", "pobj", "advmod", "nsubj", "aux", "relcl", "dobj", "cc", "conj", "punct"]
    pos_tags = ["ADP", "DET", "NOUN", "ADV", "NOUN", "AUX", "VERB", "NOUN", "CCONJ", "NOUN", "PUNCT"]
    heads = [0, 1, -2, 6, 2, 1, -4, -1, -1, -2, -10]
    # fmt: on

    en_doc = get_doc(vocab, words, pos_tags, heads, dependencies)
    en_doc.noun_chunks_iterator = noun_chunks

    # if there are overlapping spans, this will fail with an E102 error "Can't merge non-disjoint spans"
    nlp = English()
    merge_nps = nlp.create_pipe("merge_noun_chunks")
    merge_nps(en_doc)
