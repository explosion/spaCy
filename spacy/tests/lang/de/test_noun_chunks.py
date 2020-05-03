# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.language import Language
from spacy.vocab import Vocab
from spacy.tokens import Doc


@pytest.fixture
def nlp():
    return Language()


def test_noun_chunks_is_parsed_de():
    """Test that noun_chunks raises Value Error for 'de' language if Doc is not parsed. 
    To check this test, we're constructing a Doc
    with a new Vocab here and forcing is_parsed to 'False' 
    to make sure the noun chunks don't run.
    """
    try:
        doc = Doc(Vocab(), words=["Er", "lag", "auf", "seinem"])
        doc.is_parsed = False
        list(doc[0:3].noun_chunks)
    except ValueError:
        pass
    else:
        pytest.fail("Parsing did not catch a E029 ValueError for language 'de'")
