'''Test that spurious 'extra_labels' aren't created when initializing NER.'''
import pytest
from ... import blank

@pytest.mark.xfail
def test_issue2179():
    nlp = blank('it')
    ner = nlp.create_pipe('ner')
    ner.add_label('CITIZENSHIP')
    nlp.add_pipe(ner)
    nlp.begin_training()
    nlp2 = blank('it')
    nlp2.add_pipe(nlp2.create_pipe('ner'))
    nlp2.from_bytes(nlp.to_bytes())
    assert 'extra_labels' not in nlp2.get_pipe('ner').cfg
    assert nlp2.get_pipe('ner').labels == ['CITIZENSHIP']
