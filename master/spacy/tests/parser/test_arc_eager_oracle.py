import pytest
from spacy.vocab import Vocab
from spacy import registry
from spacy.training import Example
from spacy.pipeline import DependencyParser
from spacy.tokens import Doc
from spacy.pipeline._parser_internals.nonproj import projectivize
from spacy.pipeline._parser_internals.arc_eager import ArcEager
from spacy.pipeline.dep_parser import DEFAULT_PARSER_MODEL


def get_sequence_costs(M, words, heads, deps, transitions):
    doc = Doc(Vocab(), words=words)
    example = Example.from_dict(doc, {"heads": heads, "deps": deps})
    states, golds, _ = M.init_gold_batch([example])
    state = states[0]
    gold = golds[0]
    cost_history = []
    for gold_action in transitions:
        gold.update(state)
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


@pytest.mark.issue(7056)
def test_issue7056():
    """Test that the Unshift transition works properly, and doesn't cause
    sentence segmentation errors."""
    vocab = Vocab()
    ae = ArcEager(
        vocab.strings, ArcEager.get_actions(left_labels=["amod"], right_labels=["pobj"])
    )
    doc = Doc(vocab, words="Severe pain , after trauma".split())
    state = ae.init_batch([doc])[0]
    ae.apply_transition(state, "S")
    ae.apply_transition(state, "L-amod")
    ae.apply_transition(state, "S")
    ae.apply_transition(state, "S")
    ae.apply_transition(state, "S")
    ae.apply_transition(state, "R-pobj")
    ae.apply_transition(state, "D")
    ae.apply_transition(state, "D")
    ae.apply_transition(state, "D")
    assert not state.eol()


def test_oracle_four_words(arc_eager, vocab):
    words = ["a", "b", "c", "d"]
    heads = [1, 1, 3, 3]
    deps = ["left", "ROOT", "left", "ROOT"]
    for dep in deps:
        arc_eager.add_action(2, dep)  # Left
        arc_eager.add_action(3, dep)  # Right
    actions = ["S", "L-left", "B-ROOT", "S", "D", "S", "L-left", "S", "D"]
    state, cost_history = get_sequence_costs(arc_eager, words, heads, deps, actions)
    expected_gold = [
        ["S"],
        ["B-ROOT", "L-left"],
        ["B-ROOT"],
        ["S"],
        ["D"],
        ["S"],
        ["L-left"],
        ["S"],
        ["D"],
    ]
    assert state.is_final()
    for i, state_costs in enumerate(cost_history):
        # Check gold moves is 0 cost
        golds = [act for act, cost in state_costs.items() if cost < 1]
        assert golds == expected_gold[i], (i, golds, expected_gold[i])


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
    ids, words, tags, heads, deps, ents = [], [], [], [], [], []
    for id_, word, tag, head, dep, ent in annot_tuples:
        ids.append(id_)
        words.append(word)
        tags.append(tag)
        heads.append(head)
        deps.append(dep)
        ents.append(ent)
    doc = Doc(Vocab(), words=[t[1] for t in annot_tuples])
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    parser = DependencyParser(doc.vocab, model)
    parser.moves.add_action(0, "")
    parser.moves.add_action(1, "")
    parser.moves.add_action(1, "")
    parser.moves.add_action(4, "ROOT")
    heads, deps = projectivize(heads, deps)
    for i, (head, dep) in enumerate(zip(heads, deps)):
        if head > i:
            parser.moves.add_action(2, dep)
        elif head < i:
            parser.moves.add_action(3, dep)
    example = Example.from_dict(
        doc, {"words": words, "tags": tags, "heads": heads, "deps": deps}
    )
    parser.moves.get_oracle_sequence(example)


def test_oracle_dev_sentence(vocab, arc_eager):
    words_deps_heads = """
        Rolls-Royce nn Inc.
        Motor nn Inc.
        Cars nn Inc.
        Inc. nsubj said
        said ROOT said
        it nsubj expects
        expects ccomp said
        its poss sales
        U.S. nn sales
        sales nsubj steady
        to aux steady
        remain cop steady
        steady xcomp expects
        at prep steady
        about quantmod 1,200
        1,200 num cars
        cars pobj at
        in prep steady
        1990 pobj in
        . punct said
    """
    expected_transitions = [
        "S",  # Shift "Rolls-Royce"
        "S",  # Shift 'Motor'
        "S",  # Shift 'Cars'
        "L-nn",  # Attach 'Cars' to 'Inc.'
        "L-nn",  # Attach 'Motor' to 'Inc.'
        "L-nn",  # Attach 'Rolls-Royce' to 'Inc.'
        "S",  # Shift "Inc."
        "L-nsubj",  # Attach 'Inc.' to 'said'
        "S",  # Shift 'said'
        "S",  # Shift 'it'
        "L-nsubj",  # Attach 'it.' to 'expects'
        "R-ccomp",  # Attach 'expects' to 'said'
        "S",  # Shift 'its'
        "S",  # Shift 'U.S.'
        "L-nn",  # Attach 'U.S.' to 'sales'
        "L-poss",  # Attach 'its' to 'sales'
        "S",  # Shift 'sales'
        "S",  # Shift 'to'
        "S",  # Shift 'remain'
        "L-cop",  # Attach 'remain' to 'steady'
        "L-aux",  # Attach 'to' to 'steady'
        "L-nsubj",  # Attach 'sales' to 'steady'
        "R-xcomp",  # Attach 'steady' to 'expects'
        "R-prep",  # Attach 'at' to 'steady'
        "S",  # Shift 'about'
        "L-quantmod",  # Attach "about" to "1,200"
        "S",  # Shift "1,200"
        "L-num",  # Attach "1,200" to "cars"
        "R-pobj",  # Attach "cars" to "at"
        "D",  # Reduce "cars"
        "D",  # Reduce "at"
        "R-prep",  # Attach "in" to "steady"
        "R-pobj",  # Attach "1990" to "in"
        "D",  # Reduce "1990"
        "D",  # Reduce "in"
        "D",  # Reduce "steady"
        "D",  # Reduce "expects"
        "R-punct",  # Attach "." to "said"
        "D",  # Reduce "."
        "D",  # Reduce "said"
    ]

    gold_words = []
    gold_deps = []
    gold_heads = []
    for line in words_deps_heads.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        word, dep, head = line.split()
        gold_words.append(word)
        gold_deps.append(dep)
        gold_heads.append(head)
    gold_heads = [gold_words.index(head) for head in gold_heads]
    for dep in gold_deps:
        arc_eager.add_action(2, dep)  # Left
        arc_eager.add_action(3, dep)  # Right
    doc = Doc(Vocab(), words=gold_words)
    example = Example.from_dict(doc, {"heads": gold_heads, "deps": gold_deps})
    ae_oracle_actions = arc_eager.get_oracle_sequence(example, _debug=False)
    ae_oracle_actions = [arc_eager.get_class_name(i) for i in ae_oracle_actions]
    assert ae_oracle_actions == expected_transitions


def test_oracle_bad_tokenization(vocab, arc_eager):
    words_deps_heads = """
        [catalase] dep is
        : punct is
        that nsubj is
        is root is
        bad comp is
    """

    gold_words = []
    gold_deps = []
    gold_heads = []
    for line in words_deps_heads.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        word, dep, head = line.split()
        gold_words.append(word)
        gold_deps.append(dep)
        gold_heads.append(head)
    gold_heads = [gold_words.index(head) for head in gold_heads]
    for dep in gold_deps:
        arc_eager.add_action(2, dep)  # Left
        arc_eager.add_action(3, dep)  # Right
    reference = Doc(Vocab(), words=gold_words, deps=gold_deps, heads=gold_heads)
    predicted = Doc(
        reference.vocab, words=["[", "catalase", "]", ":", "that", "is", "bad"]
    )
    example = Example(predicted=predicted, reference=reference)
    ae_oracle_actions = arc_eager.get_oracle_sequence(example, _debug=False)
    ae_oracle_actions = [arc_eager.get_class_name(i) for i in ae_oracle_actions]
    assert ae_oracle_actions
