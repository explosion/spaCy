from __future__ import unicode_literals
import pytest

from spacy.en import English

def test_only_pre1():
    EN = English()
    assert len(EN("(")) == 1


def test_only_pre2():
    EN = English()
    assert len(EN("((")) == 2
