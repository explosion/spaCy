# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.kb import KnowledgeBase
from spacy.util import ensure_path
from spacy.lang.en import English

from ..util import make_tempdir


def test_issue4674():
    """Test that setting entities with overlapping identifiers does not mess up IO"""
    nlp = English()
    kb = KnowledgeBase(nlp.vocab, entity_vector_length=3)

    vector1 = [0.9, 1.1, 1.01]
    vector2 = [1.8, 2.25, 2.01]
    with pytest.warns(UserWarning):
        kb.set_entities(
            entity_list=["Q1", "Q1"],
            freq_list=[32, 111],
            vector_list=[vector1, vector2],
        )

    assert kb.get_size_entities() == 1

    # dumping to file & loading back in
    with make_tempdir() as d:
        dir_path = ensure_path(d)
        if not dir_path.exists():
            dir_path.mkdir()
        file_path = dir_path / "kb"
        kb.dump(str(file_path))

        kb2 = KnowledgeBase(vocab=nlp.vocab, entity_vector_length=3)
        kb2.load_bulk(str(file_path))

    assert kb2.get_size_entities() == 1
