from typing import List

import pytest

import spacy
from spacy.pipeline.coordinationruler import split_noun_coordination
from spacy.tokens import Doc


@pytest.fixture
def nlp():
    return spacy.blank("en")


### CONSTRUCTION CASES ###
@pytest.fixture
def noun_construction_case1(nlp):
    words = ["apples", "and", "oranges"]
    spaces = [True, True, False]
    pos_tags = ["NOUN", "CCONJ", "NOUN"]
    dep_relations = ["nsubj", "cc", "conj"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    doc[1].head = doc[2]
    doc[2].head = doc[0]
    doc[0].head = doc[0]

    return doc


@pytest.fixture
def noun_construction_case2(nlp):
    words = ["red", "apples", "and", "oranges"]
    spaces = [True, True, True, False]
    pos_tags = ["ADJ", "NOUN", "CCONJ", "NOUN"]
    dep_relations = ["amod", "nsubj", "cc", "conj"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    doc[0].head = doc[1]
    doc[2].head = doc[3]
    doc[3].head = doc[1]

    return doc


@pytest.fixture
def noun_construction_case3(nlp):
    words = ["apples", "and", "juicy", "oranges"]
    spaces = [True, True, True, False]
    pos_tags = ["NOUN", "CCONJ", "ADJ", "NOUN"]
    dep_relations = ["nsubj", "cc", "amod", "conj"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    doc[0].head = doc[0]
    doc[1].head = doc[3]
    doc[2].head = doc[3]
    doc[3].head = doc[0]

    return doc


@pytest.fixture
def noun_construction_case4(nlp):
    words = ["hot", "chicken", "wings", "and", "soup"]
    spaces = [True, True, True, True, False]
    pos_tags = ["ADJ", "NOUN", "NOUN", "CCONJ", "NOUN"]
    dep_relations = ["amod", "compound", "ROOT", "cc", "conj"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    doc[0].head = doc[2]
    doc[1].head = doc[2]
    doc[2].head = doc[2]
    doc[3].head = doc[4]
    doc[4].head = doc[2]

    return doc


@pytest.fixture
def noun_construction_case5(nlp):
    words = ["green", "apples", "and", "rotten", "oranges"]
    spaces = [True, True, True, True, False]
    pos_tags = ["ADJ", "NOUN", "CCONJ", "ADJ", "NOUN"]
    dep_relations = ["amod", "ROOT", "cc", "amod", "conj"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    doc[0].head = doc[1]
    doc[1].head = doc[1]
    doc[2].head = doc[4]
    doc[3].head = doc[4]
    doc[4].head = doc[1]

    return doc


@pytest.fixture
def noun_construction_case6(nlp):
    words = ["very", "green", "apples", "and", "oranges"]
    spaces = [True, True, True, True, False]
    pos_tags = ["ADV", "ADJ", "NOUN", "CCONJ", "NOUN"]
    dep_relations = ["advmod", "amod", "ROOT", "cc", "conj"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    doc[0].head = doc[1]
    doc[1].head = doc[2]
    doc[2].head = doc[2]
    doc[3].head = doc[4]
    doc[4].head = doc[2]

    return doc


@pytest.fixture
def noun_construction_case7(nlp):
    words = ["fresh", "and", "juicy", "apples"]
    spaces = [True, True, True, False]
    pos_tags = ["ADJ", "CCONJ", "ADJ", "NOUN"]
    dep_relations = ["amod", "cc", "conj", "ROOT"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    doc[0].head = doc[3]
    doc[1].head = doc[2]
    doc[2].head = doc[0]
    doc[3].head = doc[3]

    return doc


@pytest.fixture
def noun_construction_case8(nlp):
    words = ["fresh", ",", "juicy", "and", "delicious", "apples"]
    spaces = [True, True, True, True, True, False]
    pos_tags = ["ADJ", "PUNCT", "ADJ", "CCONJ", "ADJ", "NOUN"]
    dep_relations = ["amod", "punct", "conj", "cc", "conj", "ROOT"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    doc[0].head = doc[5]
    doc[1].head = doc[2]
    doc[2].head = doc[0]
    doc[3].head = doc[4]
    doc[4].head = doc[0]
    doc[5].head = doc[5]

    return doc


@pytest.fixture
def noun_construction_case9(nlp):
    words = ["fresh", "and", "quite", "sour", "apples"]
    spaces = [True, True, True, True, False]
    pos_tags = ["ADJ", "CCONJ", "ADV", "ADJ", "NOUN"]
    dep_relations = ["amod", "cc", "advmod", "conj", "ROOT"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    doc[0].head = doc[4]
    doc[1].head = doc[3]
    doc[2].head = doc[3]
    doc[3].head = doc[0]
    doc[4].head = doc[4]

    return doc


@pytest.fixture
def noun_construction_case10(nlp):
    words = ["fresh", "but", "quite", "sour", "apples", "and", "chicken", "wings"]
    spaces = [True, True, True, True, True, True, True, False]
    pos_tags = ["ADJ", "CCONJ", "ADV", "ADJ", "NOUN", "CCONJ", "NOUN", "NOUN"]
    dep_relations = ["amod", "cc", "advmod", "amod", "ROOT", "cc", "compound", "conj"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    doc[0].head = doc[4]
    doc[1].head = doc[4]
    doc[2].head = doc[3]
    doc[3].head = doc[4]
    doc[5].head = doc[4]
    doc[6].head = doc[7]
    doc[7].head = doc[4]

    return doc


@pytest.fixture
def noun_construction_case11(nlp):
    words = ["water", "and", "power", "meters", "and", "electrical", "sockets"]
    spaces = [True, True, True, True, True, True, False]
    pos_tags = ["NOUN", "CCONJ", "NOUN", "NOUN", "CCONJ", "ADJ", "NOUN"]
    dep_relations = ["compound", "cc", "compound", "ROOT", "cc", "amod", "conj"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    doc[0].head = doc[2]
    doc[1].head = doc[2]
    doc[2].head = doc[3]
    doc[3].head = doc[3]
    doc[4].head = doc[6]
    doc[5].head = doc[6]
    doc[6].head = doc[3]

    return doc


### splitting rules ###
def _my_custom_splitting_rule(doc: Doc) -> List[str]:
    split_phrases = []
    for token in doc:
        if token.text == "red":
            split_phrases.append("test1")
            split_phrases.append("test2")
    return split_phrases


# test split_noun_coordination on 6 different cases
def test_split_noun_coordination(
    noun_construction_case1,
    noun_construction_case2,
    noun_construction_case3,
    noun_construction_case4,
    noun_construction_case5,
    noun_construction_case6,
    noun_construction_case7,
    noun_construction_case8,
    noun_construction_case9,
    noun_construction_case10,
    noun_construction_case11,
):

    # test 1: no modifier - it should return None from _split_doc
    case1_split = split_noun_coordination(noun_construction_case1)

    assert case1_split == None

    # test 2: modifier is at the beginning of the noun phrase
    case2_split = split_noun_coordination(noun_construction_case2)

    assert len(case2_split) == 2
    assert isinstance(case2_split, list)
    assert all(isinstance(phrase, str) for phrase in case2_split)
    assert case2_split == ["red apples", "red oranges"]

    # test 3: modifier is at the end of the noun phrase
    case3_split = split_noun_coordination(noun_construction_case3)

    assert len(case3_split) == 2
    assert isinstance(case3_split, list)
    assert all(isinstance(phrase, str) for phrase in case3_split)
    assert case3_split == ["juicy oranges", "juicy apples"]

    # test 4: deal with compound nouns
    case4_split = split_noun_coordination(noun_construction_case4)

    assert len(case4_split) == 2
    assert isinstance(case4_split, list)
    assert all(isinstance(phrase, str) for phrase in case4_split)
    assert case4_split == ["hot chicken wings", "hot soup"]

    # #test 5: same # of modifiers as nouns
    # case5_split = split_noun_coordination(noun_construction_case5)
    # assert case5_split == None

    # test 6: modifier phrases
    case6_split = split_noun_coordination(noun_construction_case6)

    assert len(case6_split) == 2
    assert isinstance(case6_split, list)
    assert all(isinstance(phrase, str) for phrase in case6_split)
    assert case6_split == ["very green apples", "very green oranges"]

    ## test cases for coordinating adjectives

    # test 7:
    case7_split = split_noun_coordination(noun_construction_case7)
    print(case7_split)
    assert case7_split == ["fresh apples", "juicy apples"]

    # test 8:
    case8_split = split_noun_coordination(noun_construction_case8)
    assert case8_split == ["fresh apples", "juicy apples", "delicious apples"]

    # test 9:
    case9_split = split_noun_coordination(noun_construction_case9)
    assert case9_split == ["fresh apples", "quite sour apples"]

    # test 10:
    case10_split = split_noun_coordination(noun_construction_case10)
    assert case10_split == [
        "fresh apples",
        "quite sour apples",
        "fresh chicken wings",
        "quite sour chicken wings",
    ]

    # test 11:
    case11_split = split_noun_coordination(noun_construction_case11)
    pass


################### test factory ##############################


def test_coordinationruler(nlp, noun_construction_case2):
    assert len(noun_construction_case2) == 4
    assert [d.text for d in noun_construction_case2] == [
        "red",
        "apples",
        "and",
        "oranges",
    ]

    coord_splitter = nlp.add_pipe("coordination_splitter")
    assert len(coord_splitter.rules) == 1
    assert coord_splitter.name == "coordination_splitter"
    doc_split = coord_splitter(noun_construction_case2)
    assert len(doc_split) == 2
    assert [t.text for t in doc_split] == ["red apples", "red oranges"]


def test_coordinationruler_clear_rules(nlp):
    coord_splitter = nlp.add_pipe("coordination_splitter")
    assert len(coord_splitter.rules) == 1
    coord_splitter.clear_rules()
    assert len(coord_splitter.rules) == 0
    assert coord_splitter.rules == []


def test_coordinationruler_add_rule(nlp):
    coord_splitter = nlp.add_pipe("coordination_splitter")
    assert len(coord_splitter.rules) == 1
    coord_splitter.add_rule(_my_custom_splitting_rule)
    assert len(coord_splitter.rules) == 2


def test_coordinationruler_add_rules(nlp, noun_construction_case2):

    coord_splitter = nlp.add_pipe("coordination_splitter")
    coord_splitter.clear_rules()
    coord_splitter.add_rules([_my_custom_splitting_rule, _my_custom_splitting_rule])
    assert len(coord_splitter.rules) == 2
    doc_split = coord_splitter(noun_construction_case2)
    assert len(doc_split) == 2

    assert [t.text for t in doc_split] == ["test1", "test2"]


def test_coordinationruler_add_default_rules(nlp):
    coord_splitter = nlp.add_pipe("coordination_splitter")
    coord_splitter.clear_rules()
    assert len(coord_splitter.rules) == 0
    coord_splitter.add_default_rules()
    assert len(coord_splitter.rules) == 1
