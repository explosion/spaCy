import pytest
from spacy.lang.en import English
from spacy.training import Example
from spacy.tokens import Doc
from spacy import util

from ..util import apply_transition_sequence, make_tempdir


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


def test_overfitting_IO():
    # Simple test to try and quickly overfit the dependency parser - ensuring the ML models work correctly
    nlp = English()
    parser = nlp.add_pipe("parser")
    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for dep in annotations.get("deps", []):
            parser.add_label(dep)
    optimizer = nlp.initialize()
    for i in range(100):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["parser"] < 0.0001
    # test the trained model
    test_text = "I like securities."
    doc = nlp(test_text)
    assert doc[0].dep_ == "nsubj"
    assert doc[2].dep_ == "dobj"
    assert doc[3].dep_ == "punct"
    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        assert doc2[0].dep_ == "nsubj"
        assert doc2[2].dep_ == "dobj"
        assert doc2[3].dep_ == "punct"
