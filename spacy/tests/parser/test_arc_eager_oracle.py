# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.vocab import Vocab
from spacy.pipeline import DependencyParser
from spacy.tokens import Doc
from spacy.gold import GoldParse
from spacy.syntax.nonproj import projectivize
from spacy.syntax.stateclass import StateClass
from spacy.syntax.arc_eager import ArcEager


def get_sequence_costs(M, words, heads, deps, transitions):
    doc = Doc(Vocab(), words=words)
    gold = GoldParse(doc, heads=heads, deps=deps)
    state = StateClass(doc)
    M.preprocess_gold(gold)
    cost_history = []
    for gold_action in transitions:
        state_costs = {}
        for i in range(M.n_moves):
            name = M.class_name(i)
            state_costs[name] = M.get_cost(state, gold, i)
        M.transition(state, gold_action)
        cost_history.append(state_costs)
    return state, cost_history


@pytest.fixture
def vocab():
    return Vocab()


@pytest.fixture
def arc_eager(vocab):
    moves = ArcEager(vocab.strings, ArcEager.get_actions())
    moves.add_action(2, "left")
    moves.add_action(3, "right")
    return moves


@pytest.fixture
def words():
    return ["a", "b"]


@pytest.fixture
def doc(words, vocab):
    if vocab is None:
        vocab = Vocab()
    return Doc(vocab, words=list(words))


@pytest.fixture
def gold(doc, words):
    if len(words) == 2:
        return GoldParse(doc, words=["a", "b"], heads=[0, 0], deps=["ROOT", "right"])
    else:
        raise NotImplementedError


@pytest.mark.xfail
def test_oracle_four_words(arc_eager, vocab):
    words = ["a", "b", "c", "d"]
    heads = [1, 1, 3, 3]
    deps = ["left", "ROOT", "left", "ROOT"]
    actions = ["L-left", "B-ROOT", "L-left"]
    state, cost_history = get_sequence_costs(arc_eager, words, heads, deps, actions)
    assert state.is_final()
    for i, state_costs in enumerate(cost_history):
        # Check gold moves is 0 cost
        assert state_costs[actions[i]] == 0.0, actions[i]
        for other_action, cost in state_costs.items():
            if other_action != actions[i]:
                assert cost >= 1


annot_tuples = [
    (0, "When", "WRB", 11, "advmod", "O"),
    (1, "Walter", "NNP", 2, "compound", "B-PERSON"),
    (2, "Rodgers", "NNP", 11, "nsubj", "L-PERSON"),
    (3, ",", ",", 2, "punct", "O"),
    (4, "our", "PRP$", 6, "poss", "O"),
    (5, "embedded", "VBN", 6, "amod", "O"),
    (6, "reporter", "NN", 2, "appos", "O"),
    (7, "with", "IN", 6, "prep", "O"),
    (8, "the", "DT", 10, "det", "B-ORG"),
    (9, "3rd", "NNP", 10, "compound", "I-ORG"),
    (10, "Cavalry", "NNP", 7, "pobj", "L-ORG"),
    (11, "says", "VBZ", 44, "advcl", "O"),
    (12, "three", "CD", 13, "nummod", "U-CARDINAL"),
    (13, "battalions", "NNS", 16, "nsubj", "O"),
    (14, "of", "IN", 13, "prep", "O"),
    (15, "troops", "NNS", 14, "pobj", "O"),
    (16, "are", "VBP", 11, "ccomp", "O"),
    (17, "on", "IN", 16, "prep", "O"),
    (18, "the", "DT", 19, "det", "O"),
    (19, "ground", "NN", 17, "pobj", "O"),
    (20, ",", ",", 17, "punct", "O"),
    (21, "inside", "IN", 17, "prep", "O"),
    (22, "Baghdad", "NNP", 21, "pobj", "U-GPE"),
    (23, "itself", "PRP", 22, "appos", "O"),
    (24, ",", ",", 16, "punct", "O"),
    (25, "have", "VBP", 26, "aux", "O"),
    (26, "taken", "VBN", 16, "dep", "O"),
    (27, "up", "RP", 26, "prt", "O"),
    (28, "positions", "NNS", 26, "dobj", "O"),
    (29, "they", "PRP", 31, "nsubj", "O"),
    (30, "'re", "VBP", 31, "aux", "O"),
    (31, "going", "VBG", 26, "parataxis", "O"),
    (32, "to", "TO", 33, "aux", "O"),
    (33, "spend", "VB", 31, "xcomp", "O"),
    (34, "the", "DT", 35, "det", "B-TIME"),
    (35, "night", "NN", 33, "dobj", "L-TIME"),
    (36, "there", "RB", 33, "advmod", "O"),
    (37, "presumably", "RB", 33, "advmod", "O"),
    (38, ",", ",", 44, "punct", "O"),
    (39, "how", "WRB", 40, "advmod", "O"),
    (40, "many", "JJ", 41, "amod", "O"),
    (41, "soldiers", "NNS", 44, "pobj", "O"),
    (42, "are", "VBP", 44, "aux", "O"),
    (43, "we", "PRP", 44, "nsubj", "O"),
    (44, "talking", "VBG", 44, "ROOT", "O"),
    (45, "about", "IN", 44, "prep", "O"),
    (46, "right", "RB", 47, "advmod", "O"),
    (47, "now", "RB", 44, "advmod", "O"),
    (48, "?", ".", 44, "punct", "O"),
]


def test_get_oracle_actions():
    doc = Doc(Vocab(), words=[t[1] for t in annot_tuples])
    parser = DependencyParser(doc.vocab)
    parser.moves.add_action(0, "")
    parser.moves.add_action(1, "")
    parser.moves.add_action(1, "")
    parser.moves.add_action(4, "ROOT")
    for i, (id_, word, tag, head, dep, ent) in enumerate(annot_tuples):
        if head > i:
            parser.moves.add_action(2, dep)
        elif head < i:
            parser.moves.add_action(3, dep)
    ids, words, tags, heads, deps, ents = zip(*annot_tuples)
    heads, deps = projectivize(heads, deps)
    gold = GoldParse(doc, words=words, tags=tags, heads=heads, deps=deps)
    parser.moves.preprocess_gold(gold)
    parser.moves.get_oracle_sequence(doc, gold)
