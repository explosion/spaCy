from __future__ import unicode_literals

import pytest


@pytest.mark.models('en')
def test_issue1207(EN):
    text = 'Employees are recruiting talented staffers from overseas.'
    doc = EN(text)

    assert [i.text for i in doc.noun_chunks] == ['Employees', 'talented staffers']
    sent = list(doc.sents)[0]
    assert [i.text for i in sent.noun_chunks] == ['Employees', 'talented staffers']
