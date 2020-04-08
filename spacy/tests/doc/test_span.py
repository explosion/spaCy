# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.attrs import ORTH, LENGTH
from spacy.tokens import Doc, Span
from spacy.vocab import Vocab
from spacy.errors import ModelsWarning
from spacy.util import filter_spans

from ..util import get_doc


@pytest.fixture
def doc(en_tokenizer):
    # fmt: off
    text = "This is a sentence. This is another sentence. And a third."
    heads = [1, 0, 1, -2, -3, 1, 0, 1, -2, -3, 0, 1, -2, -1]
    deps = ["nsubj", "ROOT", "det", "attr", "punct", "nsubj", "ROOT", "det",
            "attr", "punct", "ROOT", "det", "npadvmod", "punct"]
    # fmt: on
    tokens = en_tokenizer(text)
    return get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads, deps=deps)


@pytest.fixture
def doc_not_parsed(en_tokenizer):
    text = "This is a sentence. This is another sentence. And a third."
    tokens = en_tokenizer(text)
    doc = Doc(tokens.vocab, words=[t.text for t in tokens])
    doc.is_parsed = False
    return doc


@pytest.mark.parametrize(
    "i_sent,i,j,text",
    [
        (0, 0, len("This is a"), "This is a"),
        (1, 0, len("This is another"), "This is another"),
        (2, len("And "), len("And ") + len("a third"), "a third"),
        (0, 1, 2, None),
    ],
)
def test_char_span(doc, i_sent, i, j, text):
    sents = list(doc.sents)
    span = sents[i_sent].char_span(i, j)
    if not text:
        assert not span
    else:
        assert span.text == text


def test_spans_sent_spans(doc):
    sents = list(doc.sents)
    assert sents[0].start == 0
    assert sents[0].end == 5
    assert len(sents) == 3
    assert sum(len(sent) for sent in sents) == len(doc)


def test_spans_root(doc):
    span = doc[2:4]
    assert len(span) == 2
    assert span.text == "a sentence"
    assert span.root.text == "sentence"
    assert span.root.head.text == "is"


def test_spans_string_fn(doc):
    span = doc[0:4]
    assert len(span) == 4
    assert span.text == "This is a sentence"
    assert span.upper_ == "THIS IS A SENTENCE"
    assert span.lower_ == "this is a sentence"


def test_spans_root2(en_tokenizer):
    text = "through North and South Carolina"
    heads = [0, 3, -1, -2, -4]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads)
    assert doc[-2:].root.text == "Carolina"


def test_spans_span_sent(doc, doc_not_parsed):
    """Test span.sent property"""
    assert len(list(doc.sents))
    assert doc[:2].sent.root.text == "is"
    assert doc[:2].sent.text == "This is a sentence ."
    assert doc[6:7].sent.root.left_edge.text == "This"
    # test on manual sbd
    doc_not_parsed[0].is_sent_start = True
    doc_not_parsed[5].is_sent_start = True
    assert doc_not_parsed[1:3].sent == doc_not_parsed[0:5]
    assert doc_not_parsed[10:14].sent == doc_not_parsed[5:]


def test_spans_lca_matrix(en_tokenizer):
    """Test span's lca matrix generation"""
    tokens = en_tokenizer("the lazy dog slept")
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=[2, 1, 1, 0])
    lca = doc[:2].get_lca_matrix()
    assert lca.shape == (2, 2)
    assert lca[0, 0] == 0  # the & the -> the
    assert lca[0, 1] == -1  # the & lazy -> dog (out of span)
    assert lca[1, 0] == -1  # lazy & the -> dog (out of span)
    assert lca[1, 1] == 1  # lazy & lazy -> lazy

    lca = doc[1:].get_lca_matrix()
    assert lca.shape == (3, 3)
    assert lca[0, 0] == 0  # lazy & lazy -> lazy
    assert lca[0, 1] == 1  # lazy & dog -> dog
    assert lca[0, 2] == 2  # lazy & slept -> slept

    lca = doc[2:].get_lca_matrix()
    assert lca.shape == (2, 2)
    assert lca[0, 0] == 0  # dog & dog -> dog
    assert lca[0, 1] == 1  # dog & slept -> slept
    assert lca[1, 0] == 1  # slept & dog -> slept
    assert lca[1, 1] == 1  # slept & slept -> slept


def test_span_similarity_match():
    doc = Doc(Vocab(), words=["a", "b", "a", "b"])
    span1 = doc[:2]
    span2 = doc[2:]
    with pytest.warns(ModelsWarning):
        assert span1.similarity(span2) == 1.0
        assert span1.similarity(doc) == 0.0
        assert span1[:1].similarity(doc.vocab["a"]) == 1.0


def test_spans_default_sentiment(en_tokenizer):
    """Test span.sentiment property's default averaging behaviour"""
    text = "good stuff bad stuff"
    tokens = en_tokenizer(text)
    tokens.vocab[tokens[0].text].sentiment = 3.0
    tokens.vocab[tokens[2].text].sentiment = -2.0
    doc = Doc(tokens.vocab, words=[t.text for t in tokens])
    assert doc[:2].sentiment == 3.0 / 2
    assert doc[-2:].sentiment == -2.0 / 2
    assert doc[:-1].sentiment == (3.0 + -2) / 3.0


def test_spans_override_sentiment(en_tokenizer):
    """Test span.sentiment property's default averaging behaviour"""
    text = "good stuff bad stuff"
    tokens = en_tokenizer(text)
    tokens.vocab[tokens[0].text].sentiment = 3.0
    tokens.vocab[tokens[2].text].sentiment = -2.0
    doc = Doc(tokens.vocab, words=[t.text for t in tokens])
    doc.user_span_hooks["sentiment"] = lambda span: 10.0
    assert doc[:2].sentiment == 10.0
    assert doc[-2:].sentiment == 10.0
    assert doc[:-1].sentiment == 10.0


def test_spans_are_hashable(en_tokenizer):
    """Test spans can be hashed."""
    text = "good stuff bad stuff"
    tokens = en_tokenizer(text)
    span1 = tokens[:2]
    span2 = tokens[2:4]
    assert hash(span1) != hash(span2)
    span3 = tokens[0:2]
    assert hash(span3) == hash(span1)


def test_spans_by_character(doc):
    span1 = doc[1:-2]
    span2 = doc.char_span(span1.start_char, span1.end_char, label="GPE")
    assert span1.start_char == span2.start_char
    assert span1.end_char == span2.end_char
    assert span2.label_ == "GPE"


def test_span_to_array(doc):
    span = doc[1:-2]
    arr = span.to_array([ORTH, LENGTH])
    assert arr.shape == (len(span), 2)
    assert arr[0, 0] == span[0].orth
    assert arr[0, 1] == len(span[0])


def test_span_as_doc(doc):
    span = doc[4:10]
    span_doc = span.as_doc()
    assert span.text == span_doc.text.strip()
    assert isinstance(span_doc, doc.__class__)
    assert span_doc is not doc
    assert span_doc[0].idx == 0


def test_span_as_doc_user_data(doc):
    """Test that the user_data can be preserved (but not by default). """
    my_key = "my_info"
    my_value = 342
    doc.user_data[my_key] = my_value

    span = doc[4:10]
    span_doc_with = span.as_doc(copy_user_data=True)
    span_doc_without = span.as_doc()

    assert doc.user_data.get(my_key, None) is my_value
    assert span_doc_with.user_data.get(my_key, None) is my_value
    assert span_doc_without.user_data.get(my_key, None) is None


def test_span_string_label_kb_id(doc):
    span = Span(doc, 0, 1, label="hello", kb_id="Q342")
    assert span.label_ == "hello"
    assert span.label == doc.vocab.strings["hello"]
    assert span.kb_id_ == "Q342"
    assert span.kb_id == doc.vocab.strings["Q342"]


def test_span_label_readonly(doc):
    span = Span(doc, 0, 1)
    with pytest.raises(NotImplementedError):
        span.label_ = "hello"


def test_span_kb_id_readonly(doc):
    span = Span(doc, 0, 1)
    with pytest.raises(NotImplementedError):
        span.kb_id_ = "Q342"


def test_span_ents_property(doc):
    """Test span.ents for the """
    doc.ents = [
        (doc.vocab.strings["PRODUCT"], 0, 1),
        (doc.vocab.strings["PRODUCT"], 7, 8),
        (doc.vocab.strings["PRODUCT"], 11, 14),
    ]
    assert len(list(doc.ents)) == 3
    sentences = list(doc.sents)
    assert len(sentences) == 3
    assert len(sentences[0].ents) == 1
    # First sentence, also tests start of sentence
    assert sentences[0].ents[0].text == "This"
    assert sentences[0].ents[0].label_ == "PRODUCT"
    assert sentences[0].ents[0].start == 0
    assert sentences[0].ents[0].end == 1
    # Second sentence
    assert len(sentences[1].ents) == 1
    assert sentences[1].ents[0].text == "another"
    assert sentences[1].ents[0].label_ == "PRODUCT"
    assert sentences[1].ents[0].start == 7
    assert sentences[1].ents[0].end == 8
    # Third sentence ents, Also tests end of sentence
    assert sentences[2].ents[0].text == "a third ."
    assert sentences[2].ents[0].label_ == "PRODUCT"
    assert sentences[2].ents[0].start == 11
    assert sentences[2].ents[0].end == 14


def test_filter_spans(doc):
    # Test filtering duplicates
    spans = [doc[1:4], doc[6:8], doc[1:4], doc[10:14]]
    filtered = filter_spans(spans)
    assert len(filtered) == 3
    assert filtered[0].start == 1 and filtered[0].end == 4
    assert filtered[1].start == 6 and filtered[1].end == 8
    assert filtered[2].start == 10 and filtered[2].end == 14
    # Test filtering overlaps with longest preference
    spans = [doc[1:4], doc[1:3], doc[5:10], doc[7:9], doc[1:4]]
    filtered = filter_spans(spans)
    assert len(filtered) == 2
    assert len(filtered[0]) == 3
    assert len(filtered[1]) == 5
    assert filtered[0].start == 1 and filtered[0].end == 4
    assert filtered[1].start == 5 and filtered[1].end == 10
    # Test filtering overlaps with earlier preference for identical length
    spans = [doc[1:4], doc[2:5], doc[5:10], doc[7:9], doc[1:4]]
    filtered = filter_spans(spans)
    assert len(filtered) == 2
    assert len(filtered[0]) == 3
    assert len(filtered[1]) == 5
    assert filtered[0].start == 1 and filtered[0].end == 4
    assert filtered[1].start == 5 and filtered[1].end == 10


def test_span_eq_hash(doc, doc_not_parsed):
    assert doc[0:2] == doc[0:2]
    assert doc[0:2] != doc[1:3]
    assert doc[0:2] != doc_not_parsed[0:2]
    assert hash(doc[0:2]) == hash(doc[0:2])
    assert hash(doc[0:2]) != hash(doc[1:3])
    assert hash(doc[0:2]) != hash(doc_not_parsed[0:2])
