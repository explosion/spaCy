from __future__ import unicode_literals

import pytest

# This approach is deprecated for now
#
#@pytest.mark.models
#def test_am_pm(en_nlp):
#    numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
#    variants = ['a.m.', 'am', 'p.m.', 'pm']
#    spaces = ['', ' ']
#    for num in numbers:
#        for var in variants:
#            for space in spaces:
#                string = u"The meeting was at %s%s%s wasn't it?" % (num, space, var)
#                tokens = en_nlp(string, merge_mwes=True)
#                assert tokens[4].orth_ == '%s%s%s' % (num, space, var)
#                ents = list(tokens.ents)
#                assert len(ents) == 1, ents
#                assert ents[0].label_ == 'TIME', string
#                if ents[0].start == 4 and ents[0].end == 5:
#                    assert ents[0].orth_ == '%s%s%s' % (num, space, var)
