import numpy
import pytest

from wasabi.util import supports_ansi

from spacy import displacy
from spacy.displacy.render import DependencyRenderer, EntityRenderer
from spacy.displacy.pprint import AttributeFormat, render_dep_tree, render_table
from spacy.lang.en import English
from spacy.lang.fa import Persian
from spacy.tokens import Span, Doc, Token


SUPPORTS_ANSI = supports_ansi()


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


@pytest.mark.issue(5447)
def test_issue5447():
    """Test that overlapping arcs get separate levels, unless they're identical."""
    renderer = DependencyRenderer()
    words = [
        {"text": "This", "tag": "DT"},
        {"text": "is", "tag": "VBZ"},
        {"text": "a", "tag": "DT"},
        {"text": "sentence.", "tag": "NN"},
    ]
    arcs = [
        {"start": 0, "end": 1, "label": "nsubj", "dir": "left"},
        {"start": 2, "end": 3, "label": "det", "dir": "left"},
        {"start": 2, "end": 3, "label": "overlap", "dir": "left"},
        {"end": 3, "label": "overlap", "start": 2, "dir": "left"},
        {"start": 1, "end": 3, "label": "attr", "dir": "left"},
    ]
    renderer.render([{"words": words, "arcs": arcs}])
    assert renderer.highest_level == 3


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


def test_displacy_parse_spans(en_vocab):
    """Test that spans on a Doc are converted into displaCy's format."""
    doc = Doc(en_vocab, words=["Welcome", "to", "the", "Bank", "of", "China"])
    doc.spans["sc"] = [Span(doc, 3, 6, "ORG"), Span(doc, 5, 6, "GPE")]
    spans = displacy.parse_spans(doc)
    assert isinstance(spans, dict)
    assert spans["text"] == "Welcome to the Bank of China "
    assert spans["spans"] == [
        {
            "start": 15,
            "end": 28,
            "start_token": 3,
            "end_token": 6,
            "label": "ORG",
            "kb_id": "",
            "kb_url": "#",
        },
        {
            "start": 23,
            "end": 28,
            "start_token": 5,
            "end_token": 6,
            "label": "GPE",
            "kb_id": "",
            "kb_url": "#",
        },
    ]


def test_displacy_parse_spans_with_kb_id_options(en_vocab):
    """Test that spans with kb_id on a Doc are converted into displaCy's format"""
    doc = Doc(en_vocab, words=["Welcome", "to", "the", "Bank", "of", "China"])
    doc.spans["sc"] = [
        Span(doc, 3, 6, "ORG", kb_id="Q790068"),
        Span(doc, 5, 6, "GPE", kb_id="Q148"),
    ]

    spans = displacy.parse_spans(
        doc, {"kb_url_template": "https://wikidata.org/wiki/{}"}
    )
    assert isinstance(spans, dict)
    assert spans["text"] == "Welcome to the Bank of China "
    assert spans["spans"] == [
        {
            "start": 15,
            "end": 28,
            "start_token": 3,
            "end_token": 6,
            "label": "ORG",
            "kb_id": "Q790068",
            "kb_url": "https://wikidata.org/wiki/Q790068",
        },
        {
            "start": 23,
            "end": 28,
            "start_token": 5,
            "end_token": 6,
            "label": "GPE",
            "kb_id": "Q148",
            "kb_url": "https://wikidata.org/wiki/Q148",
        },
    ]


def test_displacy_parse_spans_different_spans_key(en_vocab):
    """Test that spans in a different spans key will be parsed"""
    doc = Doc(en_vocab, words=["Welcome", "to", "the", "Bank", "of", "China"])
    doc.spans["sc"] = [Span(doc, 3, 6, "ORG"), Span(doc, 5, 6, "GPE")]
    doc.spans["custom"] = [Span(doc, 3, 6, "BANK")]
    spans = displacy.parse_spans(doc, options={"spans_key": "custom"})

    assert isinstance(spans, dict)
    assert spans["text"] == "Welcome to the Bank of China "
    assert spans["spans"] == [
        {
            "start": 15,
            "end": 28,
            "start_token": 3,
            "end_token": 6,
            "label": "BANK",
            "kb_id": "",
            "kb_url": "#",
        }
    ]


def test_displacy_parse_empty_spans_key(en_vocab):
    """Test that having an unset spans key doesn't raise an error"""
    doc = Doc(en_vocab, words=["Welcome", "to", "the", "Bank", "of", "China"])
    doc.spans["custom"] = [Span(doc, 3, 6, "BANK")]
    with pytest.warns(UserWarning, match="W117"):
        spans = displacy.parse_spans(doc)

    assert isinstance(spans, dict)


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


@pytest.mark.issue(10672)
def test_displacy_manual_sorted_entities():
    doc = {
        "text": "But Google is starting from behind.",
        "ents": [
            {"start": 14, "end": 22, "label": "SECOND"},
            {"start": 4, "end": 10, "label": "FIRST"},
        ],
        "title": None,
    }

    html = displacy.render(doc, style="ent", manual=True)
    assert html.find("FIRST") < html.find("SECOND")


@pytest.fixture
def horse_doc(en_vocab):
    return Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )


def test_viz_dep_tree_basic(en_vocab):
    """Test basic dependency tree display."""
    doc = Doc(
        en_vocab,
        words=[
            "The",
            "big",
            "dog",
            "chased",
            "the",
            "frightened",
            "cat",
            "mercilessly",
            ".",
        ],
        heads=[2, 2, 3, None, 6, 6, 3, 3, 3],
        deps=["dep"] * 9,
    )
    dep_tree = render_dep_tree(doc[0 : len(doc)], True)
    assert dep_tree == [
        "<╗  ",
        "<╣  ",
        "═╝<╗",
        "═══╣",
        "<╗ ║",
        "<╣ ║",
        "═╝<╣",
        "<══╣",
        "<══╝",
    ]
    dep_tree = render_dep_tree(doc[0 : len(doc)], False)
    assert dep_tree == [
        "  ╔>",
        "  ╠>",
        "╔>╚═",
        "╠═══",
        "║ ╔>",
        "║ ╠>",
        "╠>╚═",
        "╠══>",
        "╚══>",
    ]


def test_viz_dep_tree_non_initial_sent(en_vocab):
    """Test basic dependency tree display."""
    doc = Doc(
        en_vocab,
        words=[
            "Something",
            "happened",
            ".",
            "The",
            "big",
            "dog",
            "chased",
            "the",
            "frightened",
            "cat",
            "mercilessly",
            ".",
        ],
        heads=[0, None, 0, 5, 5, 6, None, 9, 9, 6, 6, 6],
        deps=["dep"] * 12,
    )
    dep_tree = render_dep_tree(doc[3 : len(doc)], True)
    assert dep_tree == [
        "<╗  ",
        "<╣  ",
        "═╝<╗",
        "═══╣",
        "<╗ ║",
        "<╣ ║",
        "═╝<╣",
        "<══╣",
        "<══╝",
    ]
    dep_tree = render_dep_tree(doc[3 : len(doc)], False)
    assert dep_tree == [
        "  ╔>",
        "  ╠>",
        "╔>╚═",
        "╠═══",
        "║ ╔>",
        "║ ╠>",
        "╠>╚═",
        "╠══>",
        "╚══>",
    ]


def test_viz_dep_tree_non_projective(horse_doc):
    """Test dependency tree display with a non-projective dependency."""
    dep_tree = render_dep_tree(horse_doc[0 : len(horse_doc)], True)
    assert dep_tree == [
        "<╗    ",
        "═╩═══╗",
        "<╗   ║",
        "═╩═╗<╣",
        "<══║═╣",
        "<╗ ║ ║",
        "<╣ ║ ║",
        "═╝<╝ ║",
        "<════╝",
    ]
    dep_tree = render_dep_tree(horse_doc[0 : len(horse_doc)], False)
    assert dep_tree == [
        "    ╔>",
        "╔═══╩═",
        "║   ╔>",
        "╠>╔═╩═",
        "╠═║══>",
        "║ ║ ╔>",
        "║ ║ ╠>",
        "║ ╚>╚═",
        "╚════>",
    ]


def test_viz_dep_tree_highly_nonprojective(pl_vocab):
    """Test a highly non-projective tree (colloquial Polish)."""
    doc = Doc(
        pl_vocab,
        words=[
            "Owczarki",
            "przecież",
            "niemieckie",
            "zawsze",
            "wierne",
            "są",
            "bardzo",
            ".",
        ],
        heads=[5, 5, 0, 5, 5, None, 4, 5],
        deps=["dep"] * 8,
    )
    dep_tree = render_dep_tree(doc[0 : len(doc)], True)
    assert dep_tree == [
        "═╗<╗",
        " ║<╣",
        "<╝ ║",
        "<══╣",
        "═╗<╣",
        "═══╣",
        "<╝ ║",
        "<══╝",
    ]
    dep_tree = render_dep_tree(doc[0 : len(doc)], False)
    assert dep_tree == [
        "╔>╔═",
        "╠>║ ",
        "║ ╚>",
        "╠══>",
        "╠>╔═",
        "╠═══",
        "║ ╚>",
        "╚══>",
    ]


def test_viz_dep_tree_input_not_span(horse_doc):
    """Test dependency tree display behaviour when the input is not a Span."""
    with pytest.raises(ValueError):
        render_dep_tree(horse_doc[1:3], True)


def test_viz_render_native_attributes(horse_doc):
    assert AttributeFormat("head.i").render(horse_doc[2]) == "3"
    assert AttributeFormat("head.i").render(horse_doc[2], right_pad_to_len=3) == "3  "
    assert AttributeFormat("dep_").render(horse_doc[2]) == "dep"
    with pytest.raises(AttributeError):
        AttributeFormat("depp").render(horse_doc[2])
    with pytest.raises(AttributeError):
        AttributeFormat("tree_left").render(horse_doc[2])
    with pytest.raises(AttributeError):
        AttributeFormat("tree_right").render(horse_doc[2])


def test_viz_render_colors(horse_doc):
    assert (
        AttributeFormat(
            "dep_",
            value_dep_fg_colors={"dep": 2},
            value_dep_bg_colors={"dep": 11},
        ).render(horse_doc[2])
        == "\x1b[38;5;2;48;5;11mdep\x1b[0m"
        if SUPPORTS_ANSI
        else "dep"
    )

    # foreground only
    assert (
        AttributeFormat(
            "dep_",
            value_dep_fg_colors={"dep": 2},
        ).render(horse_doc[2])
        == "\x1b[38;5;2mdep\x1b[0m"
        if SUPPORTS_ANSI
        else "dep"
    )

    # background only
    assert (
        AttributeFormat(
            "dep_",
            value_dep_bg_colors={"dep": 11},
        ).render(horse_doc[2])
        == "\x1b[48;5;11mdep\x1b[0m"
        if SUPPORTS_ANSI
        else "dep"
    )


def test_viz_render_custom_attributes(horse_doc):
    Token.set_extension("test", default="tested1", force=True)
    assert AttributeFormat("_.test").render(horse_doc[2]) == "tested1"

    class Test:
        def __init__(self):
            self.inner_test = "tested2"

    Token.set_extension("test", default=Test(), force=True)
    assert AttributeFormat("_.test.inner_test").render(horse_doc[2]) == "tested2"

    with pytest.raises(AttributeError):
        AttributeFormat("._depp").render(horse_doc[2])


def test_viz_minimal_render_table_one_sentence(
    fully_featured_doc_one_sentence,
):
    formats = [
        AttributeFormat("tree_left"),
        AttributeFormat("dep_"),
        AttributeFormat("text"),
        AttributeFormat("lemma_"),
        AttributeFormat("pos_"),
        AttributeFormat("tag_"),
        AttributeFormat("morph"),
        AttributeFormat("ent_type_"),
    ]
    assert (
        render_table(fully_featured_doc_one_sentence, formats, spacing=3).strip()
        == """
  ╔>╔═   poss       Sarah     sarah     PROPN   NNP   NounType=prop|Number=sing   PERSON
  ║ ╚>   case       's        's        PART    POS   Poss=yes                          
╔>╚═══   nsubj      sister    sister    NOUN    NN    Number=sing                       
╠═════   ROOT       flew      fly       VERB    VBD   Tense=past|VerbForm=fin           
╠>╔═══   prep       to        to        ADP     IN                                      
║ ║ ╔>   compound   Silicon   silicon   PROPN   NNP   NounType=prop|Number=sing   GPE   
║ ╚>╚═   pobj       Valley    valley    PROPN   NNP   NounType=prop|Number=sing   GPE   
╠══>╔═   prep       via       via       ADP     IN                                      
║   ╚>   pobj       London    london    PROPN   NNP   NounType=prop|Number=sing   GPE   
╚════>   punct      .         .         PUNCT   .     PunctType=peri
    """.strip()
    )


def test_viz_minimal_render_table_empty_text(
    en_vocab,
):
    # no headers
    formats = [
        AttributeFormat("tree_left"),
        AttributeFormat("dep_"),
        AttributeFormat("text"),
        AttributeFormat("lemma_"),
        AttributeFormat("pos_"),
        AttributeFormat("tag_"),
        AttributeFormat("morph"),
        AttributeFormat("ent_type_"),
    ]
    assert render_table(Doc(en_vocab), formats, spacing=3).strip() == ""

    # headers
    formats = [
        AttributeFormat("tree_left", name="tree"),
        AttributeFormat("dep_"),
        AttributeFormat("text"),
        AttributeFormat("lemma_"),
        AttributeFormat("pos_"),
        AttributeFormat("tag_"),
        AttributeFormat("morph"),
        AttributeFormat("ent_type_", name="ent"),
    ]
    assert render_table(Doc(en_vocab), formats, spacing=3).strip() == ""


def test_viz_minimal_render_table_spacing(
    fully_featured_doc_one_sentence,
):
    formats = [
        AttributeFormat("tree_left"),
        AttributeFormat("dep_"),
        AttributeFormat("text"),
        AttributeFormat("lemma_"),
        AttributeFormat("pos_"),
        AttributeFormat("tag_"),
        AttributeFormat("morph"),
        AttributeFormat("ent_type_"),
    ]
    assert (
        render_table(fully_featured_doc_one_sentence, formats, spacing=1).strip()
        == """
  ╔>╔═ poss     Sarah   sarah   PROPN NNP NounType=prop|Number=sing PERSON
  ║ ╚> case     's      's      PART  POS Poss=yes                        
╔>╚═══ nsubj    sister  sister  NOUN  NN  Number=sing                     
╠═════ ROOT     flew    fly     VERB  VBD Tense=past|VerbForm=fin         
╠>╔═══ prep     to      to      ADP   IN                                  
║ ║ ╔> compound Silicon silicon PROPN NNP NounType=prop|Number=sing GPE   
║ ╚>╚═ pobj     Valley  valley  PROPN NNP NounType=prop|Number=sing GPE   
╠══>╔═ prep     via     via     ADP   IN                                  
║   ╚> pobj     London  london  PROPN NNP NounType=prop|Number=sing GPE   
╚════> punct    .       .       PUNCT .   PunctType=peri
    """.strip()
    )


def test_viz_minimal_render_table_two_sentences(
    fully_featured_doc_two_sentences,
):
    formats = [
        AttributeFormat("tree_left"),
        AttributeFormat("dep_"),
        AttributeFormat("text"),
        AttributeFormat("lemma_"),
        AttributeFormat("pos_"),
        AttributeFormat("tag_"),
        AttributeFormat("morph"),
        AttributeFormat("ent_type_"),
    ]

    assert (
        render_table(fully_featured_doc_two_sentences, formats, spacing=3).strip()
        == """
  ╔>╔═   poss       Sarah     sarah     PROPN   NNP   NounType=prop|Number=sing   PERSON
  ║ ╚>   case       's        's        PART    POS   Poss=yes                          
╔>╚═══   nsubj      sister    sister    NOUN    NN    Number=sing                       
╠═════   ROOT       flew      fly       VERB    VBD   Tense=past|VerbForm=fin           
╠>╔═══   prep       to        to        ADP     IN                                      
║ ║ ╔>   compound   Silicon   silicon   PROPN   NNP   NounType=prop|Number=sing   GPE   
║ ╚>╚═   pobj       Valley    valley    PROPN   NNP   NounType=prop|Number=sing   GPE   
╠══>╔═   prep       via       via       ADP     IN                                      
║   ╚>   pobj       London    london    PROPN   NNP   NounType=prop|Number=sing   GPE   
╚════>   punct      .         .         PUNCT   .     PunctType=peri                    


╔>   nsubj   She     she    PRON    PRP   Case=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs    
╠═   ROOT    loved   love   VERB    VBD   Tense=Past|VerbForm=Fin                                  
╠>   dobj    it      it     PRON    PRP   Case=Acc|Gender=Neut|Number=Sing|Person=3|PronType=Prs   
╚>   punct   .       .      PUNCT   .     PunctType=peri    
""".strip()
    )


def test_viz_rich_render_table_one_sentence(
    fully_featured_doc_one_sentence,
):
    formats = [
        AttributeFormat("tree_left", name="tree", aligns="r", fg_color=2),
        AttributeFormat("dep_", name="dep", fg_color=2),
        AttributeFormat("i", name="index", aligns="r"),
        AttributeFormat("text", name="text"),
        AttributeFormat("lemma_", name="lemma"),
        AttributeFormat("pos_", name="pos", fg_color=100),
        AttributeFormat("tag_", name="tag", fg_color=100),
        AttributeFormat("morph", name="morph", fg_color=100, max_width=15),
        AttributeFormat(
            "ent_type_",
            name="ent",
            fg_color=196,
            value_dep_fg_colors={"PERSON": 50},
            value_dep_bg_colors={"PERSON": 12},
        ),
    ]
    assert (
        render_table(fully_featured_doc_one_sentence, formats, spacing=3)
        == "\n\x1b[38;5;2m  tree\x1b[0m   \x1b[38;5;2mdep     \x1b[0m   index   text      lemma     \x1b[38;5;100mpos  \x1b[0m   \x1b[38;5;100mtag\x1b[0m   \x1b[38;5;100mmorph          \x1b[0m   \x1b[38;5;196ment   \x1b[0m\n\x1b[38;5;2m------\x1b[0m   \x1b[38;5;2m--------\x1b[0m   -----   -------   -------   \x1b[38;5;100m-----\x1b[0m   \x1b[38;5;100m---\x1b[0m   \x1b[38;5;100m---------------\x1b[0m   \x1b[38;5;196m------\x1b[0m\n\x1b[38;5;2m  ╔>╔═\x1b[0m   \x1b[38;5;2mposs    \x1b[0m   0       Sarah     sarah     \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196m\x1b[38;5;50;48;5;12mPERSON\x1b[0m\x1b[0m\n\x1b[38;5;2m  ║ ╚>\x1b[0m   \x1b[38;5;2mcase    \x1b[0m   1       's        's        \x1b[38;5;100mPART \x1b[0m   \x1b[38;5;100mPOS\x1b[0m   \x1b[38;5;100mPoss=yes       \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╔>╚═══\x1b[0m   \x1b[38;5;2mnsubj   \x1b[0m   2       sister    sister    \x1b[38;5;100mNOUN \x1b[0m   \x1b[38;5;100mNN \x1b[0m   \x1b[38;5;100mNumber=sing    \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╠═════\x1b[0m   \x1b[38;5;2mROOT    \x1b[0m   3       flew      fly       \x1b[38;5;100mVERB \x1b[0m   \x1b[38;5;100mVBD\x1b[0m   \x1b[38;5;100mTense=past|Verb\x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╠>╔═══\x1b[0m   \x1b[38;5;2mprep    \x1b[0m   4       to        to        \x1b[38;5;100mADP  \x1b[0m   \x1b[38;5;100mIN \x1b[0m   \x1b[38;5;100m               \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m║ ║ ╔>\x1b[0m   \x1b[38;5;2mcompound\x1b[0m   5       Silicon   silicon   \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m║ ╚>╚═\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m   6       Valley    valley    \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m╠══>╔═\x1b[0m   \x1b[38;5;2mprep    \x1b[0m   7       via       via       \x1b[38;5;100mADP  \x1b[0m   \x1b[38;5;100mIN \x1b[0m   \x1b[38;5;100m               \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m║   ╚>\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m   8       London    london    \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m╚════>\x1b[0m   \x1b[38;5;2mpunct   \x1b[0m   9       .         .         \x1b[38;5;100mPUNCT\x1b[0m   \x1b[38;5;100m.  \x1b[0m   \x1b[38;5;100mPunctType=peri \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\n"
        if SUPPORTS_ANSI
        else "\n\x1b[38;5;2m  tree\x1b[0m   \x1b[38;5;2mdep     \x1b[0m   index   text      lemma     pos     tag   morph             ent   \n\x1b[38;5;2m------\x1b[0m   \x1b[38;5;2m--------\x1b[0m   -----   -------   -------   -----   ---   ---------------   ------\n\x1b[38;5;2m  ╔>╔═\x1b[0m   \x1b[38;5;2mposs    \x1b[0m   0       Sarah     sarah     PROPN   NNP   NounType=prop|N   PERSON\n\x1b[38;5;2m  ║ ╚>\x1b[0m   \x1b[38;5;2mcase    \x1b[0m   1       's        's        PART    POS   Poss=yes                \n\x1b[38;5;2m╔>╚═══\x1b[0m   \x1b[38;5;2mnsubj   \x1b[0m   2       sister    sister    NOUN    NN    Number=sing             \n\x1b[38;5;2m╠═════\x1b[0m   \x1b[38;5;2mROOT    \x1b[0m   3       flew      fly       VERB    VBD   Tense=past|Verb         \n\x1b[38;5;2m╠>╔═══\x1b[0m   \x1b[38;5;2mprep    \x1b[0m   4       to        to        ADP     IN                            \n\x1b[38;5;2m║ ║ ╔>\x1b[0m   \x1b[38;5;2mcompound\x1b[0m   5       Silicon   silicon   PROPN   NNP   NounType=prop|N   GPE   \n\x1b[38;5;2m║ ╚>╚═\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m   6       Valley    valley    PROPN   NNP   NounType=prop|N   GPE   \n\x1b[38;5;2m╠══>╔═\x1b[0m   \x1b[38;5;2mprep    \x1b[0m   7       via       via       ADP     IN                            \n\x1b[38;5;2m║   ╚>\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m   8       London    london    PROPN   NNP   NounType=prop|N   GPE   \n\x1b[38;5;2m╚════>\x1b[0m   \x1b[38;5;2mpunct   \x1b[0m   9       .         .         PUNCT   .     PunctType=peri          \n\n"
    )

    # trigger value for value_dep shorter than maximum length in column
    formats = [
        AttributeFormat("tree_left", name="tree", aligns="r", fg_color=2),
        AttributeFormat("dep_", name="dep", fg_color=2),
        AttributeFormat("i", name="index", aligns="r"),
        AttributeFormat(
            "text",
            name="text",
            fg_color=196,
            value_dep_fg_colors={"'s": 50},
            value_dep_bg_colors={"'s": 12},
        ),
        AttributeFormat("lemma_", name="lemma"),
        AttributeFormat("pos_", name="pos", fg_color=100),
        AttributeFormat("tag_", name="tag", fg_color=100),
        AttributeFormat("morph", name="morph", fg_color=100, max_width=15),
        AttributeFormat(
            "ent_type_",
            name="ent",
        ),
    ]
    assert (
        render_table(fully_featured_doc_one_sentence, formats, spacing=3)
        == "\n\x1b[38;5;2m  tree\x1b[0m   \x1b[38;5;2mdep     \x1b[0m   index   \x1b[38;5;196mtext   \x1b[0m   lemma     \x1b[38;5;100mpos  \x1b[0m   \x1b[38;5;100mtag\x1b[0m   \x1b[38;5;100mmorph          \x1b[0m   ent   \n\x1b[38;5;2m------\x1b[0m   \x1b[38;5;2m--------\x1b[0m   -----   \x1b[38;5;196m-------\x1b[0m   -------   \x1b[38;5;100m-----\x1b[0m   \x1b[38;5;100m---\x1b[0m   \x1b[38;5;100m---------------\x1b[0m   ------\n\x1b[38;5;2m  ╔>╔═\x1b[0m   \x1b[38;5;2mposs    \x1b[0m   0       \x1b[38;5;196mSarah  \x1b[0m   sarah     \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   PERSON\n\x1b[38;5;2m  ║ ╚>\x1b[0m   \x1b[38;5;2mcase    \x1b[0m   1       \x1b[38;5;196m\x1b[38;5;50;48;5;12m's\x1b[0m     \x1b[0m   's        \x1b[38;5;100mPART \x1b[0m   \x1b[38;5;100mPOS\x1b[0m   \x1b[38;5;100mPoss=yes       \x1b[0m         \n\x1b[38;5;2m╔>╚═══\x1b[0m   \x1b[38;5;2mnsubj   \x1b[0m   2       \x1b[38;5;196msister \x1b[0m   sister    \x1b[38;5;100mNOUN \x1b[0m   \x1b[38;5;100mNN \x1b[0m   \x1b[38;5;100mNumber=sing    \x1b[0m         \n\x1b[38;5;2m╠═════\x1b[0m   \x1b[38;5;2mROOT    \x1b[0m   3       \x1b[38;5;196mflew   \x1b[0m   fly       \x1b[38;5;100mVERB \x1b[0m   \x1b[38;5;100mVBD\x1b[0m   \x1b[38;5;100mTense=past|Verb\x1b[0m         \n\x1b[38;5;2m╠>╔═══\x1b[0m   \x1b[38;5;2mprep    \x1b[0m   4       \x1b[38;5;196mto     \x1b[0m   to        \x1b[38;5;100mADP  \x1b[0m   \x1b[38;5;100mIN \x1b[0m   \x1b[38;5;100m               \x1b[0m         \n\x1b[38;5;2m║ ║ ╔>\x1b[0m   \x1b[38;5;2mcompound\x1b[0m   5       \x1b[38;5;196mSilicon\x1b[0m   silicon   \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   GPE   \n\x1b[38;5;2m║ ╚>╚═\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m   6       \x1b[38;5;196mValley \x1b[0m   valley    \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   GPE   \n\x1b[38;5;2m╠══>╔═\x1b[0m   \x1b[38;5;2mprep    \x1b[0m   7       \x1b[38;5;196mvia    \x1b[0m   via       \x1b[38;5;100mADP  \x1b[0m   \x1b[38;5;100mIN \x1b[0m   \x1b[38;5;100m               \x1b[0m         \n\x1b[38;5;2m║   ╚>\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m   8       \x1b[38;5;196mLondon \x1b[0m   london    \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   GPE   \n\x1b[38;5;2m╚════>\x1b[0m   \x1b[38;5;2mpunct   \x1b[0m   9       \x1b[38;5;196m.      \x1b[0m   .         \x1b[38;5;100mPUNCT\x1b[0m   \x1b[38;5;100m.  \x1b[0m   \x1b[38;5;100mPunctType=peri \x1b[0m         \n\n"
        if SUPPORTS_ANSI
        else "\n\x1b[38;5;2m  tree\x1b[0m   \x1b[38;5;2mdep     \x1b[0m   index   text      lemma     pos     tag   \x1b[38;5;100mmorph                    \x1b[0m   ent   \n\x1b[38;5;2m------\x1b[0m   \x1b[38;5;2m--------\x1b[0m   -----   -------   -------   -----   ---   \x1b[38;5;100m-------------------------\x1b[0m   ------\n\x1b[38;5;2m  ╔>╔═\x1b[0m   \x1b[38;5;2mposs    \x1b[0m   0       Sarah     sarah     PROPN   NNP   \x1b[38;5;100mNounType=prop|Number=sing\x1b[0m   PERSON\n\x1b[38;5;2m  ║ ╚>\x1b[0m   \x1b[38;5;2mcase    \x1b[0m   1       's        's        PART    POS   \x1b[38;5;100mPoss=yes                 \x1b[0m         \n\x1b[38;5;2m╔>╚═══\x1b[0m   \x1b[38;5;2mnsubj   \x1b[0m   2       sister    sister    NOUN    NN    \x1b[38;5;100mNumber=sing              \x1b[0m         \n\x1b[38;5;2m╠═════\x1b[0m   \x1b[38;5;2mROOT    \x1b[0m   3       flew      fly       VERB    VBD   \x1b[38;5;100mTense=past|VerbForm=fin  \x1b[0m         \n\x1b[38;5;2m╠>╔═══\x1b[0m   \x1b[38;5;2mprep    \x1b[0m   4       to        to        ADP     IN    \x1b[38;5;100m                         \x1b[0m         \n\x1b[38;5;2m║ ║ ╔>\x1b[0m   \x1b[38;5;2mcompound\x1b[0m   5       Silicon   silicon   PROPN   NNP   \x1b[38;5;100mNounType=prop|Number=sing\x1b[0m   GPE   \n\x1b[38;5;2m║ ╚>╚═\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m   6       Valley    valley    PROPN   NNP   \x1b[38;5;100mNounType=prop|Number=sing\x1b[0m   GPE   \n\x1b[38;5;2m╠══>╔═\x1b[0m   \x1b[38;5;2mprep    \x1b[0m   7       via       via       ADP     IN    \x1b[38;5;100m                         \x1b[0m         \n\x1b[38;5;2m║   ╚>\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m   8       London    london    PROPN   NNP   \x1b[38;5;100mNounType=prop|Number=sing\x1b[0m   GPE   \n\x1b[38;5;2m╚════>\x1b[0m   \x1b[38;5;2mpunct   \x1b[0m   9       .         .         PUNCT   .     \x1b[38;5;100mPunctType=peri           \x1b[0m         \n\n"
    )


def test_viz_rich_render_table_two_sentences(
    fully_featured_doc_two_sentences,
):
    formats = [
        AttributeFormat("tree_left", name="tree", aligns="r", fg_color=2),
        AttributeFormat("dep_", name="dep", fg_color=2),
        AttributeFormat("i", name="index", aligns="r"),
        AttributeFormat("text", name="text"),
        AttributeFormat("lemma_", name="lemma"),
        AttributeFormat("pos_", name="pos", fg_color=100),
        AttributeFormat("tag_", name="tag", fg_color=100),
        AttributeFormat("morph", name="morph", fg_color=100, max_width=15),
        AttributeFormat(
            "ent_type_",
            name="ent",
            fg_color=196,
            value_dep_fg_colors={"PERSON": 50},
            value_dep_bg_colors={"PERSON": 12},
        ),
    ]
    print(render_table(fully_featured_doc_two_sentences, formats, spacing=3))
    print(repr(render_table(fully_featured_doc_two_sentences, formats, spacing=3)))
    target = (
        "\n\x1b[38;5;2m  tree\x1b[0m   \x1b[38;5;2mdep     \x1b[0m   index   text      lemma     \x1b[38;5;100mpos  \x1b[0m   \x1b[38;5;100mtag\x1b[0m   \x1b[38;5;100mmorph          \x1b[0m   \x1b[38;5;196ment   \x1b[0m\n\x1b[38;5;2m------\x1b[0m   \x1b[38;5;2m--------\x1b[0m   -----   -------   -------   \x1b[38;5;100m-----\x1b[0m   \x1b[38;5;100m---\x1b[0m   \x1b[38;5;100m---------------\x1b[0m   \x1b[38;5;196m------\x1b[0m\n\x1b[38;5;2m  ╔>╔═\x1b[0m   \x1b[38;5;2mposs    \x1b[0m   0       Sarah     sarah     \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196m\x1b[38;5;50;48;5;12mPERSON\x1b[0m\x1b[0m\n\x1b[38;5;2m  ║ ╚>\x1b[0m   \x1b[38;5;2mcase    \x1b[0m   1       's        's        \x1b[38;5;100mPART \x1b[0m   \x1b[38;5;100mPOS\x1b[0m   \x1b[38;5;100mPoss=yes       \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╔>╚═══\x1b[0m   \x1b[38;5;2mnsubj   \x1b[0m   2       sister    sister    \x1b[38;5;100mNOUN \x1b[0m   \x1b[38;5;100mNN \x1b[0m   \x1b[38;5;100mNumber=sing    \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╠═════\x1b[0m   \x1b[38;5;2mROOT    \x1b[0m   3       flew      fly       \x1b[38;5;100mVERB \x1b[0m   \x1b[38;5;100mVBD\x1b[0m   \x1b[38;5;100mTense=past|Verb\x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╠>╔═══\x1b[0m   \x1b[38;5;2mprep    \x1b[0m   4       to        to        \x1b[38;5;100mADP  \x1b[0m   \x1b[38;5;100mIN \x1b[0m   \x1b[38;5;100m               \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m║ ║ ╔>\x1b[0m   \x1b[38;5;2mcompound\x1b[0m   5       Silicon   silicon   \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m║ ╚>╚═\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m   6       Valley    valley    \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m╠══>╔═\x1b[0m   \x1b[38;5;2mprep    \x1b[0m   7       via       via       \x1b[38;5;100mADP  \x1b[0m   \x1b[38;5;100mIN \x1b[0m   \x1b[38;5;100m               \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m║   ╚>\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m   8       London    london    \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m╚════>\x1b[0m   \x1b[38;5;2mpunct   \x1b[0m   9       .         .         \x1b[38;5;100mPUNCT\x1b[0m   \x1b[38;5;100m.  \x1b[0m   \x1b[38;5;100mPunctType=peri \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\n\n\x1b[38;5;2mtree\x1b[0m   \x1b[38;5;2mdep  \x1b[0m   index   text    lemma   \x1b[38;5;100mpos  \x1b[0m   \x1b[38;5;100mtag\x1b[0m   \x1b[38;5;100mmorph          \x1b[0m   \x1b[38;5;196ment\x1b[0m\n\x1b[38;5;2m----\x1b[0m   \x1b[38;5;2m-----\x1b[0m   -----   -----   -----   \x1b[38;5;100m-----\x1b[0m   \x1b[38;5;100m---\x1b[0m   \x1b[38;5;100m---------------\x1b[0m   \x1b[38;5;196m---\x1b[0m\n\x1b[38;5;2m  ╔>\x1b[0m   \x1b[38;5;2mnsubj\x1b[0m   10      She     she     \x1b[38;5;100mPRON \x1b[0m   \x1b[38;5;100mPRP\x1b[0m   \x1b[38;5;100mCase=Nom|Gender\x1b[0m   \x1b[38;5;196m   \x1b[0m\n\x1b[38;5;2m  ╠═\x1b[0m   \x1b[38;5;2mROOT \x1b[0m   11      loved   love    \x1b[38;5;100mVERB \x1b[0m   \x1b[38;5;100mVBD\x1b[0m   \x1b[38;5;100mTense=Past|Verb\x1b[0m   \x1b[38;5;196m   \x1b[0m\n\x1b[38;5;2m  ╠>\x1b[0m   \x1b[38;5;2mdobj \x1b[0m   12      it      it      \x1b[38;5;100mPRON \x1b[0m   \x1b[38;5;100mPRP\x1b[0m   \x1b[38;5;100mCase=Acc|Gender\x1b[0m   \x1b[38;5;196m   \x1b[0m\n\x1b[38;5;2m  ╚>\x1b[0m   \x1b[38;5;2mpunct\x1b[0m   13      .       .       \x1b[38;5;100mPUNCT\x1b[0m   \x1b[38;5;100m.  \x1b[0m   \x1b[38;5;100mPunctType=peri \x1b[0m   \x1b[38;5;196m   \x1b[0m\n\n"
        if SUPPORTS_ANSI
        else "\n  tree   dep        index   text      lemma     pos     tag   morph             ent   \n------   --------   -----   -------   -------   -----   ---   ---------------   ------\n  ╔>╔═   poss       0       Sarah     sarah     PROPN   NNP   NounType=prop|N   PERSON\n  ║ ╚>   case       1       's        's        PART    POS   Poss=yes                \n╔>╚═══   nsubj      2       sister    sister    NOUN    NN    Number=sing             \n╠═════   ROOT       3       flew      fly       VERB    VBD   Tense=past|Verb         \n╠>╔═══   prep       4       to        to        ADP     IN                            \n║ ║ ╔>   compound   5       Silicon   silicon   PROPN   NNP   NounType=prop|N   GPE   \n║ ╚>╚═   pobj       6       Valley    valley    PROPN   NNP   NounType=prop|N   GPE   \n╠══>╔═   prep       7       via       via       ADP     IN                            \n║   ╚>   pobj       8       London    london    PROPN   NNP   NounType=prop|N   GPE   \n╚════>   punct      9       .         .         PUNCT   .     PunctType=peri          \n\n\ntree   dep     index   text    lemma   pos     tag   morph             ent\n----   -----   -----   -----   -----   -----   ---   ---------------   ---\n  ╔>   nsubj   10      She     she     PRON    PRP   Case=Nom|Gender      \n  ╠═   ROOT    11      loved   love    VERB    VBD   Tense=Past|Verb      \n  ╠>   dobj    12      it      it      PRON    PRP   Case=Acc|Gender      \n  ╚>   punct   13      .       .       PUNCT   .     PunctType=peri       \n\n"
    )
    assert render_table(fully_featured_doc_two_sentences, formats, spacing=3) == target
    assert (
        render_table(
            fully_featured_doc_two_sentences, formats, spacing=3, start_i=3, length=300
        )
        == target
    )
    assert (
        render_table(
            fully_featured_doc_two_sentences, formats, spacing=3, start_i=3, length=9
        )
        == target
    )


def test_viz_rich_render_table_start(
    fully_featured_doc_two_sentences,
):
    formats = [
        AttributeFormat("tree_left", name="tree", aligns="r", fg_color=2),
        AttributeFormat("dep_", name="dep", fg_color=2),
        AttributeFormat("i", name="index", aligns="r"),
        AttributeFormat("text", name="text"),
        AttributeFormat("lemma_", name="lemma"),
        AttributeFormat("pos_", name="pos", fg_color=100),
        AttributeFormat("tag_", name="tag", fg_color=100),
        AttributeFormat("morph", name="morph", fg_color=100, max_width=15),
        AttributeFormat(
            "ent_type_",
            name="ent",
            fg_color=196,
            value_dep_fg_colors={"PERSON": 50},
            value_dep_bg_colors={"PERSON": 12},
        ),
    ]
    print(
        render_table(fully_featured_doc_two_sentences, formats, spacing=3, start_i=11)
    )
    print(
        repr(
            render_table(
                fully_featured_doc_two_sentences, formats, spacing=3, start_i=11
            )
        )
    )
    target = (
        "\n\x1b[38;5;2mtree\x1b[0m   \x1b[38;5;2mdep  \x1b[0m   index   text    lemma   \x1b[38;5;100mpos  \x1b[0m   \x1b[38;5;100mtag\x1b[0m   \x1b[38;5;100mmorph          \x1b[0m   \x1b[38;5;196ment\x1b[0m\n\x1b[38;5;2m----\x1b[0m   \x1b[38;5;2m-----\x1b[0m   -----   -----   -----   \x1b[38;5;100m-----\x1b[0m   \x1b[38;5;100m---\x1b[0m   \x1b[38;5;100m---------------\x1b[0m   \x1b[38;5;196m---\x1b[0m\n\x1b[38;5;2m  ╔>\x1b[0m   \x1b[38;5;2mnsubj\x1b[0m   10      She     she     \x1b[38;5;100mPRON \x1b[0m   \x1b[38;5;100mPRP\x1b[0m   \x1b[38;5;100mCase=Nom|Gender\x1b[0m   \x1b[38;5;196m   \x1b[0m\n\x1b[38;5;2m  ╠═\x1b[0m   \x1b[38;5;2mROOT \x1b[0m   11      loved   love    \x1b[38;5;100mVERB \x1b[0m   \x1b[38;5;100mVBD\x1b[0m   \x1b[38;5;100mTense=Past|Verb\x1b[0m   \x1b[38;5;196m   \x1b[0m\n\x1b[38;5;2m  ╠>\x1b[0m   \x1b[38;5;2mdobj \x1b[0m   12      it      it      \x1b[38;5;100mPRON \x1b[0m   \x1b[38;5;100mPRP\x1b[0m   \x1b[38;5;100mCase=Acc|Gender\x1b[0m   \x1b[38;5;196m   \x1b[0m\n\x1b[38;5;2m  ╚>\x1b[0m   \x1b[38;5;2mpunct\x1b[0m   13      .       .       \x1b[38;5;100mPUNCT\x1b[0m   \x1b[38;5;100m.  \x1b[0m   \x1b[38;5;100mPunctType=peri \x1b[0m   \x1b[38;5;196m   \x1b[0m\n\n"
        if SUPPORTS_ANSI
        else "\ntree   dep     index   text    lemma   pos     tag   morph             ent\n----   -----   -----   -----   -----   -----   ---   ---------------   ---\n  ╔>   nsubj   10      She     she     PRON    PRP   Case=Nom|Gender      \n  ╠═   ROOT    11      loved   love    VERB    VBD   Tense=Past|Verb      \n  ╠>   dobj    12      it      it      PRON    PRP   Case=Acc|Gender      \n  ╚>   punct   13      .       .       PUNCT   .     PunctType=peri       \n\n"
    )
    assert (
        render_table(fully_featured_doc_two_sentences, formats, spacing=3, start_i=11)
        == target
    )
    assert (
        render_table(
            fully_featured_doc_two_sentences,
            formats,
            spacing=3,
            start_i=11,
            search_attr_name="pos",
            search_attr_value="VERB",
        )
        == target
    )
    assert (
        render_table(
            fully_featured_doc_two_sentences,
            formats,
            spacing=3,
            start_i=2,
            search_attr_name="lemma",
            search_attr_value="love",
        )
        == target
    )
    assert (
        render_table(
            fully_featured_doc_two_sentences,
            formats,
            spacing=3,
            search_attr_name="lemma",
            search_attr_value="love",
        )
        == target
    )
    assert (
        render_table(
            fully_featured_doc_two_sentences,
            formats,
            spacing=3,
            start_i=2,
            length=3,
            search_attr_name="lemma",
            search_attr_value="love",
        )
        == target
    )
    assert (
        render_table(
            fully_featured_doc_two_sentences,
            formats,
            spacing=3,
            search_attr_name="lemma_",
            search_attr_value="love",
        )
        == target
    )
    assert (
        render_table(
            fully_featured_doc_two_sentences,
            formats,
            spacing=3,
            search_attr_name="lemma",
            search_attr_value="lovef",
        )
        == ""
    )
    assert (
        render_table(
            fully_featured_doc_two_sentences,
            formats,
            spacing=3,
            search_attr_name="lemma_",
            search_attr_value="lovef",
        )
        == ""
    )
    assert (
        render_table(
            fully_featured_doc_two_sentences,
            formats,
            spacing=3,
            search_attr_name="lemmaa",
            search_attr_value="love",
        )
        == ""
    )
    assert (
        render_table(
            fully_featured_doc_two_sentences,
            formats,
            spacing=3,
            start_i=50,
            search_attr_name="lemma",
            search_attr_value="love",
        )
        == ""
    )


def test_viz_rich_render_table_end(
    fully_featured_doc_two_sentences,
):
    formats = [
        AttributeFormat("tree_left", name="tree", aligns="r", fg_color=2),
        AttributeFormat("dep_", name="dep", fg_color=2),
        AttributeFormat("i", name="index", aligns="r"),
        AttributeFormat("text", name="text"),
        AttributeFormat("lemma_", name="lemma"),
        AttributeFormat("pos_", name="pos", fg_color=100),
        AttributeFormat("tag_", name="tag", fg_color=100),
        AttributeFormat("morph", name="morph", fg_color=100, max_width=15),
        AttributeFormat(
            "ent_type_",
            name="ent",
            fg_color=196,
            value_dep_fg_colors={"PERSON": 50},
            value_dep_bg_colors={"PERSON": 12},
        ),
    ]
    target = (
        "\n\x1b[38;5;2m  tree\x1b[0m   \x1b[38;5;2mdep     \x1b[0m   index   text      lemma     \x1b[38;5;100mpos  \x1b[0m   \x1b[38;5;100mtag\x1b[0m   \x1b[38;5;100mmorph          \x1b[0m   \x1b[38;5;196ment   \x1b[0m\n\x1b[38;5;2m------\x1b[0m   \x1b[38;5;2m--------\x1b[0m   -----   -------   -------   \x1b[38;5;100m-----\x1b[0m   \x1b[38;5;100m---\x1b[0m   \x1b[38;5;100m---------------\x1b[0m   \x1b[38;5;196m------\x1b[0m\n\x1b[38;5;2m  ╔>╔═\x1b[0m   \x1b[38;5;2mposs    \x1b[0m   0       Sarah     sarah     \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196m\x1b[38;5;50;48;5;12mPERSON\x1b[0m\x1b[0m\n\x1b[38;5;2m  ║ ╚>\x1b[0m   \x1b[38;5;2mcase    \x1b[0m   1       's        's        \x1b[38;5;100mPART \x1b[0m   \x1b[38;5;100mPOS\x1b[0m   \x1b[38;5;100mPoss=yes       \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╔>╚═══\x1b[0m   \x1b[38;5;2mnsubj   \x1b[0m   2       sister    sister    \x1b[38;5;100mNOUN \x1b[0m   \x1b[38;5;100mNN \x1b[0m   \x1b[38;5;100mNumber=sing    \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╠═════\x1b[0m   \x1b[38;5;2mROOT    \x1b[0m   3       flew      fly       \x1b[38;5;100mVERB \x1b[0m   \x1b[38;5;100mVBD\x1b[0m   \x1b[38;5;100mTense=past|Verb\x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╠>╔═══\x1b[0m   \x1b[38;5;2mprep    \x1b[0m   4       to        to        \x1b[38;5;100mADP  \x1b[0m   \x1b[38;5;100mIN \x1b[0m   \x1b[38;5;100m               \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m║ ║ ╔>\x1b[0m   \x1b[38;5;2mcompound\x1b[0m   5       Silicon   silicon   \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m║ ╚>╚═\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m   6       Valley    valley    \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m╠══>╔═\x1b[0m   \x1b[38;5;2mprep    \x1b[0m   7       via       via       \x1b[38;5;100mADP  \x1b[0m   \x1b[38;5;100mIN \x1b[0m   \x1b[38;5;100m               \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m║   ╚>\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m   8       London    london    \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m╚════>\x1b[0m   \x1b[38;5;2mpunct   \x1b[0m   9       .         .         \x1b[38;5;100mPUNCT\x1b[0m   \x1b[38;5;100m.  \x1b[0m   \x1b[38;5;100mPunctType=peri \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\n"
        if SUPPORTS_ANSI
        else "\n  tree   dep        index   text      lemma     pos     tag   morph             ent   \n------   --------   -----   -------   -------   -----   ---   ---------------   ------\n  ╔>╔═   poss       0       Sarah     sarah     PROPN   NNP   NounType=prop|N   PERSON\n  ║ ╚>   case       1       's        's        PART    POS   Poss=yes                \n╔>╚═══   nsubj      2       sister    sister    NOUN    NN    Number=sing             \n╠═════   ROOT       3       flew      fly       VERB    VBD   Tense=past|Verb         \n╠>╔═══   prep       4       to        to        ADP     IN                            \n║ ║ ╔>   compound   5       Silicon   silicon   PROPN   NNP   NounType=prop|N   GPE   \n║ ╚>╚═   pobj       6       Valley    valley    PROPN   NNP   NounType=prop|N   GPE   \n╠══>╔═   prep       7       via       via       ADP     IN                            \n║   ╚>   pobj       8       London    london    PROPN   NNP   NounType=prop|N   GPE   \n╚════>   punct      9       .         .         PUNCT   .     PunctType=peri          \n\n"
    )

    assert (
        render_table(fully_featured_doc_two_sentences, formats, spacing=3, start_i=2)
        == target
    )
    assert (
        render_table(
            fully_featured_doc_two_sentences, formats, spacing=3, start_i=2, length=3
        )
        == target
    )
    assert (
        render_table(fully_featured_doc_two_sentences, formats, spacing=3, length=3)
        == target
    )
    assert (
        render_table(
            fully_featured_doc_two_sentences,
            formats,
            spacing=3,
            search_attr_name="pos",
            search_attr_value="VERB",
        )
        == target
    )
