from audioop import reverse
from pickle import EMPTY_DICT
import weakref

import numpy
from time import time
from numpy.testing import assert_array_equal
from murmurhash.mrmr import hash
import pytest
import warnings
from thinc.api import NumpyOps, get_current_ops

from spacy.attrs import DEP, ENT_IOB, ENT_TYPE, HEAD, IS_ALPHA, MORPH, POS
from spacy.attrs import SENT_START, TAG
from spacy.lang.en import English
from spacy.lang.xx import MultiLanguage
from spacy.language import Language
from spacy.lexeme import Lexeme
from spacy.tokens import Doc, Span, SpanGroup, Token
from spacy.tokens.doc import get_fnv1a_hash
from spacy.util import get_search_char_byte_arrays
from spacy.vocab import Vocab

from .test_underscore import clean_underscore  # noqa: F401


def test_doc_api_init(en_vocab):
    words = ["a", "b", "c", "d"]
    heads = [0, 0, 2, 2]
    # set sent_start by sent_starts
    doc = Doc(en_vocab, words=words, sent_starts=[True, False, True, False])
    assert [t.is_sent_start for t in doc] == [True, False, True, False]

    # set sent_start by heads
    doc = Doc(en_vocab, words=words, heads=heads, deps=["dep"] * 4)
    assert [t.is_sent_start for t in doc] == [True, False, True, False]
    # heads override sent_starts
    doc = Doc(
        en_vocab, words=words, sent_starts=[True] * 4, heads=heads, deps=["dep"] * 4
    )
    assert [t.is_sent_start for t in doc] == [True, False, True, False]


@pytest.mark.issue(1547)
def test_issue1547():
    """Test that entity labels still match after merging tokens."""
    words = ["\n", "worda", ".", "\n", "wordb", "-", "Biosphere", "2", "-", " \n"]
    doc = Doc(Vocab(), words=words)
    doc.ents = [Span(doc, 6, 8, label=doc.vocab.strings["PRODUCT"])]
    with doc.retokenize() as retokenizer:
        retokenizer.merge(doc[5:7])
    assert [ent.text for ent in doc.ents]


@pytest.mark.issue(1757)
def test_issue1757():
    """Test comparison against None doesn't cause segfault."""
    doc = Doc(Vocab(), words=["a", "b", "c"])
    assert not doc[0] < None
    assert not doc[0] is None
    assert doc[0] >= None
    assert not doc[:2] < None
    assert not doc[:2] is None
    assert doc[:2] >= None
    assert not doc.vocab["a"] is None
    assert not doc.vocab["a"] < None


@pytest.mark.issue(2396)
def test_issue2396(en_vocab):
    words = ["She", "created", "a", "test", "for", "spacy"]
    heads = [1, 1, 3, 1, 3, 4]
    deps = ["dep"] * len(heads)
    matrix = numpy.array(
        [
            [0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 2, 3, 3, 3],
            [1, 1, 3, 3, 3, 3],
            [1, 1, 3, 3, 4, 4],
            [1, 1, 3, 3, 4, 5],
        ],
        dtype=numpy.int32,
    )
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    span = doc[:]
    assert (doc.get_lca_matrix() == matrix).all()
    assert (span.get_lca_matrix() == matrix).all()


@pytest.mark.issue(11499)
def test_init_args_unmodified(en_vocab):
    words = ["A", "sentence"]
    ents = ["B-TYPE1", ""]
    sent_starts = [True, False]
    Doc(
        vocab=en_vocab,
        words=words,
        ents=ents,
        sent_starts=sent_starts,
    )
    assert ents == ["B-TYPE1", ""]
    assert sent_starts == [True, False]


@pytest.mark.parametrize("text", ["-0.23", "+123,456", "±1"])
@pytest.mark.parametrize("lang_cls", [English, MultiLanguage])
@pytest.mark.issue(2782)
def test_issue2782(text, lang_cls):
    """Check that like_num handles + and - before number."""
    nlp = lang_cls()
    doc = nlp(text)
    assert len(doc) == 1
    assert doc[0].like_num


@pytest.mark.parametrize(
    "sentence",
    [
        "The story was to the effect that a young American student recently called on Professor Christlieb with a letter of introduction.",
        "The next month Barry Siddall joined Stoke City on a free transfer, after Chris Pearce had established himself as the Vale's #1.",
        "The next month Barry Siddall joined Stoke City on a free transfer, after Chris Pearce had established himself as the Vale's number one",
        "Indeed, making the one who remains do all the work has installed him into a position of such insolent tyranny, it will take a month at least to reduce him to his proper proportions.",
        "It was a missed assignment, but it shouldn't have resulted in a turnover ...",
    ],
)
@pytest.mark.issue(3869)
def test_issue3869(sentence):
    """Test that the Doc's count_by function works consistently"""
    nlp = English()
    doc = nlp(sentence)
    count = 0
    for token in doc:
        count += token.is_alpha
    assert count == doc.count_by(IS_ALPHA).get(1, 0)


@pytest.mark.issue(3962)
def test_issue3962(en_vocab):
    """Ensure that as_doc does not result in out-of-bound access of tokens.
    This is achieved by setting the head to itself if it would lie out of the span otherwise."""
    # fmt: off
    words = ["He", "jests", "at", "scars", ",", "that", "never", "felt", "a", "wound", "."]
    heads = [1, 7, 1, 2, 7, 7, 7, 7, 9, 7, 7]
    deps = ["nsubj", "ccomp", "prep", "pobj", "punct", "nsubj", "neg", "ROOT", "det", "dobj", "punct"]
    # fmt: on
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    span2 = doc[1:5]  # "jests at scars ,"
    doc2 = span2.as_doc()
    doc2_json = doc2.to_json()
    assert doc2_json
    # head set to itself, being the new artificial root
    assert doc2[0].head.text == "jests"
    assert doc2[0].dep_ == "dep"
    assert doc2[1].head.text == "jests"
    assert doc2[1].dep_ == "prep"
    assert doc2[2].head.text == "at"
    assert doc2[2].dep_ == "pobj"
    assert doc2[3].head.text == "jests"  # head set to the new artificial root
    assert doc2[3].dep_ == "dep"
    # We should still have 1 sentence
    assert len(list(doc2.sents)) == 1
    span3 = doc[6:9]  # "never felt a"
    doc3 = span3.as_doc()
    doc3_json = doc3.to_json()
    assert doc3_json
    assert doc3[0].head.text == "felt"
    assert doc3[0].dep_ == "neg"
    assert doc3[1].head.text == "felt"
    assert doc3[1].dep_ == "ROOT"
    assert doc3[2].head.text == "felt"  # head set to ancestor
    assert doc3[2].dep_ == "dep"
    # We should still have 1 sentence as "a" can be attached to "felt" instead of "wound"
    assert len(list(doc3.sents)) == 1


@pytest.mark.issue(3962)
def test_issue3962_long(en_vocab):
    """Ensure that as_doc does not result in out-of-bound access of tokens.
    This is achieved by setting the head to itself if it would lie out of the span otherwise."""
    # fmt: off
    words = ["He", "jests", "at", "scars", ".", "They", "never", "felt", "a", "wound", "."]
    heads = [1, 1, 1, 2, 1, 7, 7, 7, 9, 7, 7]
    deps = ["nsubj", "ROOT", "prep", "pobj", "punct", "nsubj", "neg", "ROOT", "det", "dobj", "punct"]
    # fmt: on
    two_sent_doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    span2 = two_sent_doc[1:7]  # "jests at scars. They never"
    doc2 = span2.as_doc()
    doc2_json = doc2.to_json()
    assert doc2_json
    # head set to itself, being the new artificial root (in sentence 1)
    assert doc2[0].head.text == "jests"
    assert doc2[0].dep_ == "ROOT"
    assert doc2[1].head.text == "jests"
    assert doc2[1].dep_ == "prep"
    assert doc2[2].head.text == "at"
    assert doc2[2].dep_ == "pobj"
    assert doc2[3].head.text == "jests"
    assert doc2[3].dep_ == "punct"
    # head set to itself, being the new artificial root (in sentence 2)
    assert doc2[4].head.text == "They"
    assert doc2[4].dep_ == "dep"
    # head set to the new artificial head (in sentence 2)
    assert doc2[4].head.text == "They"
    assert doc2[4].dep_ == "dep"
    # We should still have 2 sentences
    sents = list(doc2.sents)
    assert len(sents) == 2
    assert sents[0].text == "jests at scars ."
    assert sents[1].text == "They never"


@Language.factory("my_pipe")
class CustomPipe:
    def __init__(self, nlp, name="my_pipe"):
        self.name = name
        Span.set_extension("my_ext", getter=self._get_my_ext)
        Doc.set_extension("my_ext", default=None)

    def __call__(self, doc):
        gathered_ext = []
        for sent in doc.sents:
            sent_ext = self._get_my_ext(sent)
            sent._.set("my_ext", sent_ext)
            gathered_ext.append(sent_ext)

        doc._.set("my_ext", "\n".join(gathered_ext))
        return doc

    @staticmethod
    def _get_my_ext(span):
        return str(span.end)


@pytest.mark.issue(4903)
def test_issue4903():
    """Ensure that this runs correctly and doesn't hang or crash on Windows /
    macOS."""
    nlp = English()
    nlp.add_pipe("sentencizer")
    nlp.add_pipe("my_pipe", after="sentencizer")
    text = ["I like bananas.", "Do you like them?", "No, I prefer wasabi."]
    if isinstance(get_current_ops(), NumpyOps):
        docs = list(nlp.pipe(text, n_process=2))
        assert docs[0].text == "I like bananas."
        assert docs[1].text == "Do you like them?"
        assert docs[2].text == "No, I prefer wasabi."


@pytest.mark.issue(5048)
def test_issue5048(en_vocab):
    words = ["This", "is", "a", "sentence"]
    pos_s = ["DET", "VERB", "DET", "NOUN"]
    spaces = [" ", " ", " ", ""]
    deps_s = ["dep", "adj", "nn", "atm"]
    tags_s = ["DT", "VBZ", "DT", "NN"]
    strings = en_vocab.strings
    for w in words:
        strings.add(w)
    deps = [strings.add(d) for d in deps_s]
    pos = [strings.add(p) for p in pos_s]
    tags = [strings.add(t) for t in tags_s]
    attrs = [POS, DEP, TAG]
    array = numpy.array(list(zip(pos, deps, tags)), dtype="uint64")
    doc = Doc(en_vocab, words=words, spaces=spaces)
    doc.from_array(attrs, array)
    v1 = [(token.text, token.pos_, token.tag_) for token in doc]
    doc2 = Doc(en_vocab, words=words, pos=pos_s, deps=deps_s, tags=tags_s)
    v2 = [(token.text, token.pos_, token.tag_) for token in doc2]
    assert v1 == v2


@pytest.mark.parametrize("text", [["one", "two", "three"]])
def test_doc_api_compare_by_string_position(en_vocab, text):
    doc = Doc(en_vocab, words=text)
    # Get the tokens in this order, so their ID ordering doesn't match the idx
    token3 = doc[-1]
    token2 = doc[-2]
    token1 = doc[-1]
    token1, token2, token3 = doc
    assert token1 < token2 < token3
    assert not token1 > token2
    assert token2 > token1
    assert token2 <= token3
    assert token3 >= token1


def test_doc_api_getitem(en_tokenizer):
    text = "Give it back! He pleaded."
    tokens = en_tokenizer(text)
    assert tokens[0].text == "Give"
    assert tokens[-1].text == "."
    with pytest.raises(IndexError):
        tokens[len(tokens)]

    def to_str(span):
        return "/".join(token.text for token in span)

    span = tokens[1:1]
    assert not to_str(span)
    span = tokens[1:4]
    assert to_str(span) == "it/back/!"
    span = tokens[1:4:1]
    assert to_str(span) == "it/back/!"
    with pytest.raises(ValueError):
        tokens[1:4:2]
    with pytest.raises(ValueError):
        tokens[1:4:-1]

    span = tokens[-3:6]
    assert to_str(span) == "He/pleaded"
    span = tokens[4:-1]
    assert to_str(span) == "He/pleaded"
    span = tokens[-5:-3]
    assert to_str(span) == "back/!"
    span = tokens[5:4]
    assert span.start == span.end == 5 and not to_str(span)
    span = tokens[4:-3]
    assert span.start == span.end == 4 and not to_str(span)

    span = tokens[:]
    assert to_str(span) == "Give/it/back/!/He/pleaded/."
    span = tokens[4:]
    assert to_str(span) == "He/pleaded/."
    span = tokens[:4]
    assert to_str(span) == "Give/it/back/!"
    span = tokens[:-3]
    assert to_str(span) == "Give/it/back/!"
    span = tokens[-3:]
    assert to_str(span) == "He/pleaded/."

    span = tokens[4:50]
    assert to_str(span) == "He/pleaded/."
    span = tokens[-50:4]
    assert to_str(span) == "Give/it/back/!"
    span = tokens[-50:-40]
    assert span.start == span.end == 0 and not to_str(span)
    span = tokens[40:50]
    assert span.start == span.end == 7 and not to_str(span)

    span = tokens[1:4]
    assert span[0].orth_ == "it"
    subspan = span[:]
    assert to_str(subspan) == "it/back/!"
    subspan = span[:2]
    assert to_str(subspan) == "it/back"
    subspan = span[1:]
    assert to_str(subspan) == "back/!"
    subspan = span[:-1]
    assert to_str(subspan) == "it/back"
    subspan = span[-2:]
    assert to_str(subspan) == "back/!"
    subspan = span[1:2]
    assert to_str(subspan) == "back"
    subspan = span[-2:-1]
    assert to_str(subspan) == "back"
    subspan = span[-50:50]
    assert to_str(subspan) == "it/back/!"
    subspan = span[50:-50]
    assert subspan.start == subspan.end == 4 and not to_str(subspan)


@pytest.mark.parametrize(
    "text", ["Give it back! He pleaded.", " Give it back! He pleaded. "]
)
def test_doc_api_serialize(en_tokenizer, text):
    tokens = en_tokenizer(text)
    tokens[0].lemma_ = "lemma"
    tokens[0].norm_ = "norm"
    tokens.ents = [(tokens.vocab.strings["PRODUCT"], 0, 1)]
    tokens[0].ent_kb_id_ = "ent_kb_id"
    tokens[0].ent_id_ = "ent_id"
    new_tokens = Doc(tokens.vocab).from_bytes(tokens.to_bytes())
    assert tokens.text == new_tokens.text
    assert [t.text for t in tokens] == [t.text for t in new_tokens]
    assert [t.orth for t in tokens] == [t.orth for t in new_tokens]
    assert new_tokens[0].lemma_ == "lemma"
    assert new_tokens[0].norm_ == "norm"
    assert new_tokens[0].ent_kb_id_ == "ent_kb_id"
    assert new_tokens[0].ent_id_ == "ent_id"

    new_tokens = Doc(tokens.vocab).from_bytes(
        tokens.to_bytes(exclude=["tensor"]), exclude=["tensor"]
    )
    assert tokens.text == new_tokens.text
    assert [t.text for t in tokens] == [t.text for t in new_tokens]
    assert [t.orth for t in tokens] == [t.orth for t in new_tokens]

    new_tokens = Doc(tokens.vocab).from_bytes(
        tokens.to_bytes(exclude=["sentiment"]), exclude=["sentiment"]
    )
    assert tokens.text == new_tokens.text
    assert [t.text for t in tokens] == [t.text for t in new_tokens]
    assert [t.orth for t in tokens] == [t.orth for t in new_tokens]

    def inner_func(d1, d2):
        return "hello!"

    _ = tokens.to_bytes()  # noqa: F841
    with pytest.warns(UserWarning):
        tokens.user_hooks["similarity"] = inner_func
        _ = tokens.to_bytes()  # noqa: F841


def test_doc_api_set_ents(en_tokenizer):
    text = "I use goggle chrone to surf the web"
    tokens = en_tokenizer(text)
    assert len(tokens.ents) == 0
    tokens.ents = [(tokens.vocab.strings["PRODUCT"], 2, 4)]
    assert len(list(tokens.ents)) == 1
    assert [t.ent_iob for t in tokens] == [2, 2, 3, 1, 2, 2, 2, 2]
    assert tokens.ents[0].label_ == "PRODUCT"
    assert tokens.ents[0].start == 2
    assert tokens.ents[0].end == 4


def test_doc_api_sents_empty_string(en_tokenizer):
    doc = en_tokenizer("")
    sents = list(doc.sents)
    assert len(sents) == 0


def test_doc_api_runtime_error(en_tokenizer):
    # Example that caused run-time error while parsing Reddit
    # fmt: off
    text = "67% of black households are single parent \n\n72% of all black babies born out of wedlock \n\n50% of all black kids don\u2019t finish high school"
    deps = ["nummod", "nsubj", "prep", "amod", "pobj", "ROOT", "amod", "attr", "", "nummod", "appos", "prep", "det",
            "amod", "pobj", "acl", "prep", "prep", "pobj",
            "", "nummod", "nsubj", "prep", "det", "amod", "pobj", "aux", "neg", "ccomp", "amod", "dobj"]
    # fmt: on
    tokens = en_tokenizer(text)
    doc = Doc(tokens.vocab, words=[t.text for t in tokens], deps=deps)
    nps = []
    for np in doc.noun_chunks:
        while len(np) > 1 and np[0].dep_ not in ("advmod", "amod", "compound"):
            np = np[1:]
        if len(np) > 1:
            nps.append(np)
    with doc.retokenize() as retokenizer:
        for np in nps:
            attrs = {
                "tag": np.root.tag_,
                "lemma": np.text,
                "ent_type": np.root.ent_type_,
            }
            retokenizer.merge(np, attrs=attrs)


def test_doc_api_right_edge(en_vocab):
    """Test for bug occurring from Unshift action, causing incorrect right edge"""
    # fmt: off
    words = [
        "I", "have", "proposed", "to", "myself", ",", "for", "the", "sake",
        "of", "such", "as", "live", "under", "the", "government", "of", "the",
        "Romans", ",", "to", "translate", "those", "books", "into", "the",
        "Greek", "tongue", "."
    ]
    heads = [2, 2, 2, 2, 3, 2, 21, 8, 6, 8, 11, 8, 11, 12, 15, 13, 15, 18, 16, 12, 21, 2, 23, 21, 21, 27, 27, 24, 2]
    deps = ["dep"] * len(heads)
    # fmt: on
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    assert doc[6].text == "for"
    subtree = [w.text for w in doc[6].subtree]
    # fmt: off
    assert subtree == ["for", "the", "sake", "of", "such", "as", "live", "under", "the", "government", "of", "the", "Romans", ","]
    # fmt: on
    assert doc[6].right_edge.text == ","


def test_doc_api_has_vector():
    vocab = Vocab()
    vocab.reset_vectors(width=2)
    vocab.set_vector("kitten", vector=numpy.asarray([0.0, 2.0], dtype="f"))
    doc = Doc(vocab, words=["kitten"])
    assert doc.has_vector


def test_doc_api_similarity_match():
    doc = Doc(Vocab(), words=["a"])
    assert doc.similarity(doc[0]) == 1.0
    assert doc.similarity(doc.vocab["a"]) == 1.0
    doc2 = Doc(doc.vocab, words=["a", "b", "c"])
    with pytest.warns(UserWarning):
        assert doc.similarity(doc2[:1]) == 1.0
        assert doc.similarity(doc2) == 0.0


@pytest.mark.parametrize(
    "words,heads,lca_matrix",
    [
        (
            ["the", "lazy", "dog", "slept"],
            [2, 2, 3, 3],
            numpy.array([[0, 2, 2, 3], [2, 1, 2, 3], [2, 2, 2, 3], [3, 3, 3, 3]]),
        ),
        (
            ["The", "lazy", "dog", "slept", ".", "The", "quick", "fox", "jumped"],
            [2, 2, 3, 3, 3, 7, 7, 8, 8],
            numpy.array(
                [
                    [0, 2, 2, 3, 3, -1, -1, -1, -1],
                    [2, 1, 2, 3, 3, -1, -1, -1, -1],
                    [2, 2, 2, 3, 3, -1, -1, -1, -1],
                    [3, 3, 3, 3, 3, -1, -1, -1, -1],
                    [3, 3, 3, 3, 4, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, 5, 7, 7, 8],
                    [-1, -1, -1, -1, -1, 7, 6, 7, 8],
                    [-1, -1, -1, -1, -1, 7, 7, 7, 8],
                    [-1, -1, -1, -1, -1, 8, 8, 8, 8],
                ]
            ),
        ),
    ],
)
def test_lowest_common_ancestor(en_vocab, words, heads, lca_matrix):
    doc = Doc(en_vocab, words, heads=heads, deps=["dep"] * len(heads))
    lca = doc.get_lca_matrix()
    assert (lca == lca_matrix).all()
    assert lca[1, 1] == 1
    assert lca[0, 1] == 2
    assert lca[1, 2] == 2


def test_doc_is_nered(en_vocab):
    words = ["I", "live", "in", "New", "York"]
    doc = Doc(en_vocab, words=words)
    assert not doc.has_annotation("ENT_IOB")
    doc.ents = [Span(doc, 3, 5, label="GPE")]
    assert doc.has_annotation("ENT_IOB")
    # Test creating doc from array with unknown values
    arr = numpy.array([[0, 0], [0, 0], [0, 0], [384, 3], [384, 1]], dtype="uint64")
    doc = Doc(en_vocab, words=words).from_array([ENT_TYPE, ENT_IOB], arr)
    assert doc.has_annotation("ENT_IOB")
    # Test serialization
    new_doc = Doc(en_vocab).from_bytes(doc.to_bytes())
    assert new_doc.has_annotation("ENT_IOB")


def test_doc_from_array_sent_starts(en_vocab):
    # fmt: off
    words = ["I", "live", "in", "New", "York", ".", "I", "like", "cats", "."]
    heads = [0, 0, 0, 0, 0, 0, 6, 6, 6, 6]
    deps = ["ROOT", "dep", "dep", "dep", "dep", "dep", "ROOT", "dep", "dep", "dep"]
    # fmt: on
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    # HEAD overrides SENT_START without warning
    attrs = [SENT_START, HEAD]
    arr = doc.to_array(attrs)
    new_doc = Doc(en_vocab, words=words)
    new_doc.from_array(attrs, arr)
    # no warning using default attrs
    attrs = doc._get_array_attrs()
    arr = doc.to_array(attrs)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        new_doc.from_array(attrs, arr)
    # only SENT_START uses SENT_START
    attrs = [SENT_START]
    arr = doc.to_array(attrs)
    new_doc = Doc(en_vocab, words=words)
    new_doc.from_array(attrs, arr)
    assert [t.is_sent_start for t in doc] == [t.is_sent_start for t in new_doc]
    assert not new_doc.has_annotation("DEP")
    # only HEAD uses HEAD
    attrs = [HEAD, DEP]
    arr = doc.to_array(attrs)
    new_doc = Doc(en_vocab, words=words)
    new_doc.from_array(attrs, arr)
    assert [t.is_sent_start for t in doc] == [t.is_sent_start for t in new_doc]
    assert new_doc.has_annotation("DEP")


def test_doc_from_array_morph(en_vocab):
    # fmt: off
    words = ["I", "live", "in", "New", "York", "."]
    morphs = ["Feat1=A", "Feat1=B", "Feat1=C", "Feat1=A|Feat2=D", "Feat2=E", "Feat3=F"]
    # fmt: on
    doc = Doc(en_vocab, words=words, morphs=morphs)
    attrs = [MORPH]
    arr = doc.to_array(attrs)
    new_doc = Doc(en_vocab, words=words)
    new_doc.from_array(attrs, arr)
    assert [str(t.morph) for t in new_doc] == morphs
    assert [str(t.morph) for t in doc] == [str(t.morph) for t in new_doc]


@pytest.mark.usefixtures("clean_underscore")
def test_doc_api_from_docs(en_tokenizer, de_tokenizer):
    en_texts = [
        "Merging the docs is fun.",
        "",
        "They don't think alike. ",
        "",
        "Another doc.",
    ]
    en_texts_without_empty = [t for t in en_texts if len(t)]
    de_text = "Wie war die Frage?"
    en_docs = [en_tokenizer(text) for text in en_texts]
    en_docs[0].spans["group"] = [en_docs[0][1:4]]
    en_docs[2].spans["group"] = [en_docs[2][1:4]]
    en_docs[4].spans["group"] = [en_docs[4][0:1]]
    span_group_texts = sorted(
        [en_docs[0][1:4].text, en_docs[2][1:4].text, en_docs[4][0:1].text]
    )
    de_doc = de_tokenizer(de_text)
    Token.set_extension("is_ambiguous", default=False)
    en_docs[0][2]._.is_ambiguous = True  # docs
    en_docs[2][3]._.is_ambiguous = True  # think
    assert Doc.from_docs([]) is None
    assert de_doc is not Doc.from_docs([de_doc])
    assert str(de_doc) == str(Doc.from_docs([de_doc]))

    with pytest.raises(ValueError):
        Doc.from_docs(en_docs + [de_doc])

    m_doc = Doc.from_docs(en_docs)
    assert len(en_texts_without_empty) == len(list(m_doc.sents))
    assert len(m_doc.text) > len(en_texts[0]) + len(en_texts[1])
    assert m_doc.text == " ".join([t.strip() for t in en_texts_without_empty])
    p_token = m_doc[len(en_docs[0]) - 1]
    assert p_token.text == "." and bool(p_token.whitespace_)
    en_docs_tokens = [t for doc in en_docs for t in doc]
    assert len(m_doc) == len(en_docs_tokens)
    think_idx = len(en_texts[0]) + 1 + en_texts[2].index("think")
    assert m_doc[2]._.is_ambiguous is True
    assert m_doc[9].idx == think_idx
    assert m_doc[9]._.is_ambiguous is True
    assert not any([t._.is_ambiguous for t in m_doc[3:8]])
    assert "group" in m_doc.spans
    assert span_group_texts == sorted([s.text for s in m_doc.spans["group"]])
    assert bool(m_doc[11].whitespace_)

    m_doc = Doc.from_docs(en_docs, ensure_whitespace=False)
    assert len(en_texts_without_empty) == len(list(m_doc.sents))
    assert len(m_doc.text) == sum(len(t) for t in en_texts)
    assert m_doc.text == "".join(en_texts_without_empty)
    p_token = m_doc[len(en_docs[0]) - 1]
    assert p_token.text == "." and not bool(p_token.whitespace_)
    en_docs_tokens = [t for doc in en_docs for t in doc]
    assert len(m_doc) == len(en_docs_tokens)
    think_idx = len(en_texts[0]) + 0 + en_texts[2].index("think")
    assert m_doc[9].idx == think_idx
    assert "group" in m_doc.spans
    assert span_group_texts == sorted([s.text for s in m_doc.spans["group"]])
    assert bool(m_doc[11].whitespace_)

    m_doc = Doc.from_docs(en_docs, attrs=["lemma", "length", "pos"])
    assert len(m_doc.text) > len(en_texts[0]) + len(en_texts[1])
    # space delimiter considered, although spacy attribute was missing
    assert m_doc.text == " ".join([t.strip() for t in en_texts_without_empty])
    p_token = m_doc[len(en_docs[0]) - 1]
    assert p_token.text == "." and bool(p_token.whitespace_)
    en_docs_tokens = [t for doc in en_docs for t in doc]
    assert len(m_doc) == len(en_docs_tokens)
    think_idx = len(en_texts[0]) + 1 + en_texts[2].index("think")
    assert m_doc[9].idx == think_idx
    assert "group" in m_doc.spans
    assert span_group_texts == sorted([s.text for s in m_doc.spans["group"]])

    # can exclude spans
    m_doc = Doc.from_docs(en_docs, exclude=["spans"])
    assert "group" not in m_doc.spans

    # can exclude user_data
    m_doc = Doc.from_docs(en_docs, exclude=["user_data"])
    assert m_doc.user_data == {}

    # can merge empty docs
    doc = Doc.from_docs([en_tokenizer("")] * 10)

    # empty but set spans keys are preserved
    en_docs = [en_tokenizer(text) for text in en_texts]
    m_doc = Doc.from_docs(en_docs)
    assert "group" not in m_doc.spans
    for doc in en_docs:
        doc.spans["group"] = []
    m_doc = Doc.from_docs(en_docs)
    assert "group" in m_doc.spans
    assert len(m_doc.spans["group"]) == 0

    # with tensor
    ops = get_current_ops()
    for doc in en_docs:
        doc.tensor = ops.asarray([[len(t.text), 0.0] for t in doc])
    m_doc = Doc.from_docs(en_docs)
    assert_array_equal(
        ops.to_numpy(m_doc.tensor),
        ops.to_numpy(ops.xp.vstack([doc.tensor for doc in en_docs if len(doc)])),
    )

    # can exclude tensor
    m_doc = Doc.from_docs(en_docs, exclude=["tensor"])
    assert m_doc.tensor.shape == (0,)


def test_doc_api_from_docs_ents(en_tokenizer):
    texts = ["Merging the docs is fun.", "They don't think alike."]
    docs = [en_tokenizer(t) for t in texts]
    docs[0].ents = ()
    docs[1].ents = (Span(docs[1], 0, 1, label="foo"),)
    doc = Doc.from_docs(docs)
    assert len(doc.ents) == 1


def test_doc_lang(en_vocab):
    doc = Doc(en_vocab, words=["Hello", "world"])
    assert doc.lang_ == "en"
    assert doc.lang == en_vocab.strings["en"]
    assert doc[0].lang_ == "en"
    assert doc[0].lang == en_vocab.strings["en"]
    nlp = English()
    doc = nlp("Hello world")
    assert doc.lang_ == "en"
    assert doc.lang == en_vocab.strings["en"]
    assert doc[0].lang_ == "en"
    assert doc[0].lang == en_vocab.strings["en"]


def test_token_lexeme(en_vocab):
    """Test that tokens expose their lexeme."""
    token = Doc(en_vocab, words=["Hello", "world"])[0]
    assert isinstance(token.lex, Lexeme)
    assert token.lex.text == token.text
    assert en_vocab[token.orth] == token.lex


def test_has_annotation(en_vocab):
    doc = Doc(en_vocab, words=["Hello", "world"])
    attrs = ("TAG", "POS", "MORPH", "LEMMA", "DEP", "HEAD", "ENT_IOB", "ENT_TYPE")
    for attr in attrs:
        assert not doc.has_annotation(attr)
        assert not doc.has_annotation(attr, require_complete=True)

    doc[0].tag_ = "A"
    doc[0].pos_ = "X"
    doc[0].set_morph("Feat=Val")
    doc[0].lemma_ = "a"
    doc[0].dep_ = "dep"
    doc[0].head = doc[1]
    doc.set_ents([Span(doc, 0, 1, label="HELLO")], default="missing")

    for attr in attrs:
        assert doc.has_annotation(attr)
        assert not doc.has_annotation(attr, require_complete=True)

    doc[1].tag_ = "A"
    doc[1].pos_ = "X"
    doc[1].set_morph("")
    doc[1].lemma_ = "a"
    doc[1].dep_ = "dep"
    doc.ents = [Span(doc, 0, 2, label="HELLO")]

    for attr in attrs:
        assert doc.has_annotation(attr)
        assert doc.has_annotation(attr, require_complete=True)


def test_has_annotation_sents(en_vocab):
    doc = Doc(en_vocab, words=["Hello", "beautiful", "world"])
    attrs = ("SENT_START", "IS_SENT_START", "IS_SENT_END")
    for attr in attrs:
        assert not doc.has_annotation(attr)
        assert not doc.has_annotation(attr, require_complete=True)

    # The first token (index 0) is always assumed to be a sentence start,
    # and ignored by the check in doc.has_annotation

    doc[1].is_sent_start = False
    for attr in attrs:
        assert doc.has_annotation(attr)
        assert not doc.has_annotation(attr, require_complete=True)

    doc[2].is_sent_start = False
    for attr in attrs:
        assert doc.has_annotation(attr)
        assert doc.has_annotation(attr, require_complete=True)


def test_is_flags_deprecated(en_tokenizer):
    doc = en_tokenizer("test")
    with pytest.deprecated_call():
        doc.is_tagged
    with pytest.deprecated_call():
        doc.is_parsed
    with pytest.deprecated_call():
        doc.is_nered
    with pytest.deprecated_call():
        doc.is_sentenced


def test_doc_set_ents(en_tokenizer):
    # set ents
    doc = en_tokenizer("a b c d e")
    doc.set_ents([Span(doc, 0, 1, 10), Span(doc, 1, 3, 11)])
    assert [t.ent_iob for t in doc] == [3, 3, 1, 2, 2]
    assert [t.ent_type for t in doc] == [10, 11, 11, 0, 0]

    # add ents, invalid IOB repaired
    doc = en_tokenizer("a b c d e")
    doc.set_ents([Span(doc, 0, 1, 10), Span(doc, 1, 3, 11)])
    doc.set_ents([Span(doc, 0, 2, 12)], default="unmodified")
    assert [t.ent_iob for t in doc] == [3, 1, 3, 2, 2]
    assert [t.ent_type for t in doc] == [12, 12, 11, 0, 0]

    # missing ents
    doc = en_tokenizer("a b c d e")
    doc.set_ents([Span(doc, 0, 1, 10), Span(doc, 1, 3, 11)], missing=[doc[4:5]])
    assert [t.ent_iob for t in doc] == [3, 3, 1, 2, 0]
    assert [t.ent_type for t in doc] == [10, 11, 11, 0, 0]

    # outside ents
    doc = en_tokenizer("a b c d e")
    doc.set_ents(
        [Span(doc, 0, 1, 10), Span(doc, 1, 3, 11)],
        outside=[doc[4:5]],
        default="missing",
    )
    assert [t.ent_iob for t in doc] == [3, 3, 1, 0, 2]
    assert [t.ent_type for t in doc] == [10, 11, 11, 0, 0]

    # blocked ents
    doc = en_tokenizer("a b c d e")
    doc.set_ents([], blocked=[doc[1:2], doc[3:5]], default="unmodified")
    assert [t.ent_iob for t in doc] == [0, 3, 0, 3, 3]
    assert [t.ent_type for t in doc] == [0, 0, 0, 0, 0]
    assert doc.ents == tuple()

    # invalid IOB repaired after blocked
    doc.ents = [Span(doc, 3, 5, "ENT")]
    assert [t.ent_iob for t in doc] == [2, 2, 2, 3, 1]
    doc.set_ents([], blocked=[doc[3:4]], default="unmodified")
    assert [t.ent_iob for t in doc] == [2, 2, 2, 3, 3]

    # all types
    doc = en_tokenizer("a b c d e")
    doc.set_ents(
        [Span(doc, 0, 1, 10)],
        blocked=[doc[1:2]],
        missing=[doc[2:3]],
        outside=[doc[3:4]],
        default="unmodified",
    )
    assert [t.ent_iob for t in doc] == [3, 3, 0, 2, 0]
    assert [t.ent_type for t in doc] == [10, 0, 0, 0, 0]

    doc = en_tokenizer("a b c d e")
    # single span instead of a list
    with pytest.raises(ValueError):
        doc.set_ents([], missing=doc[1:2])
    # invalid default mode
    with pytest.raises(ValueError):
        doc.set_ents([], missing=[doc[1:2]], default="none")
    # conflicting/overlapping specifications
    with pytest.raises(ValueError):
        doc.set_ents([], missing=[doc[1:2]], outside=[doc[1:2]])


def test_doc_ents_setter():
    """Test that both strings and integers can be used to set entities in
    tuple format via doc.ents."""
    words = ["a", "b", "c", "d", "e"]
    doc = Doc(Vocab(), words=words)
    doc.ents = [("HELLO", 0, 2), (doc.vocab.strings.add("WORLD"), 3, 5)]
    assert [e.label_ for e in doc.ents] == ["HELLO", "WORLD"]
    vocab = Vocab()
    ents = [("HELLO", 0, 2), (vocab.strings.add("WORLD"), 3, 5)]
    ents = ["B-HELLO", "I-HELLO", "O", "B-WORLD", "I-WORLD"]
    doc = Doc(vocab, words=words, ents=ents)
    assert [e.label_ for e in doc.ents] == ["HELLO", "WORLD"]


def test_doc_morph_setter(en_tokenizer, de_tokenizer):
    doc1 = en_tokenizer("a b")
    doc1b = en_tokenizer("c d")
    doc2 = de_tokenizer("a b")

    # unset values can be copied
    doc1[0].morph = doc1[1].morph
    assert doc1[0].morph.key == 0
    assert doc1[1].morph.key == 0

    # morph values from the same vocab can be copied
    doc1[0].set_morph("Feat=Val")
    doc1[1].morph = doc1[0].morph
    assert doc1[0].morph == doc1[1].morph

    # ... also across docs
    doc1b[0].morph = doc1[0].morph
    assert doc1[0].morph == doc1b[0].morph

    doc2[0].set_morph("Feat2=Val2")

    # the morph value must come from the same vocab
    with pytest.raises(ValueError):
        doc1[0].morph = doc2[0].morph


def test_doc_init_iob():
    """Test ents validation/normalization in Doc.__init__"""
    words = ["a", "b", "c", "d", "e"]
    ents = ["O"] * len(words)
    doc = Doc(Vocab(), words=words, ents=ents)
    assert doc.ents == ()

    ents = ["B-PERSON", "I-PERSON", "O", "I-PERSON", "I-PERSON"]
    doc = Doc(Vocab(), words=words, ents=ents)
    assert len(doc.ents) == 2

    ents = ["B-PERSON", "I-PERSON", "O", "I-PERSON", "I-GPE"]
    doc = Doc(Vocab(), words=words, ents=ents)
    assert len(doc.ents) == 3

    # None is missing
    ents = ["B-PERSON", "I-PERSON", "O", None, "I-GPE"]
    doc = Doc(Vocab(), words=words, ents=ents)
    assert len(doc.ents) == 2

    # empty tag is missing
    ents = ["", "B-PERSON", "O", "B-PERSON", "I-PERSON"]
    doc = Doc(Vocab(), words=words, ents=ents)
    assert len(doc.ents) == 2

    # invalid IOB
    ents = ["Q-PERSON", "I-PERSON", "O", "I-PERSON", "I-GPE"]
    with pytest.raises(ValueError):
        doc = Doc(Vocab(), words=words, ents=ents)

    # no dash
    ents = ["OPERSON", "I-PERSON", "O", "I-PERSON", "I-GPE"]
    with pytest.raises(ValueError):
        doc = Doc(Vocab(), words=words, ents=ents)

    # no ent type
    ents = ["O", "B-", "O", "I-PERSON", "I-GPE"]
    with pytest.raises(ValueError):
        doc = Doc(Vocab(), words=words, ents=ents)

    # not strings or None
    ents = [0, "B-", "O", "I-PERSON", "I-GPE"]
    with pytest.raises(ValueError):
        doc = Doc(Vocab(), words=words, ents=ents)


def test_doc_set_ents_invalid_spans(en_tokenizer):
    doc = en_tokenizer("Some text about Colombia and the Czech Republic")
    spans = [Span(doc, 3, 4, label="GPE"), Span(doc, 6, 8, label="GPE")]
    with doc.retokenize() as retokenizer:
        for span in spans:
            retokenizer.merge(span)
    with pytest.raises(IndexError):
        doc.ents = spans


def test_doc_noun_chunks_not_implemented():
    """Test that a language without noun_chunk iterator, throws a NotImplementedError"""
    text = "Může data vytvářet a spravovat, ale především je dokáže analyzovat, najít v nich nové vztahy a vše přehledně vizualizovat."
    nlp = MultiLanguage()
    doc = nlp(text)
    with pytest.raises(NotImplementedError):
        _ = list(doc.noun_chunks)  # noqa: F841


def test_span_groups(en_tokenizer):
    doc = en_tokenizer("Some text about Colombia and the Czech Republic")
    doc.spans["hi"] = [Span(doc, 3, 4, label="bye")]
    assert "hi" in doc.spans
    assert "bye" not in doc.spans
    assert len(doc.spans["hi"]) == 1
    assert doc.spans["hi"][0].label_ == "bye"
    doc.spans["hi"].append(doc[0:3])
    assert len(doc.spans["hi"]) == 2
    assert doc.spans["hi"][1].text == "Some text about"
    assert [span.text for span in doc.spans["hi"]] == ["Colombia", "Some text about"]
    assert not doc.spans["hi"].has_overlap
    doc.ents = [Span(doc, 3, 4, label="GPE"), Span(doc, 6, 8, label="GPE")]
    doc.spans["hi"].extend(doc.ents)
    assert len(doc.spans["hi"]) == 4
    assert [span.label_ for span in doc.spans["hi"]] == ["bye", "", "GPE", "GPE"]
    assert doc.spans["hi"].has_overlap
    del doc.spans["hi"]
    assert "hi" not in doc.spans


def test_doc_spans_copy(en_tokenizer):
    doc1 = en_tokenizer("Some text about Colombia and the Czech Republic")
    assert weakref.ref(doc1) == doc1.spans.doc_ref
    doc2 = doc1.copy()
    assert weakref.ref(doc2) == doc2.spans.doc_ref


def test_doc_spans_setdefault(en_tokenizer):
    doc = en_tokenizer("Some text about Colombia and the Czech Republic")
    doc.spans.setdefault("key1")
    assert len(doc.spans["key1"]) == 0
    doc.spans.setdefault("key2", default=[doc[0:1]])
    assert len(doc.spans["key2"]) == 1
    doc.spans.setdefault("key3", default=SpanGroup(doc, spans=[doc[0:1], doc[1:2]]))
    assert len(doc.spans["key3"]) == 2


EMPTY_HASH_VALUE = 0x811C9DC5


def test_fnv1a_hash():
    """Checks the conformity of the FNV1A implementation with
    http://www.isthe.com/chongo/src/fnv/test_fnv.c.
    The method called here is only used in testing; in production
    code, the hashing is performed in a fashion that is interweaved
    with other logic. The conformity of the production code is
    demonstrated by the character combination hash tests, where
    hashes produced by the production code are tested for equality
    against hashes prodduced by the test code.
    s"""
    INPUTS = [
        b"",
        b"a",
        b"b",
        b"c",
        b"d",
        b"e",
        b"f",
        b"fo",
        b"foo",
        b"foob",
        b"fooba",
        b"foobar",
        b"\x00",
        b"a\x00",
        b"b\x00",
        b"c\x00",
        b"d\x00",
        b"e\x00",
        b"f\x00",
        b"fo\x00",
        b"foo\x00",
        b"foob\x00",
        b"fooba\x00",
        b"foobar\x00",
        b"ch",
        b"cho",
        b"chon",
        b"chong",
        b"chongo",
        b"chongo ",
        b"chongo w",
        b"chongo wa",
        b"chongo was",
        b"chongo was ",
        b"chongo was h",
        b"chongo was he",
        b"chongo was her",
        b"chongo was here",
        b"chongo was here!",
        b"chongo was here!\n",
        b"ch\x00",
        b"cho\x00",
        b"chon\x00",
        b"chong\x00",
        b"chongo\x00",
        b"chongo \x00",
        b"chongo w\x00",
        b"chongo wa\x00",
        b"chongo was\x00",
        b"chongo was \x00",
        b"chongo was h\x00",
        b"chongo was he\x00",
        b"chongo was her\x00",
        b"chongo was here\x00",
        b"chongo was here!\x00",
        b"chongo was here!\n\x00",
        b"cu",
        b"cur",
        b"curd",
        b"curds",
        b"curds ",
        b"curds a",
        b"curds an",
        b"curds and",
        b"curds and ",
        b"curds and w",
        b"curds and wh",
        b"curds and whe",
        b"curds and whey",
        b"curds and whey\n",
        b"cu\x00",
        b"cur\x00",
        b"curd\x00",
        b"curds\x00",
        b"curds \x00",
        b"curds a\x00",
        b"curds an\x00",
        b"curds and\x00",
        b"curds and \x00",
        b"curds and w\x00",
        b"curds and wh\x00",
        b"curds and whe\x00",
        b"curds and whey\x00",
        b"curds and whey\n\x00",
        b"hi",
        b"hi\x00",
        b"hello",
        b"hello\x00",
        b"\xff\x00\x00\x01",
        b"\x01\x00\x00\xff",
        b"\xff\x00\x00\x02",
        b"\x02\x00\x00\xff",
        b"\xff\x00\x00\x03",
        b"\x03\x00\x00\xff",
        b"\xff\x00\x00\x04",
        b"\x04\x00\x00\xff",
        b"\x40\x51\x4e\x44",
        b"\x44\x4e\x51\x40",
        b"\x40\x51\x4e\x4a",
        b"\x4a\x4e\x51\x40",
        b"\x40\x51\x4e\x54",
        b"\x54\x4e\x51\x40",
        b"127.0.0.1",
        b"127.0.0.1\x00",
        b"127.0.0.2",
        b"127.0.0.2\x00",
        b"127.0.0.3",
        b"127.0.0.3\x00",
        b"64.81.78.68",
        b"64.81.78.68\x00",
        b"64.81.78.74",
        b"64.81.78.74\x00",
        b"64.81.78.84",
        b"64.81.78.84\x00",
        b"feedface",
        b"feedface\x00",
        b"feedfacedaffdeed",
        b"feedfacedaffdeed\x00",
        b"feedfacedeadbeef",
        b"feedfacedeadbeef\x00",
        b"line 1\nline 2\nline 3",
        b"chongo <Landon Curt Noll> /\\../\\",
        b"chongo <Landon Curt Noll> /\\../\\\x00",
        b"chongo (Landon Curt Noll) /\\../\\",
        b"chongo (Landon Curt Noll) /\\../\\\x00",
        b"http://antwrp.gsfc.nasa.gov/apod/astropix.html",
        b"http://en.wikipedia.org/wiki/Fowler_Noll_Vo_hash",
        b"http://epod.usra.edu/",
        b"http://exoplanet.eu/",
        b"http://hvo.wr.usgs.gov/cam3/",
        b"http://hvo.wr.usgs.gov/cams/HMcam/",
        b"http://hvo.wr.usgs.gov/kilauea/update/deformation.html",
        b"http://hvo.wr.usgs.gov/kilauea/update/images.html",
        b"http://hvo.wr.usgs.gov/kilauea/update/maps.html",
        b"http://hvo.wr.usgs.gov/volcanowatch/current_issue.html",
        b"http://neo.jpl.nasa.gov/risk/",
        b"http://norvig.com/21-days.html",
        b"http://primes.utm.edu/curios/home.php",
        b"http://slashdot.org/",
        b"http://tux.wr.usgs.gov/Maps/155.25-19.5.html",
        b"http://volcano.wr.usgs.gov/kilaueastatus.php",
        b"http://www.avo.alaska.edu/activity/Redoubt.php",
        b"http://www.dilbert.com/fast/",
        b"http://www.fourmilab.ch/gravitation/orbits/",
        b"http://www.fpoa.net/",
        b"http://www.ioccc.org/index.html",
        b"http://www.isthe.com/cgi-bin/number.cgi",
        b"http://www.isthe.com/chongo/bio.html",
        b"http://www.isthe.com/chongo/index.html",
        b"http://www.isthe.com/chongo/src/calc/lucas-calc",
        b"http://www.isthe.com/chongo/tech/astro/venus2004.html",
        b"http://www.isthe.com/chongo/tech/astro/vita.html",
        b"http://www.isthe.com/chongo/tech/comp/c/expert.html",
        b"http://www.isthe.com/chongo/tech/comp/calc/index.html",
        b"http://www.isthe.com/chongo/tech/comp/fnv/index.html",
        b"http://www.isthe.com/chongo/tech/math/number/howhigh.html",
        b"http://www.isthe.com/chongo/tech/math/number/number.html",
        b"http://www.isthe.com/chongo/tech/math/prime/mersenne.html",
        b"http://www.isthe.com/chongo/tech/math/prime/mersenne.html#largest",
        b"http://www.lavarnd.org/cgi-bin/corpspeak.cgi",
        b"http://www.lavarnd.org/cgi-bin/haiku.cgi",
        b"http://www.lavarnd.org/cgi-bin/rand-none.cgi",
        b"http://www.lavarnd.org/cgi-bin/randdist.cgi",
        b"http://www.lavarnd.org/index.html",
        b"http://www.lavarnd.org/what/nist-test.html",
        b"http://www.macosxhints.com/",
        b"http://www.mellis.com/",
        b"http://www.nature.nps.gov/air/webcams/parks/havoso2alert/havoalert.cfm",
        b"http://www.nature.nps.gov/air/webcams/parks/havoso2alert/timelines_24.cfm",
        b"http://www.paulnoll.com/",
        b"http://www.pepysdiary.com/",
        b"http://www.sciencenews.org/index/home/activity/view",
        b"http://www.skyandtelescope.com/",
        b"http://www.sput.nl/~rob/sirius.html",
        b"http://www.systemexperts.com/",
        b"http://www.tq-international.com/phpBB3/index.php",
        b"http://www.travelquesttours.com/index.htm",
        b"http://www.wunderground.com/global/stations/89606.html",
        b"21701" * 10,
        b"M21701" * 10,
        b"2^21701-1" * 10,
        b"\x54\xc5" * 10,
        b"\xc5\x54" * 10,
        b"23209" * 10,
        b"M23209" * 10,
        b"2^23209-1" * 10,
        b"\x5a\xa9" * 10,
        b"\xa9\x5a" * 10,
        b"391581216093" * 10,
        b"391581*2^216093-1" * 10,
        b"\x05\xf9\x9d\x03\x4c\x81" * 10,
        b"FEDCBA9876543210" * 10,
        b"\xfe\xdc\xba\x98\x76\x54\x32\x10" * 10,
        b"EFCDAB8967452301" * 10,
        b"\xef\xcd\xab\x89\x67\x45\x23\x01" * 10,
        b"0123456789ABCDEF" * 10,
        b"\x01\x23\x45\x67\x89\xab\xcd\xef" * 10,
        b"1032547698BADCFE" * 10,
        b"\x10\x32\x54\x76\x98\xba\xdc\xfe" * 10,
        b"\x00" * 500,
        b"\x07" * 500,
        b"~" * 500,
        b"\x7f" * 500,
    ]

    OUTPUTS = [
        EMPTY_HASH_VALUE,
        0xE40C292C,
        0xE70C2DE5,
        0xE60C2C52,
        0xE10C2473,
        0xE00C22E0,
        0xE30C2799,
        0x6222E842,
        0xA9F37ED7,
        0x3F5076EF,
        0x39AAA18A,
        0xBF9CF968,
        0x050C5D1F,
        0x2B24D044,
        0x9D2C3F7F,
        0x7729C516,
        0xB91D6109,
        0x931AE6A0,
        0x052255DB,
        0xBEF39FE6,
        0x6150AC75,
        0x9AAB3A3D,
        0x519C4C3E,
        0x0C1C9EB8,
        0x5F299F4E,
        0xEF8580F3,
        0xAC297727,
        0x4546B9C0,
        0xBD564E7D,
        0x6BDD5C67,
        0xDD77ED30,
        0xF4CA9683,
        0x4AEB9BD0,
        0xE0E67AD0,
        0xC2D32FA8,
        0x7F743FB7,
        0x6900631F,
        0xC59C990E,
        0x448524FD,
        0xD49930D5,
        0x1C85C7CA,
        0x0229FE89,
        0x2C469265,
        0xCE566940,
        0x8BDD8EC7,
        0x34787625,
        0xD3CA6290,
        0xDDEAF039,
        0xC0E64870,
        0xDAD35570,
        0x5A740578,
        0x5B004D15,
        0x6A9C09CD,
        0x2384F10A,
        0xDA993A47,
        0x8227DF4F,
        0x4C298165,
        0xFC563735,
        0x8CB91483,
        0x775BF5D0,
        0xD5C428D0,
        0x34CC0EA3,
        0xEA3B4CB7,
        0x8E59F029,
        0x2094DE2B,
        0xA65A0AD4,
        0x9BBEE5F4,
        0xBE836343,
        0x22D5344E,
        0x19A1470C,
        0x4A56B1FF,
        0x70B8E86F,
        0x0A5B4A39,
        0xB5C3F670,
        0x53CC3F70,
        0xC03B0A99,
        0x7259C415,
        0x4095108B,
        0x7559BDB1,
        0xB3BF0BBC,
        0x2183FF1C,
        0x2BD54279,
        0x23A156CA,
        0x64E2D7E4,
        0x683AF69A,
        0xAED2346E,
        0x4F9F2CAB,
        0x02935131,
        0xC48FB86D,
        0x2269F369,
        0xC18FB3B4,
        0x50EF1236,
        0xC28FB547,
        0x96C3BF47,
        0xBF8FB08E,
        0xF3E4D49C,
        0x32179058,
        0x280BFEE6,
        0x30178D32,
        0x21ADDAF8,
        0x4217A988,
        0x772633D6,
        0x08A3D11E,
        0xB7E2323A,
        0x07A3CF8B,
        0x91DFB7D1,
        0x06A3CDF8,
        0x6BDD3D68,
        0x1D5636A7,
        0xD5B808E5,
        0x1353E852,
        0xBF16B916,
        0xA55B89ED,
        0x3C1A2017,
        0x0588B13C,
        0xF22F0174,
        0xE83641E1,
        0x6E69B533,
        0xF1760448,
        0x64C8BD58,
        0x97B4EA23,
        0x9A4E92E6,
        0xCFB14012,
        0xF01B2511,
        0x0BBB59C3,
        0xCE524AFA,
        0xDD16EF45,
        0x60648BB3,
        0x7FA4BCFC,
        0x5053AE17,
        0xC9302890,
        0x956DED32,
        0x9136DB84,
        0xDF9D3323,
        0x32BB6CD0,
        0xC8F8385B,
        0xEB08BFBA,
        0x62CC8E3D,
        0xC3E20F5C,
        0x39E97F17,
        0x7837B203,
        0x319E877B,
        0xD3E63F89,
        0x29B50B38,
        0x5ED678B8,
        0xB0D5B793,
        0x52450BE5,
        0xFA72D767,
        0x95066709,
        0x7F52E123,
        0x76966481,
        0x063258B0,
        0x2DED6E8A,
        0xB07D7C52,
        0xD0C71B71,
        0xF684F1BD,
        0x868ECFA8,
        0xF794F684,
        0xD19701C3,
        0x346E171E,
        0x91F8F676,
        0x0BF58848,
        0x6317B6D1,
        0xAFAD4C54,
        0x0F25681E,
        0x91B18D49,
        0x7D61C12E,
        0x5147D25C,
        0x9A8B6805,
        0x4CD2A447,
        0x1E549B14,
        0x2FE1B574,
        0xCF0CD31E,
        0x6C471669,
        0x0E5EEF1E,
        0x2BED3602,
        0xB26249E0,
        0x2C9B86A4,
        0xE415E2BB,
        0x18A98D1D,
        0xB7DF8B7B,
        0x241E9075,
        0x063F70DD,
        0x0295AED9,
        0x56A7F781,
        0x253BC645,
        0x46610921,
        0x7C1577F9,
        0x512B2851,
        0x76823999,
        0xC0586935,
        0xF3415C85,
        0x0AE4FF65,
        0x58B79725,
        0xDEA43AA5,
        0x2BB3BE35,
        0xEA777A45,
        0x8F21C305,
        0x5C9D0865,
        0xFA823DD5,
        0x21A27271,
        0x83C5C6D5,
        0x813B0881,
    ]

    assert len(INPUTS) == len(OUTPUTS)
    for i in range(len(INPUTS)):
        assert get_fnv1a_hash(INPUTS[i]) == OUTPUTS[i]


def _encode_and_hash(input: str, *, reverse: bool = False) -> int:
    encoded_input = input.encode("UTF-8")
    if reverse:
        encoded_input = encoded_input[::-1]
    return get_fnv1a_hash(encoded_input)


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_character_combination_hashes_good_case(en_tokenizer, case_sensitive):
    doc = en_tokenizer("spaCy✨ and Prodigy")

    ps_search_chars, ps_width_offsets = get_search_char_byte_arrays(
        "Rp", case_sensitive
    )
    ss_search_chars, ss_width_offsets = get_search_char_byte_arrays(
        "xx✨rp", case_sensitive
    )
    hashes = doc.get_character_combination_hashes(
        cs=case_sensitive,
        p_lengths=bytes(
            (
                1,
                3,
                4,
            )
        ),
        s_lengths=bytes(
            (
                2,
                3,
                4,
                5,
            )
        ),
        ps_search_chars=ps_search_chars,
        ps_width_offsets=ps_width_offsets,
        ps_lengths=bytes((2,)),
        ss_search_chars=ss_search_chars,
        ss_width_offsets=ss_width_offsets,
        ss_lengths=bytes(
            (
                1,
                2,
            )
        ),
    )
    assert hashes[0][0] == _encode_and_hash("s")
    assert hashes[0][1] == _encode_and_hash("spa")
    assert hashes[0][2] == _encode_and_hash("spaC" if case_sensitive else "spac")
    assert hashes[0][3] == _encode_and_hash("yC" if case_sensitive else "yc")
    assert hashes[0][4] == _encode_and_hash("yCa" if case_sensitive else "yca")
    assert hashes[0][5] == _encode_and_hash("yCap" if case_sensitive else "ycap")
    assert hashes[0][6] == _encode_and_hash("yCaps" if case_sensitive else "ycaps")
    assert hashes[0][7] == _encode_and_hash("p")
    assert hashes[0][8] == _encode_and_hash("p")
    assert hashes[0][9] == _encode_and_hash("p")
    assert hashes[1][0] == _encode_and_hash("✨")
    assert hashes[1][1] == _encode_and_hash("✨")
    assert hashes[1][2] == _encode_and_hash("✨")
    assert hashes[1][3] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][4] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][5] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][6] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][7] == EMPTY_HASH_VALUE
    assert hashes[1][8] == _encode_and_hash("✨")
    assert hashes[1][9] == _encode_and_hash("✨")
    assert hashes[2][0] == _encode_and_hash("a")
    assert hashes[2][1] == _encode_and_hash("and")
    assert hashes[2][2] == _encode_and_hash("and")
    assert hashes[2][3] == _encode_and_hash("dn")
    assert hashes[2][4] == _encode_and_hash("dna")
    assert hashes[2][5] == _encode_and_hash("dna")
    assert hashes[2][6] == _encode_and_hash("dna")
    assert hashes[2][7] == EMPTY_HASH_VALUE
    assert hashes[2][8] == EMPTY_HASH_VALUE
    assert hashes[2][9] == EMPTY_HASH_VALUE
    assert hashes[3][0] == _encode_and_hash("P" if case_sensitive else "p")
    assert hashes[3][1] == _encode_and_hash("Pro" if case_sensitive else "pro")
    assert hashes[3][2] == _encode_and_hash("Prod" if case_sensitive else "prod")
    assert hashes[3][3] == _encode_and_hash("yg")
    assert hashes[3][4] == _encode_and_hash("ygi")
    assert hashes[3][5] == _encode_and_hash("ygid")
    assert hashes[3][6] == _encode_and_hash("ygido")
    assert (
        hashes[3][7] == EMPTY_HASH_VALUE if case_sensitive else _encode_and_hash("pr")
    )

    assert hashes[3][8] == _encode_and_hash("r")

    if case_sensitive:
        assert hashes[3][9] == _encode_and_hash("r")
    else:
        assert hashes[3][9] == _encode_and_hash("rp")


def test_get_character_combination_hashes_good_case_partial(en_tokenizer):
    doc = en_tokenizer("spaCy✨ and Prodigy")
    ps_search_chars, ps_width_offsets = get_search_char_byte_arrays("rp", False)
    hashes = doc.get_character_combination_hashes(
        cs=False,
        p_lengths=bytes(),
        s_lengths=bytes(
            (
                2,
                3,
                4,
                5,
            )
        ),
        ps_search_chars=ps_search_chars,
        ps_width_offsets=ps_width_offsets,
        ps_lengths=bytes((2,)),
        ss_search_chars=bytes(),
        ss_width_offsets=bytes(),
        ss_lengths=bytes(),
    )

    assert hashes[0][0] == _encode_and_hash("yc")
    assert hashes[0][1] == _encode_and_hash("yca")
    assert hashes[0][2] == _encode_and_hash("ycap")
    assert hashes[0][3] == _encode_and_hash("ycaps")
    assert hashes[0][4] == _encode_and_hash("p")
    assert hashes[1][0] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][1] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][2] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][3] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][4] == EMPTY_HASH_VALUE
    assert hashes[2][0] == _encode_and_hash("dn")
    assert hashes[2][1] == _encode_and_hash("dna")
    assert hashes[2][2] == _encode_and_hash("dna")
    assert hashes[2][3] == _encode_and_hash("dna")
    assert hashes[2][4] == EMPTY_HASH_VALUE
    assert hashes[3][0] == _encode_and_hash("yg")
    assert hashes[3][1] == _encode_and_hash("ygi")
    assert hashes[3][2] == _encode_and_hash("ygid")
    assert hashes[3][3] == _encode_and_hash("ygido")
    assert hashes[3][4] == _encode_and_hash("pr")


def test_get_character_combination_hashes_copying_in_middle(en_tokenizer):
    doc = en_tokenizer("sp𐌞Cé")

    for p_length in range(1, 8):
        for s_length in range(1, 8):

            hashes = doc.get_character_combination_hashes(
                cs=False,
                p_lengths=bytes((p_length,)),
                s_lengths=bytes((s_length,)),
                ps_search_chars=bytes(),
                ps_width_offsets=bytes(),
                ps_lengths=bytes(),
                ss_search_chars=bytes(),
                ss_width_offsets=bytes(),
                ss_lengths=bytes(),
            )

            assert hashes[0][0] == _encode_and_hash("sp𐌞cé"[:p_length])
            assert hashes[0][1] == _encode_and_hash("sp𐌞cé"[-s_length:], reverse=True)


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_character_combination_hashes_turkish_i_with_dot(
    en_tokenizer, case_sensitive
):
    doc = en_tokenizer("İ".lower() + "İ")
    search_chars, width_offsets = get_search_char_byte_arrays("İ", case_sensitive)
    hashes = doc.get_character_combination_hashes(
        cs=case_sensitive,
        p_lengths=bytes(
            (
                1,
                2,
                3,
                4,
            )
        ),
        s_lengths=bytes(
            (
                1,
                2,
                3,
                4,
            )
        ),
        ps_search_chars=search_chars,
        ps_width_offsets=width_offsets,
        ps_lengths=bytes(
            (
                1,
                2,
                3,
                4,
            )
        ),
        ss_search_chars=search_chars,
        ss_width_offsets=width_offsets,
        ss_lengths=bytes(
            (
                1,
                2,
                3,
                4,
            )
        ),
    )

    COMBINING_DOT_ABOVE = b"\xcc\x87".decode("UTF-8")
    assert hashes[0][0] == _encode_and_hash("i")
    assert hashes[0][1] == _encode_and_hash("İ".lower())
    if case_sensitive:
        assert hashes[0][2] == _encode_and_hash("İ".lower() + "İ")
        assert hashes[0][3] == _encode_and_hash("İ".lower() + "İ")
        assert hashes[0][4] == _encode_and_hash("İ", reverse=True)
        assert hashes[0][5] == _encode_and_hash(COMBINING_DOT_ABOVE + "İ", reverse=True)
        assert hashes[0][6] == _encode_and_hash("İ".lower() + "İ", reverse=True)
        assert hashes[0][7] == _encode_and_hash("İ".lower() + "İ", reverse=True)
        assert hashes[0][8] == _encode_and_hash("İ")
        assert hashes[0][9] == _encode_and_hash("İ")
        assert hashes[0][12] == _encode_and_hash("İ")
        assert hashes[0][13] == _encode_and_hash("İ")

    else:
        assert hashes[0][2] == _encode_and_hash("İ".lower() + "i")
        assert hashes[0][3] == _encode_and_hash("İ".lower() * 2)
        assert hashes[0][4] == _encode_and_hash(COMBINING_DOT_ABOVE, reverse=True)
        assert hashes[0][5] == _encode_and_hash("İ".lower(), reverse=True)
        assert hashes[0][6] == _encode_and_hash(
            COMBINING_DOT_ABOVE + "İ".lower(), reverse=True
        )
        assert hashes[0][7] == _encode_and_hash("İ".lower() * 2, reverse=True)
        assert hashes[0][8] == _encode_and_hash("i")
        assert hashes[0][9] == _encode_and_hash("İ".lower())
        assert hashes[0][10] == _encode_and_hash("İ".lower() + "i")
        assert hashes[0][11] == _encode_and_hash("İ".lower() * 2)
        assert hashes[0][12] == _encode_and_hash(COMBINING_DOT_ABOVE)
        assert hashes[0][13] == _encode_and_hash(COMBINING_DOT_ABOVE + "i")
        assert hashes[0][14] == _encode_and_hash(
            COMBINING_DOT_ABOVE + "i" + COMBINING_DOT_ABOVE
        )
        assert hashes[0][15] == _encode_and_hash((COMBINING_DOT_ABOVE + "i") * 2)


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_character_combination_hashes_string_store_spec_cases(
    en_tokenizer, case_sensitive
):
    symbol = "FLAG19"
    short_word = "bee"
    normal_word = "serendipity"
    long_word = "serendipity" * 50
    assert len(long_word) > 255
    doc = en_tokenizer(" ".join((symbol, short_word, normal_word, long_word)))
    assert len(doc) == 4
    ps_search_chars, ps_width_offsets = get_search_char_byte_arrays("E", case_sensitive)
    hashes = doc.get_character_combination_hashes(
        cs=case_sensitive,
        p_lengths=bytes((2,)),
        s_lengths=bytes((2,)),
        ps_search_chars=ps_search_chars,
        ps_width_offsets=ps_width_offsets,
        ps_lengths=bytes((2,)),
        ss_search_chars=bytes(),
        ss_width_offsets=bytes(),
        ss_lengths=bytes(),
    )
    assert hashes[0][0] == _encode_and_hash("FL" if case_sensitive else "fl")
    assert hashes[0][1] == _encode_and_hash("91")
    assert hashes[0][2] == EMPTY_HASH_VALUE
    assert hashes[1][0] == _encode_and_hash("be")
    assert hashes[1][1] == _encode_and_hash("ee")
    if case_sensitive:
        assert hashes[1][2] == EMPTY_HASH_VALUE
    else:
        assert hashes[1][2] == _encode_and_hash("ee")
    assert hashes[2][0] == hashes[3][0] == _encode_and_hash("se")
    assert hashes[2][1] == hashes[3][1] == _encode_and_hash("yt")
    if case_sensitive:
        assert hashes[2][2] == hashes[3][2] == EMPTY_HASH_VALUE
    else:
        assert hashes[2][2] == hashes[3][2] == _encode_and_hash("ee")


def test_character_combination_hashes_empty_lengths(en_tokenizer):
    doc = en_tokenizer("and𐌞")
    assert (
        doc.get_character_combination_hashes(
            cs=True,
            p_lengths=bytes(),
            s_lengths=bytes(),
            ps_search_chars=bytes(),
            ps_width_offsets=bytes(),
            ps_lengths=bytes(),
            ss_search_chars=bytes(),
            ss_width_offsets=bytes(),
            ss_lengths=bytes(),
        ).shape
        == (1, 0)
    )
