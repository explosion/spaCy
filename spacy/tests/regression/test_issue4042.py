# coding: utf8
from __future__ import unicode_literals

import spacy
from spacy.pipeline import EntityRecognizer, EntityRuler
from spacy.lang.en import English
from spacy.tokens import Span
from spacy.util import ensure_path

from ..util import make_tempdir


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


def test_issue4042_bug2():
    """
    Test that serialization of an NER works fine when new labels were added.
    This is the second bug of two bugs underlying the issue 4042.
    """
    nlp1 = English()
    vocab = nlp1.vocab

    # add ner pipe
    ner1 = nlp1.create_pipe("ner")
    ner1.add_label("SOME_LABEL")
    nlp1.add_pipe(ner1)
    nlp1.begin_training()

    # add a new label to the doc
    doc1 = nlp1("What do you think about Apple ?")
    assert len(ner1.labels) == 1
    assert "SOME_LABEL" in ner1.labels
    apple_ent = Span(doc1, 5, 6, label="MY_ORG")
    doc1.ents = list(doc1.ents) + [apple_ent]

    # reapply the NER - at this point it should resize itself
    ner1(doc1)
    assert len(ner1.labels) == 2
    assert "SOME_LABEL" in ner1.labels
    assert "MY_ORG" in ner1.labels

    with make_tempdir() as d:
        # assert IO goes fine
        output_dir = ensure_path(d)
        if not output_dir.exists():
            output_dir.mkdir()
        ner1.to_disk(output_dir)

        ner2 = EntityRecognizer(vocab)
        ner2.from_disk(output_dir)
        assert len(ner2.labels) == 2
