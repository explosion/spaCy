# coding: utf-8
from __future__ import unicode_literals

from spacy.util import ensure_path
from spacy.kb import KnowledgeBase

from ..util import make_tempdir


def test_serialize_kb_disk(en_vocab):
    # baseline assertions
    kb1 = _get_dummy_kb(en_vocab)
    _check_kb(kb1)

    # dumping to file & loading back in
    with make_tempdir() as d:
        dir_path = ensure_path(d)
        if not dir_path.exists():
            dir_path.mkdir()
        file_path = dir_path / "kb"
        kb1.dump(str(file_path))

        kb2 = KnowledgeBase(vocab=en_vocab, entity_vector_length=3)
        kb2.load_bulk(str(file_path))

    # final assertions
    _check_kb(kb2)


def _get_dummy_kb(vocab):
    kb = KnowledgeBase(vocab=vocab, entity_vector_length=3)

    kb.add_entity(entity="Q53", freq=33, entity_vector=[0, 5, 3])
    kb.add_entity(entity="Q17", freq=2, entity_vector=[7, 1, 0])
    kb.add_entity(entity="Q007", freq=7, entity_vector=[0, 0, 7])
    kb.add_entity(entity="Q44", freq=342, entity_vector=[4, 4, 4])

    kb.add_alias(alias="double07", entities=["Q17", "Q007"], probabilities=[0.1, 0.9])
    kb.add_alias(
        alias="guy",
        entities=["Q53", "Q007", "Q17", "Q44"],
        probabilities=[0.3, 0.3, 0.2, 0.1],
    )
    kb.add_alias(alias="random", entities=["Q007"], probabilities=[1.0])

    return kb


def _check_kb(kb):
    # check entities
    assert kb.get_size_entities() == 4
    for entity_string in ["Q53", "Q17", "Q007", "Q44"]:
        assert entity_string in kb.get_entity_strings()
    for entity_string in ["", "Q0"]:
        assert entity_string not in kb.get_entity_strings()

    # check aliases
    assert kb.get_size_aliases() == 3
    for alias_string in ["double07", "guy", "random"]:
        assert alias_string in kb.get_alias_strings()
    for alias_string in ["nothingness", "", "randomnoise"]:
        assert alias_string not in kb.get_alias_strings()

    # check candidates & probabilities
    candidates = sorted(kb.get_candidates("double07"), key=lambda x: x.entity_)
    assert len(candidates) == 2

    assert candidates[0].entity_ == "Q007"
    assert 6.999 < candidates[0].entity_freq < 7.01
    assert candidates[0].entity_vector == [0, 0, 7]
    assert candidates[0].alias_ == "double07"
    assert 0.899 < candidates[0].prior_prob < 0.901

    assert candidates[1].entity_ == "Q17"
    assert 1.99 < candidates[1].entity_freq < 2.01
    assert candidates[1].entity_vector == [7, 1, 0]
    assert candidates[1].alias_ == "double07"
    assert 0.099 < candidates[1].prior_prob < 0.101
