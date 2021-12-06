import pytest
import numpy
from numpy.testing import assert_array_equal

from spacy.attrs import ORTH, LENGTH
from spacy.lang.en import English
from spacy.tokens import Doc, Span, Token
from spacy.vocab import Vocab
from spacy.util import filter_spans
from thinc.api import get_current_ops

from ..util import add_vecs_to_vocab
from .test_underscore import clean_underscore  # noqa: F401


@pytest.fixture
def doc(en_tokenizer):
    # fmt: off
    text = "This is a sentence. This is another sentence. And a third."
    heads = [1, 1, 3, 1, 1, 6, 6, 8, 6, 6, 12, 12, 12, 12]
    deps = ["nsubj", "ROOT", "det", "attr", "punct", "nsubj", "ROOT", "det",
            "attr", "punct", "ROOT", "det", "npadvmod", "punct"]
    ents = ["O", "O", "B-ENT", "I-ENT", "I-ENT", "I-ENT", "I-ENT", "O", "O",
            "O", "O", "O", "O", "O"]
    # fmt: on
    tokens = en_tokenizer(text)
    lemmas = [t.text for t in tokens]  # this is not correct, just a placeholder
    spaces = [bool(t.whitespace_) for t in tokens]
    return Doc(
        tokens.vocab,
        words=[t.text for t in tokens],
        spaces=spaces,
        heads=heads,
        deps=deps,
        ents=ents,
        lemmas=lemmas,
    )


@pytest.fixture
def doc_not_parsed(en_tokenizer):
    text = "This is a sentence. This is another sentence. And a third."
    tokens = en_tokenizer(text)
    doc = Doc(tokens.vocab, words=[t.text for t in tokens])
    return doc


@pytest.mark.issue(1537)
def test_issue1537():
    """Test that Span.as_doc() doesn't segfault."""
    string = "The sky is blue . The man is pink . The dog is purple ."
    doc = Doc(Vocab(), words=string.split())
    doc[0].sent_start = True
    for word in doc[1:]:
        if word.nbor(-1).text == ".":
            word.sent_start = True
        else:
            word.sent_start = False
    sents = list(doc.sents)
    sent0 = sents[0].as_doc()
    sent1 = sents[1].as_doc()
    assert isinstance(sent0, Doc)
    assert isinstance(sent1, Doc)


@pytest.mark.issue(1612)
def test_issue1612(en_tokenizer):
    """Test that span.orth_ is identical to span.text"""
    doc = en_tokenizer("The black cat purrs.")
    span = doc[1:3]
    assert span.orth_ == span.text


@pytest.mark.issue(3199)
def test_issue3199():
    """Test that Span.noun_chunks works correctly if no noun chunks iterator
    is available. To make this test future-proof, we're constructing a Doc
    with a new Vocab here and a parse tree to make sure the noun chunks run.
    """
    words = ["This", "is", "a", "sentence"]
    doc = Doc(Vocab(), words=words, heads=[0] * len(words), deps=["dep"] * len(words))
    with pytest.raises(NotImplementedError):
        list(doc[0:3].noun_chunks)


@pytest.mark.issue(5152)
def test_issue5152():
    # Test that the comparison between a Span and a Token, goes well
    # There was a bug when the number of tokens in the span equaled the number of characters in the token (!)
    nlp = English()
    text = nlp("Talk about being boring!")
    text_var = nlp("Talk of being boring!")
    y = nlp("Let")
    span = text[0:3]  # Talk about being
    span_2 = text[0:3]  # Talk about being
    span_3 = text_var[0:3]  # Talk of being
    token = y[0]  # Let
    with pytest.warns(UserWarning):
        assert span.similarity(token) == 0.0
    assert span.similarity(span_2) == 1.0
    with pytest.warns(UserWarning):
        assert span_2.similarity(span_3) < 1.0


@pytest.mark.issue(6755)
def test_issue6755(en_tokenizer):
    doc = en_tokenizer("This is a magnificent sentence.")
    span = doc[:0]
    assert span.text_with_ws == ""
    assert span.text == ""


@pytest.mark.parametrize(
    "sentence, start_idx,end_idx,label",
    [("Welcome to Mumbai, my friend", 11, 17, "GPE")],
)
@pytest.mark.issue(6815)
def test_issue6815_1(sentence, start_idx, end_idx, label):
    nlp = English()
    doc = nlp(sentence)
    span = doc[:].char_span(start_idx, end_idx, label=label)
    assert span.label_ == label


@pytest.mark.parametrize(
    "sentence, start_idx,end_idx,kb_id", [("Welcome to Mumbai, my friend", 11, 17, 5)]
)
@pytest.mark.issue(6815)
def test_issue6815_2(sentence, start_idx, end_idx, kb_id):
    nlp = English()
    doc = nlp(sentence)
    span = doc[:].char_span(start_idx, end_idx, kb_id=kb_id)
    assert span.kb_id == kb_id


@pytest.mark.parametrize(
    "sentence, start_idx,end_idx,vector",
    [("Welcome to Mumbai, my friend", 11, 17, numpy.array([0.1, 0.2, 0.3]))],
)
@pytest.mark.issue(6815)
def test_issue6815_3(sentence, start_idx, end_idx, vector):
    nlp = English()
    doc = nlp(sentence)
    span = doc[:].char_span(start_idx, end_idx, vector=vector)
    assert (span.vector == vector).all()


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


def test_spans_root2(en_tokenizer):
    text = "through North and South Carolina"
    heads = [0, 4, 1, 1, 0]
    deps = ["dep"] * len(heads)
    tokens = en_tokenizer(text)
    doc = Doc(tokens.vocab, words=[t.text for t in tokens], heads=heads, deps=deps)
    assert doc[-2:].root.text == "Carolina"


def test_spans_span_sent(doc, doc_not_parsed):
    """Test span.sent property"""
    assert len(list(doc.sents))
    assert doc[:2].sent.root.text == "is"
    assert doc[:2].sent.text == "This is a sentence."
    assert doc[6:7].sent.root.left_edge.text == "This"
    assert doc[0 : len(doc)].sent == list(doc.sents)[0]
    assert list(doc[0 : len(doc)].sents) == list(doc.sents)

    with pytest.raises(ValueError):
        doc_not_parsed[:2].sent

    # test on manual sbd
    doc_not_parsed[0].is_sent_start = True
    doc_not_parsed[5].is_sent_start = True
    assert doc_not_parsed[1:3].sent == doc_not_parsed[0:5]
    assert doc_not_parsed[10:14].sent == doc_not_parsed[5:]


@pytest.mark.parametrize(
    "start,end,expected_sentence",
    [
        (0, 14, "This is"),  # Entire doc
        (1, 4, "This is"),  # Overlapping with 2 sentences
        (0, 2, "This is"),  # Beginning of the Doc. Full sentence
        (0, 1, "This is"),  # Beginning of the Doc. Part of a sentence
        (10, 14, "And a"),  # End of the Doc. Overlapping with 2 senteces
        (12, 14, "third."),  # End of the Doc. Full sentence
        (1, 1, "This is"),  # Empty Span
    ],
)
def test_spans_span_sent_user_hooks(doc, start, end, expected_sentence):

    # Doc-level sents hook
    def user_hook(doc):
        return [doc[ii : ii + 2] for ii in range(0, len(doc), 2)]

    doc.user_hooks["sents"] = user_hook

    # Make sure doc-level sents hook works
    assert doc[start:end].sent.text == expected_sentence

    # Span-level sent hook
    doc.user_span_hooks["sent"] = lambda x: x
    # Now, span=level sent hook overrides the doc-level sents hook
    assert doc[start:end].sent == doc[start:end]


def test_spans_lca_matrix(en_tokenizer):
    """Test span's lca matrix generation"""
    tokens = en_tokenizer("the lazy dog slept")
    doc = Doc(
        tokens.vocab,
        words=[t.text for t in tokens],
        heads=[2, 2, 3, 3],
        deps=["dep"] * 4,
    )
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

    # example from Span API docs
    tokens = en_tokenizer("I like New York in Autumn")
    doc = Doc(
        tokens.vocab,
        words=[t.text for t in tokens],
        heads=[1, 1, 3, 1, 3, 4],
        deps=["dep"] * len(tokens),
    )
    lca = doc[1:4].get_lca_matrix()
    assert_array_equal(lca, numpy.asarray([[0, 0, 0], [0, 1, 2], [0, 2, 2]]))


def test_span_similarity_match():
    doc = Doc(Vocab(), words=["a", "b", "a", "b"])
    span1 = doc[:2]
    span2 = doc[2:]
    with pytest.warns(UserWarning):
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

    # default and specified alignment mode "strict"
    span2 = doc.char_span(span1.start_char, span1.end_char, label="GPE")
    assert span1.start_char == span2.start_char
    assert span1.end_char == span2.end_char
    assert span2.label_ == "GPE"

    span2 = doc.char_span(
        span1.start_char, span1.end_char, label="GPE", alignment_mode="strict"
    )
    assert span1.start_char == span2.start_char
    assert span1.end_char == span2.end_char
    assert span2.label_ == "GPE"

    # alignment mode "contract"
    span2 = doc.char_span(
        span1.start_char - 3, span1.end_char, label="GPE", alignment_mode="contract"
    )
    assert span1.start_char == span2.start_char
    assert span1.end_char == span2.end_char
    assert span2.label_ == "GPE"

    # alignment mode "expand"
    span2 = doc.char_span(
        span1.start_char + 1, span1.end_char, label="GPE", alignment_mode="expand"
    )
    assert span1.start_char == span2.start_char
    assert span1.end_char == span2.end_char
    assert span2.label_ == "GPE"

    # unsupported alignment mode
    with pytest.raises(ValueError):
        span2 = doc.char_span(
            span1.start_char + 1, span1.end_char, label="GPE", alignment_mode="unk"
        )


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

    # partial initial entity is removed
    assert len(span_doc.ents) == 0

    # full entity is preserved
    span_doc = doc[2:10].as_doc()
    assert len(span_doc.ents) == 1

    # partial final entity is removed
    span_doc = doc[0:5].as_doc()
    assert len(span_doc.ents) == 0


@pytest.mark.usefixtures("clean_underscore")
def test_span_as_doc_user_data(doc):
    """Test that the user_data can be preserved (but not by default)."""
    my_key = "my_info"
    my_value = 342
    doc.user_data[my_key] = my_value
    Token.set_extension("is_x", default=False)
    doc[7]._.is_x = True

    span = doc[4:10]
    span_doc_with = span.as_doc(copy_user_data=True)
    span_doc_without = span.as_doc()

    assert doc.user_data.get(my_key, None) is my_value
    assert span_doc_with.user_data.get(my_key, None) is my_value
    assert span_doc_without.user_data.get(my_key, None) is None
    for i in range(len(span_doc_with)):
        if i != 3:
            assert span_doc_with[i]._.is_x is False
        else:
            assert span_doc_with[i]._.is_x is True
    assert not any([t._.is_x for t in span_doc_without])


def test_span_string_label_kb_id(doc):
    span = Span(doc, 0, 1, label="hello", kb_id="Q342")
    assert span.label_ == "hello"
    assert span.label == doc.vocab.strings["hello"]
    assert span.kb_id_ == "Q342"
    assert span.kb_id == doc.vocab.strings["Q342"]


def test_span_attrs_writable(doc):
    span = Span(doc, 0, 1)
    span.label_ = "label"
    span.kb_id_ = "kb_id"


def test_span_ents_property(doc):
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
    assert sentences[2].ents[0].text == "a third."
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

    # check that an out-of-bounds is not equivalent to the span of the full doc
    assert doc[0 : len(doc)] != doc[len(doc) : len(doc) + 1]


def test_span_boundaries(doc):
    start = 1
    end = 5
    span = doc[start:end]
    for i in range(start, end):
        assert span[i - start] == doc[i]
    with pytest.raises(IndexError):
        span[-5]
    with pytest.raises(IndexError):
        span[5]

    empty_span_0 = doc[0:0]
    assert empty_span_0.text == ""
    assert empty_span_0.start == 0
    assert empty_span_0.end == 0
    assert empty_span_0.start_char == 0
    assert empty_span_0.end_char == 0

    empty_span_1 = doc[1:1]
    assert empty_span_1.text == ""
    assert empty_span_1.start == 1
    assert empty_span_1.end == 1
    assert empty_span_1.start_char == empty_span_1.end_char

    oob_span_start = doc[-len(doc) - 1 : -len(doc) - 10]
    assert oob_span_start.text == ""
    assert oob_span_start.start == 0
    assert oob_span_start.end == 0
    assert oob_span_start.start_char == 0
    assert oob_span_start.end_char == 0

    oob_span_end = doc[len(doc) + 1 : len(doc) + 10]
    assert oob_span_end.text == ""
    assert oob_span_end.start == len(doc)
    assert oob_span_end.end == len(doc)
    assert oob_span_end.start_char == len(doc.text)
    assert oob_span_end.end_char == len(doc.text)


def test_span_lemma(doc):
    # span lemmas should have the same number of spaces as the span
    sp = doc[1:5]
    assert len(sp.text.split(" ")) == len(sp.lemma_.split(" "))


def test_sent(en_tokenizer):
    doc = en_tokenizer("Check span.sent raises error if doc is not sentencized.")
    span = doc[1:3]
    assert not span.doc.has_annotation("SENT_START")
    with pytest.raises(ValueError):
        span.sent


def test_span_with_vectors(doc):
    ops = get_current_ops()
    prev_vectors = doc.vocab.vectors
    vectors = [
        ("apple", ops.asarray([1, 2, 3])),
        ("orange", ops.asarray([-1, -2, -3])),
        ("And", ops.asarray([-1, -1, -1])),
        ("juice", ops.asarray([5, 5, 10])),
        ("pie", ops.asarray([7, 6.3, 8.9])),
    ]
    add_vecs_to_vocab(doc.vocab, vectors)
    # 0-length span
    assert_array_equal(ops.to_numpy(doc[0:0].vector), numpy.zeros((3,)))
    # longer span with no vector
    assert_array_equal(ops.to_numpy(doc[0:4].vector), numpy.zeros((3,)))
    # single-token span with vector
    assert_array_equal(ops.to_numpy(doc[10:11].vector), [-1, -1, -1])
    doc.vocab.vectors = prev_vectors


@pytest.mark.parametrize(
    "start,end,expected_sentences,expected_sentences_with_hook",
    [
        (0, 14, 3, 7),  # Entire doc
        (3, 6, 2, 2),  # Overlapping with 2 sentences
        (0, 4, 1, 2),  # Beginning of the Doc. Full sentence
        (0, 3, 1, 2),  # Beginning of the Doc. Part of a sentence
        (9, 14, 2, 3),  # End of the Doc. Overlapping with 2 senteces
        (10, 14, 1, 2),  # End of the Doc. Full sentence
        (11, 14, 1, 2),  # End of the Doc. Partial sentence
        (0, 0, 1, 1),  # Empty Span
    ],
)
def test_span_sents(doc, start, end, expected_sentences, expected_sentences_with_hook):

    assert len(list(doc[start:end].sents)) == expected_sentences

    def user_hook(doc):
        return [doc[ii : ii + 2] for ii in range(0, len(doc), 2)]

    doc.user_hooks["sents"] = user_hook

    assert len(list(doc[start:end].sents)) == expected_sentences_with_hook

    doc.user_span_hooks["sents"] = lambda x: [x]

    assert list(doc[start:end].sents)[0] == doc[start:end]
    assert len(list(doc[start:end].sents)) == 1


def test_span_sents_not_parsed(doc_not_parsed):
    with pytest.raises(ValueError):
        list(Span(doc_not_parsed, 0, 3).sents)
