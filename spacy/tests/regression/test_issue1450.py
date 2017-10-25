from __future__ import unicode_literals
import pytest

from ...matcher import Matcher
from ...tokens import Doc
from ...vocab import Vocab


@pytest.mark.parametrize(
    'string,start,end',
    [
        ('a', 0, 1),
        ('a b', 0, 2),
        ('a c', 0, 1),
        ('a b c', 0, 2),
        ('a b b c', 0, 2),
        ('a b b', 0, 2),
    ]
)
def test_issue1450_matcher_end_zero_plus(string, start, end):
    '''Test matcher works when patterns end with * operator.
    
    Original example (rewritten to avoid model usage)

    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)
    matcher.add(
        "TSTEND",
        on_match_1,
        [
            {TAG: "JJ", LOWER: "new"},
            {TAG: "NN", 'OP': "*"}
        ]
    )
    doc = nlp(u'Could you create a new ticket for me?')
    print([(w.tag_, w.text, w.lower_) for w in doc])
    matches = matcher(doc)
    print(matches)
    assert len(matches) == 1
    assert matches[0][1] == 4
    assert matches[0][2] == 5
    '''
    matcher = Matcher(Vocab())
    matcher.add(
        "TSTEND",
        None,
        [
            {'ORTH': "a"},
            {'ORTH': "b", 'OP': "*"}
        ]
    )
    doc = Doc(Vocab(), words=string.split())
    matches = matcher(doc)
    if start is None or end is None:
        assert matches == []
    
    assert matches[0][1] == start
    assert matches[0][2] == end
