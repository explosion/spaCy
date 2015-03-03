from __future__ import unicode_literals
from spacy.en import English

EN = English()


def test_subtrees():
    sent = EN('The four wheels on the bus turned quickly')
    wheels = sent[2]
    bus = sent[5]
    assert len(list(wheels.lefts)) == 2
    assert len(list(wheels.rights)) == 1
    assert len(list(wheels.children)) == 3
    assert len(list(bus.lefts)) == 1
    assert len(list(bus.rights)) == 0
    assert len(list(bus.children)) == 1

    assert len(list(wheels.subtree)) == 6

