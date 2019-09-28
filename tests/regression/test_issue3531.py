# coding: utf8
from __future__ import unicode_literals

from spacy import displacy


def test_issue3531():
    """Test that displaCy renderer doesn't require "settings" key."""
    example_dep = {
        "words": [
            {"text": "But", "tag": "CCONJ"},
            {"text": "Google", "tag": "PROPN"},
            {"text": "is", "tag": "VERB"},
            {"text": "starting", "tag": "VERB"},
            {"text": "from", "tag": "ADP"},
            {"text": "behind.", "tag": "ADV"},
        ],
        "arcs": [
            {"start": 0, "end": 3, "label": "cc", "dir": "left"},
            {"start": 1, "end": 3, "label": "nsubj", "dir": "left"},
            {"start": 2, "end": 3, "label": "aux", "dir": "left"},
            {"start": 3, "end": 4, "label": "prep", "dir": "right"},
            {"start": 4, "end": 5, "label": "pcomp", "dir": "right"},
        ],
    }
    example_ent = {
        "text": "But Google is starting from behind.",
        "ents": [{"start": 4, "end": 10, "label": "ORG"}],
    }
    dep_html = displacy.render(example_dep, style="dep", manual=True)
    assert dep_html
    ent_html = displacy.render(example_ent, style="ent", manual=True)
    assert ent_html
