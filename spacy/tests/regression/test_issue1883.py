'''Check Matcher can be unpickled correctly.'''
from __future__ import unicode_literals

import copy

from ... vocab import Vocab
from ... matcher import Matcher
from ... tokens import Doc


def test_issue1883():
    m = Matcher(Vocab())
    m.add('pat1', None, [{'orth': 'hello'}])
    doc = Doc(m.vocab, words=['hello'])
    assert len(m(doc)) == 1
    m2 = copy.deepcopy(m)
    doc2 = Doc(m2.vocab, words=['hello'])
    assert len(m2(doc2)) == 1
