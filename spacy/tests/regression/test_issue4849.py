# coding: utf8
from __future__ import unicode_literals

from spacy.lang.en import English
from spacy.pipeline import EntityRuler


def test_issue4849():
    nlp = English()

    ruler = EntityRuler(
        nlp, patterns=[
            {"label": "PERSON", "pattern": 'joe biden', "id": 'joe-biden'},
            {"label": "PERSON", "pattern": 'bernie sanders', "id": 'bernie-sanders'},
        ],
        phrase_matcher_attr="LOWER"
    )

    nlp.add_pipe(ruler)

    text = """
    The left is starting to take aim at Democratic front-runner Joe Biden.
    Sen. Bernie Sanders joined in her criticism: "There is no 'middle ground' when it comes to climate policy."
    """

    # USING 1 PROCESS
    count_ents = 0
    for doc in nlp.pipe([text], n_process=1):
        count_ents += len([ent for ent in doc.ents if ent.ent_id > 0])
    assert(count_ents == 2)

    # USING 2 PROCESSES
    count_ents = 0
    for doc in nlp.pipe([text], n_process=2):
        count_ents += len([ent for ent in doc.ents if ent.ent_id > 0])
    assert (count_ents == 2)
