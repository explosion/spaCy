import numpy
import pytest

from spacy import displacy
from spacy.displacy.render import DependencyRenderer, EntityRenderer
from spacy.lang.en import English
from spacy.lang.fa import Persian
from spacy.tokens import Span, Doc


@pytest.mark.issue(2361)
def test_issue2361(de_vocab):
    """Test if < is escaped when rendering"""
    chars = ("&lt;", "&gt;", "&amp;", "&quot;")
    words = ["<", ">", "&", '"']
    doc = Doc(de_vocab, words=words, deps=["dep"] * len(words))
    html = displacy.render(doc)
    for char in chars:
        assert char in html


@pytest.mark.issue(2728)
def test_issue2728(en_vocab):
    """Test that displaCy ENT visualizer escapes HTML correctly."""
    doc = Doc(en_vocab, words=["test", "<RELEASE>", "test"])
    doc.ents = [Span(doc, 0, 1, label="TEST")]
    html = displacy.render(doc, style="ent")
    assert "&lt;RELEASE&gt;" in html
    doc.ents = [Span(doc, 1, 2, label="TEST")]
    html = displacy.render(doc, style="ent")
    assert "&lt;RELEASE&gt;" in html


@pytest.mark.issue(3288)
def test_issue3288(en_vocab):
    """Test that retokenization works correctly via displaCy when punctuation
    is merged onto the preceeding token and tensor is resized."""
    words = ["Hello", "World", "!", "When", "is", "this", "breaking", "?"]
    heads = [1, 1, 1, 4, 4, 6, 4, 4]
    deps = ["intj", "ROOT", "punct", "advmod", "ROOT", "det", "nsubj", "punct"]
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    doc.tensor = numpy.zeros((len(words), 96), dtype="float32")
    displacy.render(doc)


@pytest.mark.issue(3531)
def test_issue3531():
    """Test that displaCy renderer doesn't require "settings" key."""
    example_dep = {
        "words": [
            {"text": "But", "tag": "CCONJ"},
            {"text": "Google", "tag": "PROPN"},
            {"text": "is", "tag": "VERB"},
            {"text": "starting", "tag": "VERB"},
            {"text": "from", "tag": "ADP"},
            {"text": "behind.", "tag": "ADV"},
        ],
        "arcs": [
            {"start": 0, "end": 3, "label": "cc", "dir": "left"},
            {"start": 1, "end": 3, "label": "nsubj", "dir": "left"},
            {"start": 2, "end": 3, "label": "aux", "dir": "left"},
            {"start": 3, "end": 4, "label": "prep", "dir": "right"},
            {"start": 4, "end": 5, "label": "pcomp", "dir": "right"},
        ],
    }
    example_ent = {
        "text": "But Google is starting from behind.",
        "ents": [{"start": 4, "end": 10, "label": "ORG"}],
    }
    dep_html = displacy.render(example_dep, style="dep", manual=True)
    assert dep_html
    ent_html = displacy.render(example_ent, style="ent", manual=True)
    assert ent_html


@pytest.mark.issue(3882)
def test_issue3882(en_vocab):
    """Test that displaCy doesn't serialize the doc.user_data when making a
    copy of the Doc.
    """
    doc = Doc(en_vocab, words=["Hello", "world"], deps=["dep", "dep"])
    doc.user_data["test"] = set()
    displacy.parse_deps(doc)


@pytest.mark.issue(5838)
def test_issue5838():
    # Displacy's EntityRenderer break line
    # not working after last entity
    sample_text = "First line\nSecond line, with ent\nThird line\nFourth line\n"
    nlp = English()
    doc = nlp(sample_text)
    doc.ents = [Span(doc, 7, 8, label="test")]
    html = displacy.render(doc, style="ent")
    found = html.count("</br>")
    assert found == 4


def test_displacy_parse_ents(en_vocab):
    """Test that named entities on a Doc are converted into displaCy's format."""
    doc = Doc(en_vocab, words=["But", "Google", "is", "starting", "from", "behind"])
    doc.ents = [Span(doc, 1, 2, label=doc.vocab.strings["ORG"])]
    ents = displacy.parse_ents(doc)
    assert isinstance(ents, dict)
    assert ents["text"] == "But Google is starting from behind "
    assert ents["ents"] == [
        {"start": 4, "end": 10, "label": "ORG", "kb_id": "", "kb_url": "#"}
    ]

    doc.ents = [Span(doc, 1, 2, label=doc.vocab.strings["ORG"], kb_id="Q95")]
    ents = displacy.parse_ents(doc)
    assert isinstance(ents, dict)
    assert ents["text"] == "But Google is starting from behind "
    assert ents["ents"] == [
        {"start": 4, "end": 10, "label": "ORG", "kb_id": "Q95", "kb_url": "#"}
    ]


def test_displacy_parse_ents_with_kb_id_options(en_vocab):
    """Test that named entities with kb_id on a Doc are converted into displaCy's format."""
    doc = Doc(en_vocab, words=["But", "Google", "is", "starting", "from", "behind"])
    doc.ents = [Span(doc, 1, 2, label=doc.vocab.strings["ORG"], kb_id="Q95")]

    ents = displacy.parse_ents(
        doc, {"kb_url_template": "https://www.wikidata.org/wiki/{}"}
    )
    assert isinstance(ents, dict)
    assert ents["text"] == "But Google is starting from behind "
    assert ents["ents"] == [
        {
            "start": 4,
            "end": 10,
            "label": "ORG",
            "kb_id": "Q95",
            "kb_url": "https://www.wikidata.org/wiki/Q95",
        }
    ]


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
