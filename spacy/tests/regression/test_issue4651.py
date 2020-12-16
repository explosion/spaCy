# coding: utf-8
from __future__ import unicode_literals

from spacy.lang.en import English
from spacy.pipeline import EntityRuler

from ..util import make_tempdir


def test_issue4651_with_phrase_matcher_attr():
    """Test that the EntityRuler PhraseMatcher is deserialize correctly using
    the method from_disk when the EntityRuler argument phrase_matcher_attr is
    specified.
    """
    text = "Spacy is a python library for nlp"

    nlp = English()
    ruler = EntityRuler(nlp, phrase_matcher_attr="LOWER")
    patterns = [{"label": "PYTHON_LIB", "pattern": "spacy", "id": "spaCy"}]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)

    doc = nlp(text)
    res = [(ent.text, ent.label_, ent.ent_id_) for ent in doc.ents]

    nlp_reloaded = English()
    with make_tempdir() as d:
        file_path = d / "entityruler"
        ruler.to_disk(file_path)
        ruler_reloaded = EntityRuler(nlp_reloaded).from_disk(file_path)

    nlp_reloaded.add_pipe(ruler_reloaded)
    doc_reloaded = nlp_reloaded(text)
    res_reloaded = [(ent.text, ent.label_, ent.ent_id_) for ent in doc_reloaded.ents]

    assert res == res_reloaded


def test_issue4651_without_phrase_matcher_attr():
    """Test that the EntityRuler PhraseMatcher is deserialize correctly using
    the method from_disk when the EntityRuler argument phrase_matcher_attr is
    not specified.
    """
    text = "Spacy is a python library for nlp"

    nlp = English()
    ruler = EntityRuler(nlp)
    patterns = [{"label": "PYTHON_LIB", "pattern": "spacy", "id": "spaCy"}]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)

    doc = nlp(text)
    res = [(ent.text, ent.label_, ent.ent_id_) for ent in doc.ents]

    nlp_reloaded = English()
    with make_tempdir() as d:
        file_path = d / "entityruler"
        ruler.to_disk(file_path)
        ruler_reloaded = EntityRuler(nlp_reloaded).from_disk(file_path)

    nlp_reloaded.add_pipe(ruler_reloaded)
    doc_reloaded = nlp_reloaded(text)
    res_reloaded = [(ent.text, ent.label_, ent.ent_id_) for ent in doc_reloaded.ents]

    assert res == res_reloaded
