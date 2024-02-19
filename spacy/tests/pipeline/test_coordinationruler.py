import pytest
from typing import List
from spacy.tokens import Doc

import en_core_web_sm


@pytest.fixture
def nlp():
    return en_core_web_sm.load()


def _my_custom_splitting_rule(doc: Doc) -> List[str]:
    split_phrases = []
    for token in doc:
        if token.text == "read":
            split_phrases.append("test1")
            split_phrases.append("test2")
    return split_phrases


def test_coordinationruler(nlp):
    doc = nlp("I read and write books")
    assert len(doc) == 5
    assert [d.text for d in doc] == ["I", "read", "and", "write", "books"]
    coord_splitter = nlp.add_pipe("coordination_splitter")
    assert len(coord_splitter.rules) == 3
    assert coord_splitter.name == "coordination_splitter"
    doc_split = coord_splitter(doc)
    assert len(doc_split) == 2
    assert [t.text for t in doc_split] == ["I read books", "I write books"]


def test_coordinationruler_clear_rules(nlp):
    coord_splitter = nlp.add_pipe("coordination_splitter")
    assert len(coord_splitter.rules) == 3
    coord_splitter.clear_rules()
    assert len(coord_splitter.rules) == 0
    assert coord_splitter.rules == []


def test_coordinationruler_add_rule(nlp):
    coord_splitter = nlp.add_pipe("coordination_splitter")
    assert len(coord_splitter.rules) == 3
    coord_splitter.add_rule(_my_custom_splitting_rule)
    assert len(coord_splitter.rules) == 4


def test_coordinationruler_add_rules(nlp):
    doc = nlp("I read and write books")
    coord_splitter = nlp.add_pipe("coordination_splitter")
    coord_splitter.clear_rules()
    coord_splitter.add_rules([_my_custom_splitting_rule, _my_custom_splitting_rule])
    assert len(coord_splitter.rules) == 2
    doc_split = coord_splitter(doc)
    assert len(doc_split) == 2

    assert [t.text for t in doc_split] == ["test1", "test2"]


def test_coordinationruler_add_default_rules(nlp):
    coord_splitter = nlp.add_pipe("coordination_splitter")
    coord_splitter.clear_rules()
    assert len(coord_splitter.rules) == 0
    coord_splitter.add_default_rules()
    assert len(coord_splitter.rules) == 3
