# coding: utf8
from __future__ import unicode_literals

import spacy
from spacy.lang.en import English
from spacy.pipeline import EntityRuler
from spacy.tests.util import make_tempdir
from spacy.util import ensure_path


def test_issue4042():
    """Test that serialization of an EntityRuler before NER works fine."""
    nlp = English()

    # add ner pipe
    ner = nlp.create_pipe("ner")
    ner.add_label("SOME_LABEL")
    nlp.add_pipe(ner)
    nlp.begin_training()

    # Add entity ruler
    ruler = EntityRuler(nlp)
    patterns = [
        {"label": "MY_ORG", "pattern": "Apple"},
        {"label": "MY_GPE", "pattern": [{"lower": "san"}, {"lower": "francisco"}]},
    ]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler, before="ner")  # works fine with "after"
    doc1 = nlp("What do you think about Apple ?")
    assert doc1.ents[0].label_ == "MY_ORG"

    with make_tempdir() as d:
        output_dir = ensure_path(d)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)

        nlp2 = spacy.load(output_dir)
        doc2 = nlp2("What do you think about Apple ?")
        assert doc2.ents[0].label_ == "MY_ORG"
