# coding: utf8
from __future__ import unicode_literals

from spacy.util import load_model_from_path
from spacy.lang.en import English

from ..util import make_tempdir


def test_issue4707():
    """Tests that disabled component names are also excluded from nlp.from_disk
    by default when loading a model.
    """
    nlp = English()
    nlp.add_pipe(nlp.create_pipe("sentencizer"))
    nlp.add_pipe(nlp.create_pipe("entity_ruler"))
    assert nlp.pipe_names == ["sentencizer", "entity_ruler"]
    exclude = ["tokenizer", "sentencizer"]
    with make_tempdir() as tmpdir:
        nlp.to_disk(tmpdir, exclude=exclude)
        new_nlp = load_model_from_path(tmpdir, disable=exclude)
    assert "sentencizer" not in new_nlp.pipe_names
    assert "entity_ruler" in new_nlp.pipe_names
