# coding: utf8
from __future__ import unicode_literals

from spacy.pipeline import EntityRecognizer

from spacy.lang.en import English
from spacy.tests.util import make_tempdir
from spacy.tokens import Span
from spacy.util import ensure_path


def test_issue4042():
    """Test that serialization of an NER works fine when new labels were added."""
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
        print("tmpdir", output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        ner1.to_disk(output_dir)

        nlp2 = English(vocab)
        ner2 = EntityRecognizer(vocab)
        ner2.from_disk(output_dir)
        print(ner2.labels)
        assert len(ner2.labels) == 2
