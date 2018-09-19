'''Test that deprojectivization doesn't mess up sentence boundaries.'''
import pytest
from ...syntax.nonproj import projectivize, deprojectivize
from ..util import get_doc

@pytest.mark.xfail
def test_issue2772(en_vocab):
    words = 'When we write or communicate virtually , we can hide our true feelings .'.split()
    # A tree with a non-projective (i.e. crossing) arc
    # The arcs (0, 4) and (2, 9) cross.
    heads = [4, 1, 7, -1, -1, -1, 3, 2, 1, 0, 2, 1, -1, -1]
    deps = ['dep'] * len(heads)
    heads, deps = projectivize(heads, deps)
    doc = get_doc(en_vocab, words=words, heads=heads, deps=deps)
    assert doc[0].is_sent_start == True
    assert doc[1].is_sent_start is None
    deprojectivize(doc)
    assert doc[0].is_sent_start == True
    assert doc[1].is_sent_start is None
