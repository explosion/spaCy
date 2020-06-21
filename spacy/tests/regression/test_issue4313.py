from collections import defaultdict

import pytest

from spacy.pipeline.defaults import default_ner
from spacy.pipeline import EntityRecognizer

from spacy.lang.en import English
from spacy.tokens import Span


# skipped after removing Beam stuff during the Example/GoldParse refactor
@pytest.mark.skip
def test_issue4313():
    """ This should not crash or exit with some strange error code """
    beam_width = 16
    beam_density = 0.0001
    nlp = English()
    config = {
        "learn_tokens": False,
        "min_action_freq": 30,
        "beam_width": 1,
        "beam_update_prob": 1.0,
    }
    ner = EntityRecognizer(nlp.vocab, default_ner(), **config)
    ner.add_label("SOME_LABEL")
    ner.begin_training([])
    nlp.add_pipe(ner)

    # add a new label to the doc
    doc = nlp("What do you think about Apple ?")
    assert len(ner.labels) == 1
    assert "SOME_LABEL" in ner.labels
    apple_ent = Span(doc, 5, 6, label="MY_ORG")
    doc.ents = list(doc.ents) + [apple_ent]

    # ensure the beam_parse still works with the new label
    docs = [doc]
    beams = nlp.entity.beam_parse(
        docs, beam_width=beam_width, beam_density=beam_density
    )

    for doc, beam in zip(docs, beams):
        entity_scores = defaultdict(float)
        for score, ents in nlp.entity.moves.get_beam_parses(beam):
            for start, end, label in ents:
                entity_scores[(start, end, label)] += score
