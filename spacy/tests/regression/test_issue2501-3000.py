import pytest
from spacy import displacy
from spacy.training import Example
from spacy.lang.en import English
from spacy.lang.ja import Japanese
from spacy.lang.xx import MultiLanguage
from spacy.language import Language
from spacy.matcher import Matcher
from spacy.tokens import Doc, Span
from spacy.vocab import Vocab
from spacy.compat import pickle
import numpy
import random


def test_issue2564():
    """Test the tagger sets has_annotation("TAG") correctly when used via Language.pipe."""
    nlp = Language()
    tagger = nlp.add_pipe("tagger")
    tagger.add_label("A")
    nlp.initialize()
    doc = nlp("hello world")
    assert doc.has_annotation("TAG")
    docs = nlp.pipe(["hello", "world"])
    piped_doc = next(docs)
    assert piped_doc.has_annotation("TAG")


def test_issue2569(en_tokenizer):
    """Test that operator + is greedy."""
    doc = en_tokenizer("It is May 15, 1993.")
    doc.ents = [Span(doc, 2, 6, label=doc.vocab.strings["DATE"])]
    matcher = Matcher(doc.vocab)
    matcher.add("RULE", [[{"ENT_TYPE": "DATE", "OP": "+"}]])
    matched = [doc[start:end] for _, start, end in matcher(doc)]
    matched = sorted(matched, key=len, reverse=True)
    assert len(matched) == 10
    assert len(matched[0]) == 4
    assert matched[0].text == "May 15, 1993"


@pytest.mark.parametrize(
    "text",
    [
        "ABLEItemColumn IAcceptance Limits of ErrorIn-Service Limits of ErrorColumn IIColumn IIIColumn IVColumn VComputed VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeCubic FeetCubic FeetCubic FeetCubic FeetCubic Feet1Up to 10.0100.0050.0100.005220.0200.0100.0200.010350.0360.0180.0360.0184100.0500.0250.0500.0255Over 100.5% of computed volume0.25% of computed volume0.5% of computed volume0.25% of computed volume TABLE ItemColumn IAcceptance Limits of ErrorIn-Service Limits of ErrorColumn IIColumn IIIColumn IVColumn VComputed VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeCubic FeetCubic FeetCubic FeetCubic FeetCubic Feet1Up to 10.0100.0050.0100.005220.0200.0100.0200.010350.0360.0180.0360.0184100.0500.0250.0500.0255Over 100.5% of computed volume0.25% of computed volume0.5% of computed volume0.25% of computed volume ItemColumn IAcceptance Limits of ErrorIn-Service Limits of ErrorColumn IIColumn IIIColumn IVColumn VComputed VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeCubic FeetCubic FeetCubic FeetCubic FeetCubic Feet1Up to 10.0100.0050.0100.005220.0200.0100.0200.010350.0360.0180.0360.0184100.0500.0250.0500.0255Over 100.5% of computed volume0.25% of computed volume0.5% of computed volume0.25% of computed volume",
        "oow.jspsearch.eventoracleopenworldsearch.technologyoraclesolarissearch.technologystoragesearch.technologylinuxsearch.technologyserverssearch.technologyvirtualizationsearch.technologyengineeredsystemspcodewwmkmppscem:",
    ],
)
def test_issue2626_2835(en_tokenizer, text):
    """Check that sentence doesn't cause an infinite loop in the tokenizer."""
    doc = en_tokenizer(text)
    assert doc


def test_issue2656(en_tokenizer):
    """Test that tokenizer correctly splits off punctuation after numbers with
    decimal points.
    """
    doc = en_tokenizer("I went for 40.3, and got home by 10.0.")
    assert len(doc) == 11
    assert doc[0].text == "I"
    assert doc[1].text == "went"
    assert doc[2].text == "for"
    assert doc[3].text == "40.3"
    assert doc[4].text == ","
    assert doc[5].text == "and"
    assert doc[6].text == "got"
    assert doc[7].text == "home"
    assert doc[8].text == "by"
    assert doc[9].text == "10.0"
    assert doc[10].text == "."


def test_issue2671():
    """Ensure the correct entity ID is returned for matches with quantifiers.
    See also #2675
    """
    nlp = English()
    matcher = Matcher(nlp.vocab)
    pattern_id = "test_pattern"
    pattern = [
        {"LOWER": "high"},
        {"IS_PUNCT": True, "OP": "?"},
        {"LOWER": "adrenaline"},
    ]
    matcher.add(pattern_id, [pattern])
    doc1 = nlp("This is a high-adrenaline situation.")
    doc2 = nlp("This is a high adrenaline situation.")
    matches1 = matcher(doc1)
    for match_id, start, end in matches1:
        assert nlp.vocab.strings[match_id] == pattern_id
    matches2 = matcher(doc2)
    for match_id, start, end in matches2:
        assert nlp.vocab.strings[match_id] == pattern_id


def test_issue2728(en_vocab):
    """Test that displaCy ENT visualizer escapes HTML correctly."""
    doc = Doc(en_vocab, words=["test", "<RELEASE>", "test"])
    doc.ents = [Span(doc, 0, 1, label="TEST")]
    html = displacy.render(doc, style="ent")
    assert "&lt;RELEASE&gt;" in html
    doc.ents = [Span(doc, 1, 2, label="TEST")]
    html = displacy.render(doc, style="ent")
    assert "&lt;RELEASE&gt;" in html


def test_issue2754(en_tokenizer):
    """Test that words like 'a' and 'a.m.' don't get exceptional norm values."""
    a = en_tokenizer("a")
    assert a[0].norm_ == "a"
    am = en_tokenizer("am")
    assert am[0].norm_ == "am"


def test_issue2772(en_vocab):
    """Test that deprojectivization doesn't mess up sentence boundaries."""
    # fmt: off
    words = ["When", "we", "write", "or", "communicate", "virtually", ",", "we", "can", "hide", "our", "true", "feelings", "."]
    # fmt: on
    # A tree with a non-projective (i.e. crossing) arc
    # The arcs (0, 4) and (2, 9) cross.
    heads = [4, 2, 9, 2, 2, 4, 9, 9, 9, 9, 12, 12, 9, 9]
    deps = ["dep"] * len(heads)
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    assert doc[1].is_sent_start is False


@pytest.mark.parametrize("text", ["-0.23", "+123,456", "±1"])
@pytest.mark.parametrize("lang_cls", [English, MultiLanguage])
def test_issue2782(text, lang_cls):
    """Check that like_num handles + and - before number."""
    nlp = lang_cls()
    doc = nlp(text)
    assert len(doc) == 1
    assert doc[0].like_num


def test_issue2800():
    """Test issue that arises when too many labels are added to NER model.
    Used to cause segfault.
    """
    nlp = English()
    train_data = []
    train_data.extend(
        [Example.from_dict(nlp.make_doc("One sentence"), {"entities": []})]
    )
    entity_types = [str(i) for i in range(1000)]
    ner = nlp.add_pipe("ner")
    for entity_type in list(entity_types):
        ner.add_label(entity_type)
    optimizer = nlp.initialize()
    for i in range(20):
        losses = {}
        random.shuffle(train_data)
        for example in train_data:
            nlp.update([example], sgd=optimizer, losses=losses, drop=0.5)


def test_issue2822(it_tokenizer):
    """Test that the abbreviation of poco is kept as one word."""
    doc = it_tokenizer("Vuoi un po' di zucchero?")
    assert len(doc) == 6
    assert doc[0].text == "Vuoi"
    assert doc[1].text == "un"
    assert doc[2].text == "po'"
    assert doc[3].text == "di"
    assert doc[4].text == "zucchero"
    assert doc[5].text == "?"


def test_issue2833(en_vocab):
    """Test that a custom error is raised if a token or span is pickled."""
    doc = Doc(en_vocab, words=["Hello", "world"])
    with pytest.raises(NotImplementedError):
        pickle.dumps(doc[0])
    with pytest.raises(NotImplementedError):
        pickle.dumps(doc[0:2])


def test_issue2871():
    """Test that vectors recover the correct key for spaCy reserved words."""
    words = ["dog", "cat", "SUFFIX"]
    vocab = Vocab(vectors_name="test_issue2871")
    vocab.vectors.resize(shape=(3, 10))
    vector_data = numpy.zeros((3, 10), dtype="f")
    for word in words:
        _ = vocab[word]  # noqa: F841
        vocab.set_vector(word, vector_data[0])
    vocab.vectors.name = "dummy_vectors"
    assert vocab["dog"].rank == 0
    assert vocab["cat"].rank == 1
    assert vocab["SUFFIX"].rank == 2
    assert vocab.vectors.find(key="dog") == 0
    assert vocab.vectors.find(key="cat") == 1
    assert vocab.vectors.find(key="SUFFIX") == 2


def test_issue2901():
    """Test that `nlp` doesn't fail."""
    try:
        nlp = Japanese()
    except ImportError:
        pytest.skip()

    doc = nlp("pythonが大好きです")
    assert doc


def test_issue2926(fr_tokenizer):
    """Test that the tokenizer correctly splits tokens separated by a slash (/)
    ending in a digit.
    """
    doc = fr_tokenizer("Learn html5/css3/javascript/jquery")
    assert len(doc) == 8
    assert doc[0].text == "Learn"
    assert doc[1].text == "html5"
    assert doc[2].text == "/"
    assert doc[3].text == "css3"
    assert doc[4].text == "/"
    assert doc[5].text == "javascript"
    assert doc[6].text == "/"
    assert doc[7].text == "jquery"
