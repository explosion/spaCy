# coding: utf8
from __future__ import unicode_literals

from spacy.lang.en import English
from spacy.pipeline import merge_entities, EntityRuler


def test_issue5918():
    # Test edge case when merging entities.
    nlp = English()
    patterns = [
        {"label": "ORG", "pattern": "Digicon Inc"},
        {"label": "ORG", "pattern": "Rotan Mosle Inc's"},
        {"label": "ORG", "pattern": "Rotan Mosle Technology Partners Ltd"},
    ]
    ruler = EntityRuler(nlp)
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)

    text = """
        Digicon Inc said it has completed the previously-announced disposition
        of its computer systems division to an investment group led by
        Rotan Mosle Inc's Rotan Mosle Technology Partners Ltd affiliate.
        """
    doc = nlp(text)
    assert len(doc.ents) == 3
    # make it so that the third span's head is within the entity (ent_iob=I)
    # bug #5918 would wrongly transfer that I to the full entity, resulting in 2 instead of 3 final ents.
    doc[29].head = doc[33]
    doc = merge_entities(doc)
    assert len(doc.ents) == 3
