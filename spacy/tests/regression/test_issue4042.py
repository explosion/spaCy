# coding: utf8
from __future__ import unicode_literals

import spacy
from spacy.lang.en import English
from spacy.matcher import Matcher
from spacy.pipeline import EntityRuler
from spacy.tests.util import make_tempdir
from spacy.util import ensure_path


def test_issue4054(en_vocab):
    """Test that serialization of an EntityRuler before NER works fine."""
    nlp = English()

    # add ner pipe
    ner = nlp.create_pipe("ner")
    ner.add_label("SOME_LABEL")
    nlp.add_pipe(ner)
    nlp.begin_training()

    # Add matcher
    matcher = Matcher(nlp.vocab)
    pattern = [{"LOWER": "hello"}, {"IS_PUNCT": True}, {"LOWER": "world"}]
    matcher.add("HelloWorld", None, pattern)

    ruler = EntityRuler(nlp)
    patterns = [
        {"label": "ORG", "pattern": "Apple"},
        {"label": "GPE", "pattern": [{"lower": "san"}, {"lower": "francisco"}]},
    ]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler, before="ner")  # works fine with "after"

    with make_tempdir() as d:
        output_dir = ensure_path(d)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)

        spacy.load(output_dir)
