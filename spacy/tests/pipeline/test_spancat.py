# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Span
from spacy.language import Language
from spacy.pipeline.spancat import SpanCategorizer


def test_init_spancat(en_vocab):
    model = SpanCategorizer(en_vocab)


@pytest.fixture
def spancat(en_vocab):
    return SpanCategorizer(en_vocab)


def test_spancat_add_label(spancat):
    assert "NP" not in spancat.labels
    spancat.add_label("NP")
    assert "NP" in spancat.labels

def test_spancat_init_model(spancat):
    model = spancat.Model(10, width=10, embed_size=10)
