from __future__ import unicode_literals
from ...tokenizer import Tokenizer
from ...symbols import ORTH, LEMMA, POS
from ...lang.en import English

def test_issue1250_cached_special_cases():
    nlp = English()
    nlp.tokenizer.add_special_case(u'reimbur', [{ORTH: u'reimbur', LEMMA: u'reimburse', POS: u'VERB'}])

    lemmas = [w.lemma_ for w in nlp(u'reimbur, reimbur...')]
    assert lemmas == ['reimburse', ',', 'reimburse', '...']
    lemmas = [w.lemma_ for w in nlp(u'reimbur, reimbur...')]
    assert lemmas == ['reimburse', ',', 'reimburse', '...']
