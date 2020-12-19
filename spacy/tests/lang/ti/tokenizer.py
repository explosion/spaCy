from __future__ import unicode_literals

from spacy.lang.ti import Tigrinya

nlp = Tigrinya()
text = '''"ንአስመራ ንኺድ!"'''
doc = nlp(text)
tok_exp = nlp.tokenizer.explain(text)
assert [t.text for t in doc if not t.is_space] == [t[1] for t in tok_exp]
for t in tok_exp:
    print(t[1], "\t", t[0])


