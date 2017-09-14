import pytest

@pytest.mark.models('en')
def test_issue1305(EN):
    '''Test lemmatization of English VBZ'''
    assert EN.vocab.morphology.lemmatizer('works', 'verb') == set(['work'])
    doc = EN(u'This app works well')
    assert doc[2].lemma_ == 'work'
