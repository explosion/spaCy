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


EMPTY_HASH_VALUE = 0xCBF29CE484222325


def test_fnv1a_hash():
    """Checks the conformity of the 64-bit FNV1A implementation with
    http://www.isthe.com/chongo/src/fnv/test_fnv.c.
    The method called here is only used in testing; in production
    code, the hashing is performed in a fashion that is interweaved
    with other logic. The conformity of the production code is
    demonstrated by the character combination hash tests, where
    hashes produced by the production code are tested for equality
    against hashes produced by the test code.
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
        0xAF63DC4C8601EC8C,
        0xAF63DF4C8601F1A5,
        0xAF63DE4C8601EFF2,
        0xAF63D94C8601E773,
        0xAF63D84C8601E5C0,
        0xAF63DB4C8601EAD9,
        0x08985907B541D342,
        0xDCB27518FED9D577,
        0xDD120E790C2512AF,
        0xCAC165AFA2FEF40A,
        0x85944171F73967E8,
        0xAF63BD4C8601B7DF,
        0x089BE207B544F1E4,
        0x08A61407B54D9B5F,
        0x08A2AE07B54AB836,
        0x0891B007B53C4869,
        0x088E4A07B5396540,
        0x08987C07B5420EBB,
        0xDCB28A18FED9F926,
        0xDD1270790C25B935,
        0xCAC146AFA2FEBF5D,
        0x8593D371F738ACFE,
        0x34531CA7168B8F38,
        0x08A25607B54A22AE,
        0xF5FAF0190CF90DF3,
        0xF27397910B3221C7,
        0x2C8C2B76062F22E0,
        0xE150688C8217B8FD,
        0xF35A83C10E4F1F87,
        0xD1EDD10B507344D0,
        0x2A5EE739B3DDB8C3,
        0xDCFB970CA1C0D310,
        0x4054DA76DAA6DA90,
        0xF70A2FF589861368,
        0x4C628B38AED25F17,
        0x9DD1F6510F78189F,
        0xA3DE85BD491270CE,
        0x858E2FA32A55E61D,
        0x46810940EFF5F915,
        0xF5FADD190CF8EDAA,
        0xF273ED910B32B3E9,
        0x2C8C5276062F6525,
        0xE150B98C821842A0,
        0xF35AA3C10E4F55E7,
        0xD1ED680B50729265,
        0x2A5F0639B3DDED70,
        0xDCFBAA0CA1C0F359,
        0x4054BA76DAA6A430,
        0xF709C7F5898562B0,
        0x4C62E638AED2F9B8,
        0x9DD1A8510F779415,
        0xA3DE2ABD4911D62D,
        0x858E0EA32A55AE0A,
        0x46810F40EFF60347,
        0xC33BCE57BEF63EAF,
        0x08A24307B54A0265,
        0xF5B9FD190CC18D15,
        0x4C968290ACE35703,
        0x07174BD5C64D9350,
        0x5A294C3FF5D18750,
        0x05B3C1AEB308B843,
        0xB92A48DA37D0F477,
        0x73CDDDCCD80EBC49,
        0xD58C4C13210A266B,
        0xE78B6081243EC194,
        0xB096F77096A39F34,
        0xB425C54FF807B6A3,
        0x23E520E2751BB46E,
        0x1A0B44CCFE1385EC,
        0xF5BA4B190CC2119F,
        0x4C962690ACE2BAAF,
        0x0716DED5C64CDA19,
        0x5A292C3FF5D150F0,
        0x05B3E0AEB308ECF0,
        0xB92A5EDA37D119D9,
        0x73CE41CCD80F6635,
        0xD58C2C132109F00B,
        0xE78BAF81243F47D1,
        0xB0968F7096A2EE7C,
        0xB425A84FF807855C,
        0x23E4E9E2751B56F9,
        0x1A0B4ECCFE1396EA,
        0x54ABD453BB2C9004,
        0x08BA5F07B55EC3DA,
        0x337354193006CB6E,
        0xA430D84680AABD0B,
        0xA9BC8ACCA21F39B1,
        0x6961196491CC682D,
        0xAD2BB1774799DFE9,
        0x6961166491CC6314,
        0x8D1BB3904A3B1236,
        0x6961176491CC64C7,
        0xED205D87F40434C7,
        0x6961146491CC5FAE,
        0xCD3BAF5E44F8AD9C,
        0xE3B36596127CD6D8,
        0xF77F1072C8E8A646,
        0xE3B36396127CD372,
        0x6067DCE9932AD458,
        0xE3B37596127CF208,
        0x4B7B10FA9FE83936,
        0xAABAFE7104D914BE,
        0xF4D3180B3CDE3EDA,
        0xAABAFD7104D9130B,
        0xF4CFB20B3CDB5BB1,
        0xAABAFC7104D91158,
        0xF4CC4C0B3CD87888,
        0xE729BAC5D2A8D3A7,
        0x74BC0524F4DFA4C5,
        0xE72630C5D2A5B352,
        0x6B983224EF8FB456,
        0xE73042C5D2AE266D,
        0x8527E324FDEB4B37,
        0x0A83C86FEE952ABC,
        0x7318523267779D74,
        0x3E66D3D56B8CACA1,
        0x956694A5C0095593,
        0xCAC54572BB1A6FC8,
        0xA7A4C9F3EDEBF0D8,
        0x7829851FAC17B143,
        0x2C8F4C9AF81BCF06,
        0xD34E31539740C732,
        0x3605A2AC253D2DB1,
        0x08C11B8346F4A3C3,
        0x6BE396289CE8A6DA,
        0xD9B957FB7FE794C5,
        0x05BE33DA04560A93,
        0x0957F1577BA9747C,
        0xDA2CC3ACC24FBA57,
        0x74136F185B29E7F0,
        0xB2F2B4590EDB93B2,
        0xB3608FCE8B86AE04,
        0x4A3A865079359063,
        0x5B3A7EF496880A50,
        0x48FAE3163854C23B,
        0x07AAA640476E0B9A,
        0x2F653656383A687D,
        0xA1031F8E7599D79C,
        0xA31908178FF92477,
        0x097EDF3C14C3FB83,
        0xB51CA83FEAA0971B,
        0xDD3C0D96D784F2E9,
        0x86CD26A9EA767D78,
        0xE6B215FF54A30C18,
        0xEC5B06A1C5531093,
        0x45665A929F9EC5E5,
        0x8C7609B4A9F10907,
        0x89AAC3A491F0D729,
        0x32CE6B26E0F4A403,
        0x614AB44E02B53E01,
        0xFA6472EB6EEF3290,
        0x9E5D75EB1948EB6A,
        0xB6D12AD4A8671852,
        0x88826F56EBA07AF1,
        0x44535BF2645BC0FD,
        0x169388FFC21E3728,
        0xF68AAC9E396D8224,
        0x8E87D7E7472B3883,
        0x295C26CAA8B423DE,
        0x322C814292E72176,
        0x8A06550EB8AF7268,
        0xEF86D60E661BCF71,
        0x9E5426C87F30EE54,
        0xF1EA8AA826FD047E,
        0x0BABAF9A642CB769,
        0x4B3341D4068D012E,
        0xD15605CBC30A335C,
        0x5B21060AED8412E5,
        0x45E2CDA1CE6F4227,
        0x50AE3745033AD7D4,
        0xAA4588CED46BF414,
        0xC1B0056C4A95467E,
        0x56576A71DE8B4089,
        0xBF20965FA6DC927E,
        0x569F8383C2040882,
        0xE1E772FBA08FECA0,
        0x4CED94AF97138AC4,
        0xC4112FFB337A82FB,
        0xD64A4FD41DE38B7D,
        0x4CFC32329EDEBCBB,
        0x0803564445050395,
        0xAA1574ECF4642FFD,
        0x694BC4E54CC315F9,
        0xA3D7CB273B011721,
        0x577C2F8B6115BFA5,
        0xB7EC8C1A769FB4C1,
        0x5D5CFCE63359AB19,
        0x33B96C3CD65B5F71,
        0xD845097780602BB9,
        0x84D47645D02DA3D5,
        0x83544F33B58773A5,
        0x9175CBB2160836C5,
        0xC71B3BC175E72BC5,
        0x636806AC222EC985,
        0xB6EF0E6950F52ED5,
        0xEAD3D8A0F3DFDAA5,
        0x922908FE9A861BA5,
        0x6D4821DE275FD5C5,
        0x1FE3FCE62BD816B5,
        0xC23E9FCCD6F70591,
        0xC1AF12BDFE16B5B5,
        0x39E9F18F2F85E221,
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
    assert doc.get_character_combination_hashes(
        cs=True,
        p_lengths=bytes(),
        s_lengths=bytes(),
        ps_search_chars=bytes(),
        ps_width_offsets=bytes(),
        ps_lengths=bytes(),
        ss_search_chars=bytes(),
        ss_width_offsets=bytes(),
        ss_lengths=bytes(),
    ).shape == (1, 0)
