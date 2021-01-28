import pytest
from ..util import make_tempdir


def test_issue6730(en_vocab):
    """Ensure that the KB does not accept empty strings, but otherwise IO works fine."""
    from spacy.kb import KnowledgeBase

    kb = KnowledgeBase(en_vocab, entity_vector_length=3)
    kb.add_entity(entity="1", freq=148, entity_vector=[1, 2, 3])

    with pytest.raises(ValueError):
        kb.add_alias(alias="", entities=["1"], probabilities=[0.4])
    assert kb.contains_alias("") is False

    kb.add_alias(alias="x", entities=["1"], probabilities=[0.2])
    kb.add_alias(alias="y", entities=["1"], probabilities=[0.1])

    with make_tempdir() as tmp_dir:
        kb.to_disk(tmp_dir)
        kb.from_disk(tmp_dir)
    assert kb.get_size_aliases() == 2
    assert set(kb.get_alias_strings()) == {"x", "y"}
