# coding: utf-8
from __future__ import unicode_literals

import numpy
from spacy import displacy

from ..util import get_doc


def test_issue3288(en_vocab):
    """Test that retokenization works correctly via displaCy when punctuation
    is merged onto the preceeding token and tensor is resized."""
    words = ["Hello", "World", "!", "When", "is", "this", "breaking", "?"]
    heads = [1, 0, -1, 1, 0, 1, -2, -3]
    deps = ["intj", "ROOT", "punct", "advmod", "ROOT", "det", "nsubj", "punct"]
    doc = get_doc(en_vocab, words=words, heads=heads, deps=deps)
    doc.tensor = numpy.zeros((len(words), 96), dtype="float32")
    displacy.render(doc)
