# coding: utf8
from __future__ import unicode_literals

from collections import defaultdict

import pytest
from spacy_lookup import Entity

from spacy.pipeline import EntityRecognizer

from spacy.lang.en import English


@pytest.mark.skip(reason="Issue not yet resolved (test crashes).")
def test_issue4313():
    beam_width = 16
    beam_density = 0.0001
    nlp = English()
    ner = EntityRecognizer(nlp.vocab)
    ner.begin_training([])
    nlp.add_pipe(ner)

    entity = Entity(keywords_list=["gradient", "neural network"], label="ML")
    nlp.add_pipe(entity, last=True)

    # this will trigger some tokens to be labeled as entity "ML"
    with nlp.disable_pipes("ner"):
        docs = list(
            nlp.pipe(
                [
                    "You have to be aware of a vanishing gradient when training a neural network"
                ]
            )
        )

    beams = nlp.entity.beam_parse(
        docs, beam_width=beam_width, beam_density=beam_density
    )

    for doc, beam in zip(docs, beams):
        entity_scores = defaultdict(float)
        for score, ents in nlp.entity.moves.get_beam_parses(beam):
            for start, end, label in ents:
                entity_scores[(start, end, label)] += score
