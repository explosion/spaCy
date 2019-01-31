from __future__ import unicode_literals
import pytest
import spacy


@pytest.mark.models('fr')
def test_issue1959(FR):
    texts = ['Je suis la mauvaise herbe', "Me, myself and moi"]
    for text in texts:
        FR(text)
