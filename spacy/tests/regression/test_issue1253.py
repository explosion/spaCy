from __future__ import unicode_literals
import pytest
import spacy


def ss(tt):
    for i in range(len(tt)-1):
        for j in range(i+1, len(tt)):
            tt[i:j].root


@pytest.mark.models('en')
def test_access_parse_for_merged():
    nlp = spacy.load('en_core_web_sm')
    t_t = nlp.tokenizer("Highly rated - I'll definitely")
    nlp.tagger(t_t)
    nlp.parser(t_t)
    nlp.parser(t_t)
    ss(t_t)

