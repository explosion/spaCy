from __future__ import unicode_literals
import pytest

from ...vocab import Vocab
from ...pipeline import DependencyParser
from ...tokens import Doc
from ...gold import GoldParse
from ...syntax.nonproj import projectivize
from ...syntax.stateclass import StateClass
from ...syntax.arc_eager import ArcEager


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
    moves.add_action(2, 'left')
    moves.add_action(3, 'right')
    return moves

@pytest.fixture
def words():
    return ['a', 'b']

@pytest.fixture
def doc(words, vocab):
    if vocab is None:
        vocab = Vocab()
    return Doc(vocab, words=list(words))

@pytest.fixture
def gold(doc, words):
    if len(words) == 2:
        return GoldParse(doc, words=['a', 'b'], heads=[0, 0], deps=['ROOT', 'right'])
    else:
        raise NotImplementedError


def test_shift_is_gold_at_first_state(arc_eager, doc, gold):
    state = StateClass(doc)
    arc_eager.preprocess_gold(gold)
    assert arc_eager.get_cost(state, gold, 'S') == 0


def test_reduce_is_not_gold_at_second_state(arc_eager, doc, gold):
    state = StateClass(doc)
    arc_eager.preprocess_gold(gold)
    arc_eager.transition(state, 'S')
    assert arc_eager.get_cost(state, gold, 'D') != 0


def test_break_is_not_gold_at_second_state(arc_eager, doc, gold):
    state = StateClass(doc)
    arc_eager.preprocess_gold(gold)
    arc_eager.transition(state, 'S')
    assert arc_eager.get_cost(state, gold, 'B-ROOT') != 0

def test_left_is_not_gold_at_second_state(arc_eager, doc, gold):
    state = StateClass(doc)
    arc_eager.preprocess_gold(gold)
    arc_eager.transition(state, 'S')
    assert arc_eager.get_cost(state, gold, 'L-left') != 0

def test_right_is_gold_at_second_state(arc_eager, doc, gold):
    state = StateClass(doc)
    arc_eager.preprocess_gold(gold)
    arc_eager.transition(state, 'S')
    assert arc_eager.get_cost(state, gold, 'R-right') == 0


def test_reduce_is_gold_at_third_state(arc_eager, doc, gold):
    state = StateClass(doc)
    arc_eager.preprocess_gold(gold)
    arc_eager.transition(state, 'S')
    arc_eager.transition(state, 'R-right')
    assert arc_eager.get_cost(state, gold, 'D') == 0

def test_cant_arc_is_gold_at_third_state(arc_eager, doc, gold):
    state = StateClass(doc)
    arc_eager.preprocess_gold(gold)
    arc_eager.transition(state, 'S')
    arc_eager.transition(state, 'R-right')
    assert not state.can_arc()


def test_fourth_state_is_final(arc_eager, doc, gold):
    state = StateClass(doc)
    arc_eager.preprocess_gold(gold)
    arc_eager.transition(state, 'S')
    arc_eager.transition(state, 'R-right')
    arc_eager.transition(state, 'D')
    assert state.is_final()


def test_oracle_sequence_two_words(arc_eager, doc, gold):
    parser = DependencyParser(doc.vocab, moves=arc_eager)
    state = StateClass(doc)
    parser.moves.preprocess_gold(gold)
    actions = parser.moves.get_oracle_sequence(doc, gold)
    names = [parser.moves.class_name(i) for i in actions]
    assert names == ['S', 'R-right', 'D']

def test_oracle_four_words(arc_eager, vocab):
    words = ['a', 'b', 'c', 'd']
    heads = [1, 1, 3, 3]
    deps = ['left', 'ROOT', 'left', 'ROOT']
    actions = ['S', 'L-left', 'S', 'B-ROOT', 'S', 'L-left', 'S']
    state, cost_history = get_sequence_costs(arc_eager, words, heads, deps, actions)
    assert state.is_final()
    for i, state_costs in enumerate(cost_history):
        # Check gold moves is 0 cost
        assert state_costs[actions[i]] == 0.0, actions[i]
        for other_action, cost in state_costs.items():
            if other_action != actions[i]:
                assert cost >= 1

def test_non_monotonic_sequence_four_words(arc_eager, vocab):
    words = ['a', 'b', 'c', 'd']
    heads = [1, 1, 3, 3]
    deps = ['left', 'B-ROOT', 'left', 'B-ROOT']
    actions = ['S', 'R-right', 'R-right', 'L-left', 'L-left', 'L-left', 'S']
    state, cost_history = get_sequence_costs(arc_eager, words, heads, deps, actions)
    assert state.is_final()
    c0 = cost_history.pop(0)
    assert c0['S'] == 0.0
    c1 = cost_history.pop(0)
    assert c1['L-left'] == 0.0
    assert c1['R-right'] != 0.0
    c2 = cost_history.pop(0)
    assert c2['R-right'] != 0.0
    assert c2['B-ROOT'] == 0.0
    assert c2['D'] == 0.0
    c3 = cost_history.pop(0)
    assert c3['L-left'] == -1.0
 

def test_reduce_is_gold_at_break(arc_eager, vocab):
    words = ['a', 'b', 'c', 'd']
    heads = [1, 1, 3, 3]
    deps = ['left', 'B-ROOT', 'left', 'B-ROOT']
    actions = ['S', 'R-right', 'B-ROOT', 'D', 'S', 'L-left', 'S']
    state, cost_history = get_sequence_costs(arc_eager, words, heads, deps, actions)
    assert state.is_final(), state.print_state(words)
    c0 = cost_history.pop(0)
    c1 = cost_history.pop(0)
    c2 = cost_history.pop(0)
    c3 = cost_history.pop(0)
    assert c3['D'] == 0.0

annot_tuples = [
    (0, 'When', 'WRB', 11, 'advmod', 'O'),
    (1, 'Walter', 'NNP', 2, 'compound', 'B-PERSON'),
    (2, 'Rodgers', 'NNP', 11, 'nsubj', 'L-PERSON'),
    (3, ',', ',', 2, 'punct', 'O'),
    (4, 'our', 'PRP$', 6, 'poss', 'O'),
    (5, 'embedded', 'VBN', 6, 'amod', 'O'),
    (6, 'reporter', 'NN', 2, 'appos', 'O'),
    (7, 'with', 'IN', 6, 'prep', 'O'),
    (8, 'the', 'DT', 10, 'det', 'B-ORG'),
    (9, '3rd', 'NNP', 10, 'compound', 'I-ORG'),
    (10, 'Cavalry', 'NNP', 7, 'pobj', 'L-ORG'),
    (11, 'says', 'VBZ', 44, 'advcl', 'O'),
    (12, 'three', 'CD', 13, 'nummod', 'U-CARDINAL'),
    (13, 'battalions', 'NNS', 16, 'nsubj', 'O'),
    (14, 'of', 'IN', 13, 'prep', 'O'),
    (15, 'troops', 'NNS', 14, 'pobj', 'O'),
    (16, 'are', 'VBP', 11, 'ccomp', 'O'),
    (17, 'on', 'IN', 16, 'prep', 'O'),
    (18, 'the', 'DT', 19, 'det', 'O'),
    (19, 'ground', 'NN', 17, 'pobj', 'O'),
    (20, ',', ',', 17, 'punct', 'O'),
    (21, 'inside', 'IN', 17, 'prep', 'O'),
    (22, 'Baghdad', 'NNP', 21, 'pobj', 'U-GPE'),
    (23, 'itself', 'PRP', 22, 'appos', 'O'),
    (24, ',', ',', 16, 'punct', 'O'),
    (25, 'have', 'VBP', 26, 'aux', 'O'),
    (26, 'taken', 'VBN', 16, 'dep', 'O'),
    (27, 'up', 'RP', 26, 'prt', 'O'),
    (28, 'positions', 'NNS', 26, 'dobj', 'O'),
    (29, 'they', 'PRP', 31, 'nsubj', 'O'),
    (30, "'re", 'VBP', 31, 'aux', 'O'),
    (31, 'going', 'VBG', 26, 'parataxis', 'O'),
    (32, 'to', 'TO', 33, 'aux', 'O'),
    (33, 'spend', 'VB', 31, 'xcomp', 'O'),
    (34, 'the', 'DT', 35, 'det', 'B-TIME'), 
    (35, 'night', 'NN', 33, 'dobj', 'L-TIME'),
    (36, 'there', 'RB', 33, 'advmod', 'O'),
    (37, 'presumably', 'RB', 33, 'advmod', 'O'),
    (38, ',', ',', 44, 'punct', 'O'),
    (39, 'how', 'WRB', 40, 'advmod', 'O'),
    (40, 'many', 'JJ', 41, 'amod', 'O'),
    (41, 'soldiers', 'NNS', 44, 'pobj', 'O'),
    (42, 'are', 'VBP', 44, 'aux', 'O'),
    (43, 'we', 'PRP', 44, 'nsubj', 'O'),
    (44, 'talking', 'VBG', 44, 'ROOT', 'O'),
    (45, 'about', 'IN', 44, 'prep', 'O'),
    (46, 'right', 'RB', 47, 'advmod', 'O'),
    (47, 'now', 'RB', 44, 'advmod', 'O'),
    (48, '?', '.', 44, 'punct', 'O')]

def test_get_oracle_actions():
    doc = Doc(Vocab(), words=[t[1] for t in annot_tuples])
    parser = DependencyParser(doc.vocab)
    parser.moves.add_action(0, '')
    parser.moves.add_action(1, '')
    parser.moves.add_action(1, '')
    parser.moves.add_action(4, 'ROOT')
    for i, (id_, word, tag, head, dep, ent) in enumerate(annot_tuples):
        if head > i:
            parser.moves.add_action(2, dep)
        elif head < i:
            parser.moves.add_action(3, dep)
    ids, words, tags, heads, deps, ents = zip(*annot_tuples)
    heads, deps = projectivize(heads, deps)
    gold = GoldParse(doc, words=words, tags=tags, heads=heads, deps=deps)
    parser.moves.preprocess_gold(gold)
    actions = parser.moves.get_oracle_sequence(doc, gold)
