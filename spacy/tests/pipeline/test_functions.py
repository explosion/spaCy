import pytest
from spacy.pipeline.functions import merge_subtokens
from spacy.language import Language
from spacy.tokens import Span, Doc


@pytest.fixture
def doc(en_vocab):
    # fmt: off
    words = ["This", "is", "a", "sentence", ".", "This", "is", "another", "sentence", ".", "And", "a", "third", "."]
    heads = [1, 1, 3, 1, 1, 6, 6, 8, 6, 6, 11, 12, 13, 13]
    deps = ["nsubj", "ROOT", "subtok", "attr", "punct", "nsubj", "ROOT",
            "subtok", "attr", "punct", "subtok", "subtok", "subtok", "ROOT"]
    # fmt: on
    return Doc(en_vocab, words=words, heads=heads, deps=deps)


@pytest.fixture
def doc2(en_vocab):
    words = ["I", "like", "New", "York", "in", "Autumn", "."]
    heads = [1, 1, 3, 1, 1, 4, 1]
    tags = ["PRP", "IN", "NNP", "NNP", "IN", "NNP", "."]
    pos = ["PRON", "VERB", "PROPN", "PROPN", "ADP", "PROPN", "PUNCT"]
    deps = ["ROOT", "prep", "compound", "pobj", "prep", "pobj", "punct"]
    doc = Doc(en_vocab, words=words, heads=heads, tags=tags, pos=pos, deps=deps)
    doc.ents = [Span(doc, 2, 4, label="GPE")]
    return doc


def test_merge_subtokens(doc):
    doc = merge_subtokens(doc)
    # Doc doesn't have spaces, so the result is "And a third ."
    # fmt: off
    assert [t.text for t in doc] == ["This", "is", "a sentence", ".", "This", "is", "another sentence", ".", "And a third ."]
    # fmt: on


def test_factories_merge_noun_chunks(doc2):
    assert len(doc2) == 7
    nlp = Language()
    merge_noun_chunks = nlp.create_pipe("merge_noun_chunks")
    merge_noun_chunks(doc2)
    assert len(doc2) == 6
    assert doc2[2].text == "New York"


def test_factories_merge_ents(doc2):
    assert len(doc2) == 7
    assert len(list(doc2.ents)) == 1
    nlp = Language()
    merge_entities = nlp.create_pipe("merge_entities")
    merge_entities(doc2)
    assert len(doc2) == 6
    assert len(list(doc2.ents)) == 1
    assert doc2[2].text == "New York"


def test_token_splitter():
    nlp = Language()
    config = {"min_length": 20, "split_length": 5}
    token_splitter = nlp.add_pipe("token_splitter", config=config)
    doc = nlp("aaaaabbbbbcccccdddd e f g")
    assert [t.text for t in doc] == ["aaaaabbbbbcccccdddd", "e", "f", "g"]
    doc = nlp("aaaaabbbbbcccccdddddeeeeeff g h i")
    assert [t.text for t in doc] == [
        "aaaaa",
        "bbbbb",
        "ccccc",
        "ddddd",
        "eeeee",
        "ff",
        "g",
        "h",
        "i",
    ]
    assert all(len(t.text) <= token_splitter.split_length for t in doc)
