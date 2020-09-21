import pytest
from spacy import displacy
from spacy.displacy.render import DependencyRenderer, EntityRenderer
from spacy.tokens import Span, Doc
from spacy.lang.fa import Persian


def test_displacy_parse_ents(en_vocab):
    """Test that named entities on a Doc are converted into displaCy's format."""
    doc = Doc(en_vocab, words=["But", "Google", "is", "starting", "from", "behind"])
    doc.ents = [Span(doc, 1, 2, label=doc.vocab.strings["ORG"])]
    ents = displacy.parse_ents(doc)
    assert isinstance(ents, dict)
    assert ents["text"] == "But Google is starting from behind "
    assert ents["ents"] == [{"start": 4, "end": 10, "label": "ORG"}]


def test_displacy_parse_deps(en_vocab):
    """Test that deps and tags on a Doc are converted into displaCy's format."""
    words = ["This", "is", "a", "sentence"]
    heads = [1, 1, 3, 1]
    pos = ["DET", "VERB", "DET", "NOUN"]
    tags = ["DT", "VBZ", "DT", "NN"]
    deps = ["nsubj", "ROOT", "det", "attr"]
    doc = Doc(en_vocab, words=words, heads=heads, pos=pos, tags=tags, deps=deps)
    deps = displacy.parse_deps(doc)
    assert isinstance(deps, dict)
    assert deps["words"] == [
        {"lemma": None, "text": words[0], "tag": pos[0]},
        {"lemma": None, "text": words[1], "tag": pos[1]},
        {"lemma": None, "text": words[2], "tag": pos[2]},
        {"lemma": None, "text": words[3], "tag": pos[3]},
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
    doc = Doc(en_vocab, words=["But", "Google", "is", "starting", "from", "behind"])
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
    heads = [1, 0, 3, 1]
    nlp = Persian()
    doc = Doc(nlp.vocab, words=words, tags=pos, heads=heads, deps=deps)
    doc.ents = [Span(doc, 1, 3, label="TEST")]
    html = displacy.render(doc, page=True, style="dep")
    assert "direction: rtl" in html
    assert 'direction="rtl"' in html
    assert f'lang="{nlp.lang}"' in html
    html = displacy.render(doc, page=True, style="ent")
    assert "direction: rtl" in html
    assert f'lang="{nlp.lang}"' in html


def test_displacy_render_wrapper(en_vocab):
    """Test that displaCy accepts custom rendering wrapper."""

    def wrapper(html):
        return "TEST" + html + "TEST"

    displacy.set_render_wrapper(wrapper)
    doc = Doc(en_vocab, words=["But", "Google", "is", "starting", "from", "behind"])
    doc.ents = [Span(doc, 1, 2, label=doc.vocab.strings["ORG"])]
    html = displacy.render(doc, style="ent")
    assert html.startswith("TEST<div")
    assert html.endswith("/div>TEST")
    # Restore
    displacy.set_render_wrapper(lambda html: html)


def test_displacy_options_case():
    ents = ["foo", "BAR"]
    colors = {"FOO": "red", "bar": "green"}
    renderer = EntityRenderer({"ents": ents, "colors": colors})
    text = "abcd"
    labels = ["foo", "bar", "FOO", "BAR"]
    spans = [{"start": i, "end": i + 1, "label": labels[i]} for i in range(len(text))]
    result = renderer.render_ents("abcde", spans, None).split("\n\n")
    assert "red" in result[0] and "foo" in result[0]
    assert "green" in result[1] and "bar" in result[1]
    assert "red" in result[2] and "FOO" in result[2]
    assert "green" in result[3] and "BAR" in result[3]
