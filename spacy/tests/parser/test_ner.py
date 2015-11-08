from __future__ import unicode_literals, print_function
import pytest

@pytest.mark.models
def test_simple_types(EN):
    tokens = EN(u'Mr. Best flew to New York on Saturday morning.')
    ents = list(tokens.ents)
    assert ents[0].start == 1
    assert ents[0].end == 2
    assert ents[0].label_ == 'PERSON'
    assert ents[1].start == 4
    assert ents[1].end == 6
    assert ents[1].label_ == 'GPE'


@pytest.mark.models
def test_consistency_bug(EN):
    '''Test an arbitrary sequence-consistency bug encountered during speed test'''
    tokens = EN(u'Where rap essentially went mainstream, illustrated by seminal Public Enemy, Beastie Boys and L.L. Cool J. tracks.')

    tokens = EN(u'''Charity and other short-term aid have buoyed them so far, and a tax-relief bill working its way through Congress would help. But the September 11 Victim Compensation Fund, enacted by Congress to discourage people from filing lawsuits, will determine the shape of their lives for years to come.\n\n''', entity=False)
    ents = EN.matcher(tokens)
    EN.entity(tokens)
