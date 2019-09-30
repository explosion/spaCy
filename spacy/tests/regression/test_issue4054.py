# coding: utf8
from __future__ import unicode_literals

from spacy.vocab import Vocab

import spacy
from spacy.lang.en import English
from spacy.tests.util import make_tempdir
from spacy.util import ensure_path


def test_issue4054(en_vocab):
    """Test that a new blank model can be made with a vocab from file,
    and that serialization does not drop the language at any point."""
    nlp1 = English()
    vocab1 = nlp1.vocab

    with make_tempdir() as d:
        vocab_dir = ensure_path(d / "vocab")
        if not vocab_dir.exists():
            vocab_dir.mkdir()
        vocab1.to_disk(vocab_dir)

        vocab2 = Vocab().from_disk(vocab_dir)
        print("lang", vocab2.lang)
        nlp2 = spacy.blank("en", vocab=vocab2)

        nlp_dir = ensure_path(d / "nlp")
        if not nlp_dir.exists():
            nlp_dir.mkdir()
        nlp2.to_disk(nlp_dir)
        nlp3 = spacy.load(nlp_dir)
        assert nlp3.lang == "en"
