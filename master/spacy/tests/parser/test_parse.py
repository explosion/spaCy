import pytest
from numpy.testing import assert_equal
from thinc.api import Adam

from spacy import registry, util
from spacy.attrs import DEP, NORM
from spacy.lang.en import English
from spacy.tokens import Doc
from spacy.training import Example
from spacy.vocab import Vocab

from ...pipeline import DependencyParser
from ...pipeline.dep_parser import DEFAULT_PARSER_MODEL
from ..util import apply_transition_sequence, make_tempdir
from ...pipeline.tok2vec import DEFAULT_TOK2VEC_MODEL

TRAIN_DATA = [
    (
        "They trade mortgage-backed securities.",
        {
            "heads": [1, 1, 4, 4, 5, 1, 1],
            "deps": ["nsubj", "ROOT", "compound", "punct", "nmod", "dobj", "punct"],
        },
    ),
    (
        "I like London and Berlin.",
        {
            "heads": [1, 1, 1, 2, 2, 1],
            "deps": ["nsubj", "ROOT", "dobj", "cc", "conj", "punct"],
        },
    ),
]


CONFLICTING_DATA = [
    (
        "I like London and Berlin.",
        {
            "heads": [1, 1, 1, 2, 2, 1],
            "deps": ["nsubj", "ROOT", "dobj", "cc", "conj", "punct"],
        },
    ),
    (
        "I like London and Berlin.",
        {
            "heads": [0, 0, 0, 0, 0, 0],
            "deps": ["ROOT", "nsubj", "nsubj", "cc", "conj", "punct"],
        },
    ),
]

PARTIAL_DATA = [
    (
        "I like London.",
        {
            "heads": [1, 1, 1, None],
            "deps": ["nsubj", "ROOT", "dobj", None],
        },
    ),
]

eps = 0.1


@pytest.fixture
def vocab():
    return Vocab(lex_attr_getters={NORM: lambda s: s})


@pytest.fixture
def parser(vocab):
    vocab.strings.add("ROOT")
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    parser = DependencyParser(vocab, model)
    parser.cfg["token_vector_width"] = 4
    parser.cfg["hidden_width"] = 32
    # parser.add_label('right')
    parser.add_label("left")
    parser.initialize(lambda: [_parser_example(parser)])
    sgd = Adam(0.001)

    for i in range(10):
        losses = {}
        doc = Doc(vocab, words=["a", "b", "c", "d"])
        example = Example.from_dict(
            doc, {"heads": [1, 1, 3, 3], "deps": ["left", "ROOT", "left", "ROOT"]}
        )
        parser.update([example], sgd=sgd, losses=losses)
    return parser


def _parser_example(parser):
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    gold = {"heads": [1, 1, 3, 3], "deps": ["right", "ROOT", "left", "ROOT"]}
    return Example.from_dict(doc, gold)


@pytest.mark.issue(2772)
def test_issue2772(en_vocab):
    """Test that deprojectivization doesn't mess up sentence boundaries."""
    # fmt: off
    words = ["When", "we", "write", "or", "communicate", "virtually", ",", "we", "can", "hide", "our", "true", "feelings", "."]
    # fmt: on
    # A tree with a non-projective (i.e. crossing) arc
    # The arcs (0, 4) and (2, 9) cross.
    heads = [4, 2, 9, 2, 2, 4, 9, 9, 9, 9, 12, 12, 9, 9]
    deps = ["dep"] * len(heads)
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    assert doc[1].is_sent_start is False


@pytest.mark.issue(3830)
def test_issue3830_no_subtok():
    """Test that the parser doesn't have subtok label if not learn_tokens"""
    config = {
        "learn_tokens": False,
    }
    model = registry.resolve({"model": DEFAULT_PARSER_MODEL}, validate=True)["model"]
    parser = DependencyParser(Vocab(), model, **config)
    parser.add_label("nsubj")
    assert "subtok" not in parser.labels
    parser.initialize(lambda: [_parser_example(parser)])
    assert "subtok" not in parser.labels


@pytest.mark.issue(3830)
def test_issue3830_with_subtok():
    """Test that the parser does have subtok label if learn_tokens=True."""
    config = {
        "learn_tokens": True,
    }
    model = registry.resolve({"model": DEFAULT_PARSER_MODEL}, validate=True)["model"]
    parser = DependencyParser(Vocab(), model, **config)
    parser.add_label("nsubj")
    assert "subtok" not in parser.labels
    parser.initialize(lambda: [_parser_example(parser)])
    assert "subtok" in parser.labels


@pytest.mark.issue(7716)
@pytest.mark.xfail(reason="Not fixed yet")
def test_partial_annotation(parser):
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    doc[2].is_sent_start = False
    # Note that if the following line is used, then doc[2].is_sent_start == False
    # doc[3].is_sent_start = False

    doc = parser(doc)
    assert doc[2].is_sent_start == False


def test_parser_root(en_vocab):
    words = ["i", "do", "n't", "have", "other", "assistance"]
    heads = [3, 3, 3, 3, 5, 3]
    deps = ["nsubj", "aux", "neg", "ROOT", "amod", "dobj"]
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    for t in doc:
        assert t.dep != 0, t.text


@pytest.mark.skip(
    reason="The step_through API was removed (but should be brought back)"
)
@pytest.mark.parametrize("words", [["Hello"]])
def test_parser_parse_one_word_sentence(en_vocab, en_parser, words):
    doc = Doc(en_vocab, words=words, heads=[0], deps=["ROOT"])
    assert len(doc) == 1
    with en_parser.step_through(doc) as _:  # noqa: F841
        pass
    assert doc[0].dep != 0


@pytest.mark.skip(
    reason="The step_through API was removed (but should be brought back)"
)
def test_parser_initial(en_vocab, en_parser):
    words = ["I", "ate", "the", "pizza", "with", "anchovies", "."]
    transition = ["L-nsubj", "S", "L-det"]
    doc = Doc(en_vocab, words=words)
    apply_transition_sequence(en_parser, doc, transition)
    assert doc[0].head.i == 1
    assert doc[1].head.i == 1
    assert doc[2].head.i == 3
    assert doc[3].head.i == 3


def test_parser_parse_subtrees(en_vocab, en_parser):
    words = ["The", "four", "wheels", "on", "the", "bus", "turned", "quickly"]
    heads = [2, 2, 6, 2, 5, 3, 6, 6]
    deps = ["dep"] * len(heads)
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    assert len(list(doc[2].lefts)) == 2
    assert len(list(doc[2].rights)) == 1
    assert len(list(doc[2].children)) == 3
    assert len(list(doc[5].lefts)) == 1
    assert len(list(doc[5].rights)) == 0
    assert len(list(doc[5].children)) == 1
    assert len(list(doc[2].subtree)) == 6


def test_parser_merge_pp(en_vocab):
    words = ["A", "phrase", "with", "another", "phrase", "occurs"]
    heads = [1, 5, 1, 4, 2, 5]
    deps = ["det", "nsubj", "prep", "det", "pobj", "ROOT"]
    pos = ["DET", "NOUN", "ADP", "DET", "NOUN", "VERB"]
    doc = Doc(en_vocab, words=words, deps=deps, heads=heads, pos=pos)
    with doc.retokenize() as retokenizer:
        for np in doc.noun_chunks:
            retokenizer.merge(np, attrs={"lemma": np.lemma_})
    assert doc[0].text == "A phrase"
    assert doc[1].text == "with"
    assert doc[2].text == "another phrase"
    assert doc[3].text == "occurs"


@pytest.mark.skip(
    reason="The step_through API was removed (but should be brought back)"
)
def test_parser_arc_eager_finalize_state(en_vocab, en_parser):
    words = ["a", "b", "c", "d", "e"]
    # right branching
    transition = ["R-nsubj", "D", "R-nsubj", "R-nsubj", "D", "R-ROOT"]
    tokens = Doc(en_vocab, words=words)
    apply_transition_sequence(en_parser, tokens, transition)

    assert tokens[0].n_lefts == 0
    assert tokens[0].n_rights == 2
    assert tokens[0].left_edge.i == 0
    assert tokens[0].right_edge.i == 4
    assert tokens[0].head.i == 0

    assert tokens[1].n_lefts == 0
    assert tokens[1].n_rights == 0
    assert tokens[1].left_edge.i == 1
    assert tokens[1].right_edge.i == 1
    assert tokens[1].head.i == 0

    assert tokens[2].n_lefts == 0
    assert tokens[2].n_rights == 2
    assert tokens[2].left_edge.i == 2
    assert tokens[2].right_edge.i == 4
    assert tokens[2].head.i == 0

    assert tokens[3].n_lefts == 0
    assert tokens[3].n_rights == 0
    assert tokens[3].left_edge.i == 3
    assert tokens[3].right_edge.i == 3
    assert tokens[3].head.i == 2

    assert tokens[4].n_lefts == 0
    assert tokens[4].n_rights == 0
    assert tokens[4].left_edge.i == 4
    assert tokens[4].right_edge.i == 4
    assert tokens[4].head.i == 2

    # left branching
    transition = ["S", "S", "S", "L-nsubj", "L-nsubj", "L-nsubj", "L-nsubj"]
    tokens = Doc(en_vocab, words=words)
    apply_transition_sequence(en_parser, tokens, transition)

    assert tokens[0].n_lefts == 0
    assert tokens[0].n_rights == 0
    assert tokens[0].left_edge.i == 0
    assert tokens[0].right_edge.i == 0
    assert tokens[0].head.i == 4

    assert tokens[1].n_lefts == 0
    assert tokens[1].n_rights == 0
    assert tokens[1].left_edge.i == 1
    assert tokens[1].right_edge.i == 1
    assert tokens[1].head.i == 4

    assert tokens[2].n_lefts == 0
    assert tokens[2].n_rights == 0
    assert tokens[2].left_edge.i == 2
    assert tokens[2].right_edge.i == 2
    assert tokens[2].head.i == 4

    assert tokens[3].n_lefts == 0
    assert tokens[3].n_rights == 0
    assert tokens[3].left_edge.i == 3
    assert tokens[3].right_edge.i == 3
    assert tokens[3].head.i == 4

    assert tokens[4].n_lefts == 4
    assert tokens[4].n_rights == 0
    assert tokens[4].left_edge.i == 0
    assert tokens[4].right_edge.i == 4
    assert tokens[4].head.i == 4


def test_parser_set_sent_starts(en_vocab):
    # fmt: off
    words = ['Ein', 'Satz', '.', 'Außerdem', 'ist', 'Zimmer', 'davon', 'überzeugt', ',', 'dass', 'auch', 'epige-', '\n', 'netische', 'Mechanismen', 'eine', 'Rolle', 'spielen', ',', 'also', 'Vorgänge', ',', 'die', '\n', 'sich', 'darauf', 'auswirken', ',', 'welche', 'Gene', 'abgelesen', 'werden', 'und', '\n', 'welche', 'nicht', '.', '\n']
    heads = [1, 1, 1, 30, 4, 4, 7, 4, 7, 17, 14, 14, 11, 14, 17, 16, 17, 6, 17, 20, 11, 20, 26, 22, 26, 26, 20, 26, 29, 31, 31, 25, 31, 32, 17, 4, 4, 36]
    deps = ['nk', 'ROOT', 'punct', 'mo', 'ROOT', 'sb', 'op', 'pd', 'punct', 'cp', 'mo', 'nk', '', 'nk', 'sb', 'nk', 'oa', 're', 'punct', 'mo', 'app', 'punct', 'sb', '', 'oa', 'op', 'rc', 'punct', 'nk', 'sb', 'oc', 're', 'cd', '', 'oa', 'ng', 'punct', '']
    # fmt: on
    doc = Doc(en_vocab, words=words, deps=deps, heads=heads)
    for i in range(len(words)):
        if i == 0 or i == 3:
            assert doc[i].is_sent_start is True
        else:
            assert doc[i].is_sent_start is False
    for sent in doc.sents:
        for token in sent:
            assert token.head in sent


def test_parser_constructor(en_vocab):
    config = {
        "learn_tokens": False,
        "min_action_freq": 30,
        "update_with_oracle_cut_size": 100,
    }
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    DependencyParser(en_vocab, model, **config)
    DependencyParser(en_vocab, model)


@pytest.mark.parametrize("pipe_name", ["parser", "beam_parser"])
def test_incomplete_data(pipe_name):
    # Test that the parser works with incomplete information
    nlp = English()
    parser = nlp.add_pipe(pipe_name)
    train_examples = []
    for text, annotations in PARTIAL_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for dep in annotations.get("deps", []):
            if dep is not None:
                parser.add_label(dep)
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    for i in range(150):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses[pipe_name] < 0.0001

    # test the trained model
    test_text = "I like securities."
    doc = nlp(test_text)
    assert doc[0].dep_ == "nsubj"
    assert doc[2].dep_ == "dobj"
    assert doc[0].head.i == 1
    assert doc[2].head.i == 1


@pytest.mark.parametrize("pipe_name", ["parser", "beam_parser"])
def test_overfitting_IO(pipe_name):
    # Simple test to try and quickly overfit the dependency parser (normal or beam)
    nlp = English()
    parser = nlp.add_pipe(pipe_name)
    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for dep in annotations.get("deps", []):
            parser.add_label(dep)
    optimizer = nlp.initialize()
    # run overfitting
    for i in range(200):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses[pipe_name] < 0.0001
    # test the trained model
    test_text = "I like securities."
    doc = nlp(test_text)
    assert doc[0].dep_ == "nsubj"
    assert doc[2].dep_ == "dobj"
    assert doc[3].dep_ == "punct"
    assert doc[0].head.i == 1
    assert doc[2].head.i == 1
    assert doc[3].head.i == 1
    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        assert doc2[0].dep_ == "nsubj"
        assert doc2[2].dep_ == "dobj"
        assert doc2[3].dep_ == "punct"
        assert doc2[0].head.i == 1
        assert doc2[2].head.i == 1
        assert doc2[3].head.i == 1

    # Make sure that running pipe twice, or comparing to call, always amounts to the same predictions
    texts = [
        "Just a sentence.",
        "Then one more sentence about London.",
        "Here is another one.",
        "I like London.",
    ]
    batch_deps_1 = [doc.to_array([DEP]) for doc in nlp.pipe(texts)]
    batch_deps_2 = [doc.to_array([DEP]) for doc in nlp.pipe(texts)]
    no_batch_deps = [doc.to_array([DEP]) for doc in [nlp(text) for text in texts]]
    assert_equal(batch_deps_1, batch_deps_2)
    assert_equal(batch_deps_1, no_batch_deps)


# fmt: off
@pytest.mark.slow
@pytest.mark.parametrize("pipe_name", ["parser", "beam_parser"])
@pytest.mark.parametrize(
    "parser_config",
    [
        # TransitionBasedParser V1
        ({"@architectures": "spacy.TransitionBasedParser.v1", "tok2vec": DEFAULT_TOK2VEC_MODEL, "state_type": "parser", "extra_state_tokens": False, "hidden_width": 64, "maxout_pieces": 2, "use_upper": True}),
        # TransitionBasedParser V2
        ({"@architectures": "spacy.TransitionBasedParser.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "state_type": "parser", "extra_state_tokens": False, "hidden_width": 64, "maxout_pieces": 2, "use_upper": True}),
    ],
)
# fmt: on
def test_parser_configs(pipe_name, parser_config):
    pipe_config = {"model": parser_config}
    nlp = English()
    parser = nlp.add_pipe(pipe_name, config=pipe_config)
    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for dep in annotations.get("deps", []):
            parser.add_label(dep)
    optimizer = nlp.initialize()
    for i in range(5):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)


def test_beam_parser_scores():
    # Test that we can get confidence values out of the beam_parser pipe
    beam_width = 16
    beam_density = 0.0001
    nlp = English()
    config = {
        "beam_width": beam_width,
        "beam_density": beam_density,
    }
    parser = nlp.add_pipe("beam_parser", config=config)
    train_examples = []
    for text, annotations in CONFLICTING_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for dep in annotations.get("deps", []):
            parser.add_label(dep)
    optimizer = nlp.initialize()

    # update a bit with conflicting data
    for i in range(10):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)

    # test the scores from the beam
    test_text = "I like securities."
    doc = nlp.make_doc(test_text)
    docs = [doc]
    beams = parser.predict(docs)
    head_scores, label_scores = parser.scored_parses(beams)

    for j in range(len(doc)):
        for label in parser.labels:
            label_score = label_scores[0][(j, label)]
            assert 0 - eps <= label_score <= 1 + eps
        for i in range(len(doc)):
            head_score = head_scores[0][(j, i)]
            assert 0 - eps <= head_score <= 1 + eps


def test_beam_overfitting_IO():
    # Simple test to try and quickly overfit the Beam dependency parser
    nlp = English()
    beam_width = 16
    beam_density = 0.0001
    config = {
        "beam_width": beam_width,
        "beam_density": beam_density,
    }
    parser = nlp.add_pipe("beam_parser", config=config)
    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for dep in annotations.get("deps", []):
            parser.add_label(dep)
    optimizer = nlp.initialize()
    # run overfitting
    for i in range(150):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["beam_parser"] < 0.0001
    # test the scores from the beam
    test_text = "I like securities."
    docs = [nlp.make_doc(test_text)]
    beams = parser.predict(docs)
    head_scores, label_scores = parser.scored_parses(beams)
    # we only processed one document
    head_scores = head_scores[0]
    label_scores = label_scores[0]
    # test label annotations: 0=nsubj, 2=dobj, 3=punct
    assert label_scores[(0, "nsubj")] == pytest.approx(1.0, abs=eps)
    assert label_scores[(0, "dobj")] == pytest.approx(0.0, abs=eps)
    assert label_scores[(0, "punct")] == pytest.approx(0.0, abs=eps)
    assert label_scores[(2, "nsubj")] == pytest.approx(0.0, abs=eps)
    assert label_scores[(2, "dobj")] == pytest.approx(1.0, abs=eps)
    assert label_scores[(2, "punct")] == pytest.approx(0.0, abs=eps)
    assert label_scores[(3, "nsubj")] == pytest.approx(0.0, abs=eps)
    assert label_scores[(3, "dobj")] == pytest.approx(0.0, abs=eps)
    assert label_scores[(3, "punct")] == pytest.approx(1.0, abs=eps)
    # test head annotations: the root is token at index 1
    assert head_scores[(0, 0)] == pytest.approx(0.0, abs=eps)
    assert head_scores[(0, 1)] == pytest.approx(1.0, abs=eps)
    assert head_scores[(0, 2)] == pytest.approx(0.0, abs=eps)
    assert head_scores[(2, 0)] == pytest.approx(0.0, abs=eps)
    assert head_scores[(2, 1)] == pytest.approx(1.0, abs=eps)
    assert head_scores[(2, 2)] == pytest.approx(0.0, abs=eps)
    assert head_scores[(3, 0)] == pytest.approx(0.0, abs=eps)
    assert head_scores[(3, 1)] == pytest.approx(1.0, abs=eps)
    assert head_scores[(3, 2)] == pytest.approx(0.0, abs=eps)

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        docs2 = [nlp2.make_doc(test_text)]
        parser2 = nlp2.get_pipe("beam_parser")
        beams2 = parser2.predict(docs2)
        head_scores2, label_scores2 = parser2.scored_parses(beams2)
        # we only processed one document
        head_scores2 = head_scores2[0]
        label_scores2 = label_scores2[0]
        # check the results again
        assert label_scores2[(0, "nsubj")] == pytest.approx(1.0, abs=eps)
        assert label_scores2[(0, "dobj")] == pytest.approx(0.0, abs=eps)
        assert label_scores2[(0, "punct")] == pytest.approx(0.0, abs=eps)
        assert label_scores2[(2, "nsubj")] == pytest.approx(0.0, abs=eps)
        assert label_scores2[(2, "dobj")] == pytest.approx(1.0, abs=eps)
        assert label_scores2[(2, "punct")] == pytest.approx(0.0, abs=eps)
        assert label_scores2[(3, "nsubj")] == pytest.approx(0.0, abs=eps)
        assert label_scores2[(3, "dobj")] == pytest.approx(0.0, abs=eps)
        assert label_scores2[(3, "punct")] == pytest.approx(1.0, abs=eps)
        assert head_scores2[(0, 0)] == pytest.approx(0.0, abs=eps)
        assert head_scores2[(0, 1)] == pytest.approx(1.0, abs=eps)
        assert head_scores2[(0, 2)] == pytest.approx(0.0, abs=eps)
        assert head_scores2[(2, 0)] == pytest.approx(0.0, abs=eps)
        assert head_scores2[(2, 1)] == pytest.approx(1.0, abs=eps)
        assert head_scores2[(2, 2)] == pytest.approx(0.0, abs=eps)
        assert head_scores2[(3, 0)] == pytest.approx(0.0, abs=eps)
        assert head_scores2[(3, 1)] == pytest.approx(1.0, abs=eps)
        assert head_scores2[(3, 2)] == pytest.approx(0.0, abs=eps)
