from __future__ import unicode_literals
import pytest

import spacy
from spacy.attrs import ORTH


@pytest.mark.models
def test_issue429():

    nlp = spacy.load('en', parser=False)


    def merge_phrases(matcher, doc, i, matches):
      if i != len(matches) - 1:
        return None
      spans = [(ent_id, label, doc[start:end]) for ent_id, label, start, end in matches]
      for ent_id, label, span in spans:
        span.merge('NNP' if label else span.root.tag_, span.text, nlp.vocab.strings[label])

    doc = nlp('a')
    nlp.matcher.add('key', label='TEST', attrs={}, specs=[[{ORTH: 'a'}]], on_match=merge_phrases)
    doc = nlp.tokenizer('a b c')
    nlp.tagger(doc)
    nlp.matcher(doc)
        
    for word in doc:
        print(word.text, word.ent_iob_, word.ent_type_)
    nlp.entity(doc)
