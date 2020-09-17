import pytest
from spacy.pipeline.functions import merge_subtokens
from spacy.language import Language
from spacy.tokens import Span

from ..util import get_doc


@pytest.fixture
def doc(en_tokenizer):
    # fmt: off
    text = "This is a sentence. This is another sentence. And a third."
    heads = [1, 0, 1, -2, -3, 1, 0, 1, -2, -3, 1, 1, 1, 0]
    deps = ["nsubj", "ROOT", "subtok", "attr", "punct", "nsubj", "ROOT",
            "subtok", "attr", "punct", "subtok", "subtok", "subtok", "ROOT"]
    # fmt: on
    tokens = en_tokenizer(text)
    return get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads, deps=deps)


@pytest.fixture
def doc2(en_tokenizer):
    text = "I like New York in Autumn."
    heads = [1, 0, 1, -2, -3, -1, -5]
    tags = ["PRP", "IN", "NNP", "NNP", "IN", "NNP", "."]
    pos = ["PRON", "VERB", "PROPN", "PROPN", "ADP", "PROPN", "PUNCT"]
    deps = ["ROOT", "prep", "compound", "pobj", "prep", "pobj", "punct"]
    tokens = en_tokenizer(text)
    doc = get_doc(
        tokens.vocab,
        words=[t.text for t in tokens],
        heads=heads,
        tags=tags,
        pos=pos,
        deps=deps,
    )
    doc.ents = [Span(doc, 2, 4, doc.vocab.strings["GPE"])]
    return doc


def test_merge_subtokens(doc):
    doc = merge_subtokens(doc)
    # get_doc() doesn't set spaces, so the result is "And a third ."
    assert [t.text for t in doc] == [
        "This",
        "is",
        "a sentence",
        ".",
        "This",
        "is",
        "another sentence",
        ".",
        "And a third .",
    ]


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
