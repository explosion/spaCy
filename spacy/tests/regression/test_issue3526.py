# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Span
from spacy.language import Language
from spacy.pipeline import EntityRuler
from spacy import load
import srsly

from ..util import make_tempdir


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


def test_entity_ruler_existing_overwrite_serialize_bytes(patterns, en_vocab):
    nlp = Language(vocab=en_vocab)
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    ruler_bytes = ruler.to_bytes()
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    assert ruler.overwrite
    new_ruler = EntityRuler(nlp)
    new_ruler = new_ruler.from_bytes(ruler_bytes)
    assert len(new_ruler) == len(ruler)
    assert len(new_ruler.labels) == 4
    assert new_ruler.overwrite == ruler.overwrite
    assert new_ruler.ent_id_sep == ruler.ent_id_sep


def test_entity_ruler_existing_bytes_old_format_safe(patterns, en_vocab):
    nlp = Language(vocab=en_vocab)
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    bytes_old_style = srsly.msgpack_dumps(ruler.patterns)
    new_ruler = EntityRuler(nlp)
    new_ruler = new_ruler.from_bytes(bytes_old_style)
    assert len(new_ruler) == len(ruler)
    for pattern in ruler.patterns:
        assert pattern in new_ruler.patterns
    assert new_ruler.overwrite is not ruler.overwrite


def test_entity_ruler_from_disk_old_format_safe(patterns, en_vocab):
    nlp = Language(vocab=en_vocab)
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    with make_tempdir() as tmpdir:
        out_file = tmpdir / "entity_ruler"
        srsly.write_jsonl(out_file.with_suffix(".jsonl"), ruler.patterns)
        new_ruler = EntityRuler(nlp).from_disk(out_file)
        for pattern in ruler.patterns:
            assert pattern in new_ruler.patterns
        assert len(new_ruler) == len(ruler)
        assert new_ruler.overwrite is not ruler.overwrite


def test_entity_ruler_in_pipeline_from_issue(patterns, en_vocab):
    nlp = Language(vocab=en_vocab)
    ruler = EntityRuler(nlp, overwrite_ents=True)

    ruler.add_patterns([{"label": "ORG", "pattern": "Apple"}])
    nlp.add_pipe(ruler)
    with make_tempdir() as tmpdir:
        nlp.to_disk(tmpdir)
        ruler = nlp.get_pipe("entity_ruler")
        assert ruler.patterns == [{"label": "ORG", "pattern": "Apple"}]
        assert ruler.overwrite is True
        nlp2 = load(tmpdir)
        new_ruler = nlp2.get_pipe("entity_ruler")
        assert new_ruler.patterns == [{"label": "ORG", "pattern": "Apple"}]
        assert new_ruler.overwrite is True
