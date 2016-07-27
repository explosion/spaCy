from __future__ import unicode_literals
import pytest


# @pytest.mark.models
# def test_nsubj(EN):
#     sent = EN(u'A base phrase should be recognized.')
#     base_nps = list(sent.noun_chunks)
#     assert len(base_nps) == 1
#     assert base_nps[0].string == 'A base phrase '


# @pytest.mark.models
# def test_coord(EN):
#     sent = EN(u'A base phrase and a good phrase are often the same.')
#     base_nps = list(sent.noun_chunks)
#     assert len(base_nps) == 2
#     assert base_nps[0].string == 'A base phrase '
#     assert base_nps[1].string == 'a good phrase '


# @pytest.mark.models
# def test_pp(EN):
#     sent = EN(u'A phrase with another phrase occurs')
#     base_nps = list(sent.noun_chunks)
#     assert len(base_nps) == 2
#     assert base_nps[0].string == 'A phrase '
#     assert base_nps[1].string == 'another phrase ' 


@pytest.mark.models
def test_merge_pp(EN):
    sent = EN(u'A phrase with another phrase occurs')
    nps = [(np[0].idx, np[-1].idx + len(np[-1]), np.lemma_, np[0].ent_type_) for np in sent.noun_chunks]

    for start, end, lemma, ent_type in nps:
        sent.merge(start, end, u'NP', lemma, ent_type)
    assert sent[0].string == 'A phrase '
    assert sent[1].string == 'with '
    assert sent[2].string == 'another phrase '
    assert sent[3].string == 'occurs'
