# coding: utf-8
from __future__ import unicode_literals

import pytest
import numpy
from spacy.attrs import IS_ALPHA, IS_DIGIT, IS_LOWER, IS_PUNCT, IS_TITLE, IS_STOP
from spacy.symbols import VERB
from spacy.vocab import Vocab
from spacy.tokens import Doc

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


def test_doc_token_api_strings(en_tokenizer):
    text = "Give it back! He pleaded."
    pos = ["VERB", "PRON", "PART", "PUNCT", "PRON", "VERB", "PUNCT"]
    heads = [0, -1, -2, -3, 1, 0, -1]
    deps = ["ROOT", "dobj", "prt", "punct", "nsubj", "ROOT", "punct"]

    tokens = en_tokenizer(text)
    doc = get_doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    assert doc[0].orth_ == "Give"
    assert doc[0].text == "Give"
    assert doc[0].text_with_ws == "Give "
    assert doc[0].lower_ == "give"
    assert doc[0].shape_ == "Xxxx"
    assert doc[0].prefix_ == "G"
    assert doc[0].suffix_ == "ive"
    assert doc[0].pos_ == "VERB"
    assert doc[0].dep_ == "ROOT"


def test_doc_token_api_flags(en_tokenizer):
    text = "Give it back! He pleaded."
    tokens = en_tokenizer(text)
    assert tokens[0].check_flag(IS_ALPHA)
    assert not tokens[0].check_flag(IS_DIGIT)
    assert tokens[0].check_flag(IS_TITLE)
    assert tokens[1].check_flag(IS_LOWER)
    assert tokens[3].check_flag(IS_PUNCT)
    assert tokens[2].check_flag(IS_STOP)
    assert not tokens[5].check_flag(IS_STOP)
    # TODO: Test more of these, esp. if a bug is found


@pytest.mark.parametrize("text", ["Give it back! He pleaded."])
def test_doc_token_api_prob_inherited_from_vocab(en_tokenizer, text):
    word = text.split()[0]
    en_tokenizer.vocab[word].prob = -1
    tokens = en_tokenizer(text)
    assert tokens[0].prob != 0


@pytest.mark.parametrize("text", ["one two"])
def test_doc_token_api_str_builtin(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert str(tokens[0]) == text.split(" ")[0]
    assert str(tokens[1]) == text.split(" ")[1]


def test_doc_token_api_is_properties(en_vocab):
    doc = Doc(en_vocab, words=["Hi", ",", "my", "email", "is", "test@me.com"])
    assert doc[0].is_title
    assert doc[0].is_alpha
    assert not doc[0].is_digit
    assert doc[1].is_punct
    assert doc[3].is_ascii
    assert not doc[3].like_url
    assert doc[4].is_lower
    assert doc[5].like_email


def test_doc_token_api_vectors():
    vocab = Vocab()
    vocab.reset_vectors(width=2)
    vocab.set_vector("apples", vector=numpy.asarray([0.0, 2.0], dtype="f"))
    vocab.set_vector("oranges", vector=numpy.asarray([0.0, 1.0], dtype="f"))
    doc = Doc(vocab, words=["apples", "oranges", "oov"])
    assert doc.has_vector
    assert doc[0].has_vector
    assert doc[1].has_vector
    assert not doc[2].has_vector
    apples_norm = (0 * 0 + 2 * 2) ** 0.5
    oranges_norm = (0 * 0 + 1 * 1) ** 0.5
    cosine = ((0 * 0) + (2 * 1)) / (apples_norm * oranges_norm)
    assert doc[0].similarity(doc[1]) == cosine


def test_doc_token_api_ancestors(en_tokenizer):
    # the structure of this sentence depends on the English annotation scheme
    text = "Yesterday I saw a dog that barked loudly."
    heads = [2, 1, 0, 1, -2, 1, -2, -1, -6]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads)
    assert [t.text for t in doc[6].ancestors] == ["dog", "saw"]
    assert [t.text for t in doc[1].ancestors] == ["saw"]
    assert [t.text for t in doc[2].ancestors] == []

    assert doc[2].is_ancestor(doc[7])
    assert not doc[6].is_ancestor(doc[2])


def test_doc_token_api_head_setter(en_tokenizer):
    # the structure of this sentence depends on the English annotation scheme
    text = "Yesterday I saw a dog that barked loudly."
    heads = [2, 1, 0, 1, -2, 1, -2, -1, -6]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads)

    assert doc[6].n_lefts == 1
    assert doc[6].n_rights == 1
    assert doc[6].left_edge.i == 5
    assert doc[6].right_edge.i == 7

    assert doc[4].n_lefts == 1
    assert doc[4].n_rights == 1
    assert doc[4].left_edge.i == 3
    assert doc[4].right_edge.i == 7

    assert doc[3].n_lefts == 0
    assert doc[3].n_rights == 0
    assert doc[3].left_edge.i == 3
    assert doc[3].right_edge.i == 3

    assert doc[2].left_edge.i == 0
    assert doc[2].right_edge.i == 8

    doc[6].head = doc[3]

    assert doc[6].n_lefts == 1
    assert doc[6].n_rights == 1
    assert doc[6].left_edge.i == 5
    assert doc[6].right_edge.i == 7

    assert doc[3].n_lefts == 0
    assert doc[3].n_rights == 1
    assert doc[3].left_edge.i == 3
    assert doc[3].right_edge.i == 7

    assert doc[4].n_lefts == 1
    assert doc[4].n_rights == 0
    assert doc[4].left_edge.i == 3
    assert doc[4].right_edge.i == 7

    assert doc[2].left_edge.i == 0
    assert doc[2].right_edge.i == 8

    doc[0].head = doc[5]

    assert doc[5].left_edge.i == 0
    assert doc[6].left_edge.i == 0
    assert doc[3].left_edge.i == 0
    assert doc[4].left_edge.i == 0
    assert doc[2].left_edge.i == 0

    # head token must be from the same document
    doc2 = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads)
    with pytest.raises(ValueError):
        doc[0].head = doc2[0]


def test_is_sent_start(en_tokenizer):
    doc = en_tokenizer("This is a sentence. This is another.")
    assert doc[5].is_sent_start is None
    doc[5].is_sent_start = True
    assert doc[5].is_sent_start is True
    doc.is_parsed = True
    assert len(list(doc.sents)) == 2


def test_is_sent_end(en_tokenizer):
    doc = en_tokenizer("This is a sentence. This is another.")
    assert doc[4].is_sent_end is None
    doc[5].is_sent_start = True
    assert doc[4].is_sent_end is True
    doc.is_parsed = True
    assert len(list(doc.sents)) == 2


def test_set_pos():
    doc = Doc(Vocab(), words=["hello", "world"])
    doc[0].pos_ = "NOUN"
    assert doc[0].pos_ == "NOUN"
    doc[1].pos = VERB
    assert doc[1].pos_ == "VERB"


def test_tokens_sent(doc):
    """Test token.sent property"""
    assert len(list(doc.sents)) == 3
    assert doc[1].sent.text == "This is a sentence ."
    assert doc[7].sent.text == "This is another sentence ."
    assert doc[1].sent.root.left_edge.text == "This"
    assert doc[7].sent.root.left_edge.text == "This"


def test_token0_has_sent_start_true():
    doc = Doc(Vocab(), words=["hello", "world"])
    assert doc[0].is_sent_start is True
    assert doc[1].is_sent_start is None
    assert not doc.is_sentenced


def test_tokenlast_has_sent_end_true():
    doc = Doc(Vocab(), words=["hello", "world"])
    assert doc[0].is_sent_end is None
    assert doc[1].is_sent_end is True
    assert not doc.is_sentenced


def test_token_api_conjuncts_chain(en_vocab):
    words = "The boy and the girl and the man went .".split()
    heads = [1, 7, -1, 1, -3, -1, 1, -3, 0, -1]
    deps = ["det", "nsubj", "cc", "det", "conj", "cc", "det", "conj", "ROOT", "punct"]
    doc = get_doc(en_vocab, words=words, heads=heads, deps=deps)
    assert [w.text for w in doc[1].conjuncts] == ["girl", "man"]
    assert [w.text for w in doc[4].conjuncts] == ["boy", "man"]
    assert [w.text for w in doc[7].conjuncts] == ["boy", "girl"]


def test_token_api_conjuncts_simple(en_vocab):
    words = "They came and went .".split()
    heads = [1, 0, -1, -2, -1]
    deps = ["nsubj", "ROOT", "cc", "conj", "dep"]
    doc = get_doc(en_vocab, words=words, heads=heads, deps=deps)
    assert [w.text for w in doc[1].conjuncts] == ["went"]
    assert [w.text for w in doc[3].conjuncts] == ["came"]


def test_token_api_non_conjuncts(en_vocab):
    words = "They came .".split()
    heads = [1, 0, -1]
    deps = ["nsubj", "ROOT", "punct"]
    doc = get_doc(en_vocab, words=words, heads=heads, deps=deps)
    assert [w.text for w in doc[0].conjuncts] == []
    assert [w.text for w in doc[1].conjuncts] == []
