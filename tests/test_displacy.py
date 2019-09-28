# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy import displacy
from spacy.displacy.render import DependencyRenderer
from spacy.tokens import Span
from spacy.lang.fa import Persian

from .util import get_doc


def test_displacy_parse_ents(en_vocab):
    """Test that named entities on a Doc are converted into displaCy's format."""
    doc = get_doc(en_vocab, words=["But", "Google", "is", "starting", "from", "behind"])
    doc.ents = [Span(doc, 1, 2, label=doc.vocab.strings["ORG"])]
    ents = displacy.parse_ents(doc)
    assert isinstance(ents, dict)
    assert ents["text"] == "But Google is starting from behind "
    assert ents["ents"] == [{"start": 4, "end": 10, "label": "ORG"}]


def test_displacy_parse_deps(en_vocab):
    """Test that deps and tags on a Doc are converted into displaCy's format."""
    words = ["This", "is", "a", "sentence"]
    heads = [1, 0, 1, -2]
    pos = ["DET", "VERB", "DET", "NOUN"]
    tags = ["DT", "VBZ", "DT", "NN"]
    deps = ["nsubj", "ROOT", "det", "attr"]
    doc = get_doc(en_vocab, words=words, heads=heads, pos=pos, tags=tags, deps=deps)
    deps = displacy.parse_deps(doc)
    assert isinstance(deps, dict)
    assert deps["words"] == [
        {"text": "This", "tag": "DET"},
        {"text": "is", "tag": "AUX"},
        {"text": "a", "tag": "DET"},
        {"text": "sentence", "tag": "NOUN"},
    ]
    assert deps["arcs"] == [
        {"start": 0, "end": 1, "label": "nsubj", "dir": "left"},
        {"start": 2, "end": 3, "label": "det", "dir": "left"},
        {"start": 1, "end": 3, "label": "attr", "dir": "right"},
    ]


def test_displacy_invalid_arcs():
    renderer = DependencyRenderer()
    words = [{"text": "This", "tag": "DET"}, {"text": "is", "tag": "VERB"}]
    arcs = [
        {"start": 0, "end": 1, "label": "nsubj", "dir": "left"},
        {"start": -1, "end": 2, "label": "det", "dir": "left"},
    ]
    with pytest.raises(ValueError):
        renderer.render([{"words": words, "arcs": arcs}])


def test_displacy_spans(en_vocab):
    """Test that displaCy can render Spans."""
    doc = get_doc(en_vocab, words=["But", "Google", "is", "starting", "from", "behind"])
    doc.ents = [Span(doc, 1, 2, label=doc.vocab.strings["ORG"])]
    html = displacy.render(doc[1:4], style="ent")
    assert html.startswith("<div")


def test_displacy_raises_for_wrong_type(en_vocab):
    with pytest.raises(ValueError):
        displacy.render("hello world")


def test_displacy_rtl():
    # Source: http://www.sobhe.ir/hazm/ – is this correct?
    words = ["ما", "بسیار", "کتاب", "می\u200cخوانیم"]
    # These are (likely) wrong, but it's just for testing
    pos = ["PRO", "ADV", "N_PL", "V_SUB"]  # needs to match lang.fa.tag_map
    deps = ["foo", "bar", "foo", "baz"]
    heads = [1, 0, 1, -2]
    nlp = Persian()
    doc = get_doc(nlp.vocab, words=words, pos=pos, tags=pos, heads=heads, deps=deps)
    doc.ents = [Span(doc, 1, 3, label="TEST")]
    html = displacy.render(doc, page=True, style="dep")
    assert "direction: rtl" in html
    assert 'direction="rtl"' in html
    assert 'lang="{}"'.format(nlp.lang) in html
    html = displacy.render(doc, page=True, style="ent")
    assert "direction: rtl" in html
    assert 'lang="{}"'.format(nlp.lang) in html


def test_displacy_render_wrapper(en_vocab):
    """Test that displaCy accepts custom rendering wrapper."""

    def wrapper(html):
        return "TEST" + html + "TEST"

    displacy.set_render_wrapper(wrapper)
    doc = get_doc(en_vocab, words=["But", "Google", "is", "starting", "from", "behind"])
    doc.ents = [Span(doc, 1, 2, label=doc.vocab.strings["ORG"])]
    html = displacy.render(doc, style="ent")
    assert html.startswith("TEST<div")
    assert html.endswith("/div>TEST")
    # Restore
    displacy.set_render_wrapper(lambda html: html)
