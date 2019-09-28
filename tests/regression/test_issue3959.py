# coding: utf8
from __future__ import unicode_literals

from spacy.lang.en import English
from ..util import make_tempdir


def test_issue3959():
    """ Ensure that a modified pos attribute is serialized correctly."""
    nlp = English()
    doc = nlp(
        "displaCy uses JavaScript, SVG and CSS to show you how computers understand language"
    )
    assert doc[0].pos_ == ""

    doc[0].pos_ = "NOUN"
    assert doc[0].pos_ == "NOUN"

    # usually this is already True when starting from proper models instead of blank English
    doc.is_tagged = True

    with make_tempdir() as tmp_dir:
        file_path = tmp_dir / "my_doc"
        doc.to_disk(file_path)

        doc2 = nlp("")
        doc2.from_disk(file_path)

        assert doc2[0].pos_ == "NOUN"
