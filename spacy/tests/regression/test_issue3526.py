# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Span
from spacy.language import Language
from spacy.pipeline import EntityRuler
from spacy import load
from tempfile import TemporaryDirectory

@pytest.fixture
def nlp():
    return Language()


@pytest.fixture
def patterns():
    return [
        {"label": "HELLO", "pattern": "hello world"},
        {"label": "BYE", "pattern": [{"LOWER": "bye"}, {"LOWER": "bye"}]},
        {"label": "HELLO", "pattern": [{"ORTH": "HELLO"}]},
        {"label": "COMPLEX", "pattern": [{"ORTH": "foo", "OP": "*"}]},
        {"label": "TECH_ORG", "pattern": "Apple", "id": "a1"},
    ]


@pytest.fixture
def add_ent():
    def add_ent_component(doc):
        doc.ents = [Span(doc, 0, 3, label=doc.vocab.strings["ORG"])]
        return doc

    return add_ent_component


def test_entity_ruler_existing_overwrite_serialize_bytes(nlp, patterns):
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    ruler_bytes = ruler.to_bytes()
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    assert ruler.overwrite
    new_ruler = EntityRuler(nlp)
    new_ruler.from_bytes(ruler_bytes)
    new_ruler = new_ruler.from_bytes(ruler_bytes)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    assert new_ruler.overwrite == ruler.overwrite
    assert new_ruler.ent_id_sep == ruler.ent_id_sep

def test_entity_ruler_in_pipeline_from_issue(nlp, patterns):
    nlp1 = load('en_core_web_sm')
    ruler = EntityRuler(nlp, overwrite_ents=True)

    ruler.add_patterns([{"label": "ORG", "pattern": "Apple"}])
    nlp1.add_pipe(ruler)
    with TemporaryDirectory() as tmpdir:
        nlp1.to_disk(tmpdir)
        assert nlp1.pipeline[-1][-1].patterns == [{"label": "ORG", "pattern": "Apple"}]
        assert nlp1.pipeline[-1][-1].overwrite is True
        nlp2 = load(tmpdir)
        assert nlp2.pipeline[-1][-1].patterns == [{"label": "ORG", "pattern": "Apple"}]
        assert nlp2.pipeline[-1][-1].overwrite is True