'''Test Span.as_doc() doesn't segfault'''
from __future__ import unicode_literals
from ...tokens import Doc 
from ...vocab import Vocab
from ... import load as load_spacy


def test_issue1537():
    string = 'The sky is blue . The man is pink . The dog is purple .'
    doc = Doc(Vocab(), words=string.split())
    doc[0].sent_start = True
    for word in doc[1:]:
        if word.nbor(-1).text == '.':
            word.sent_start = True
        else:
            word.sent_start = False

    sents = list(doc.sents)
    sent0 = sents[0].as_doc()
    sent1 = sents[1].as_doc()
    assert isinstance(sent0, Doc)
    assert isinstance(sent1, Doc)


# Currently segfaulting, due to l_edge and r_edge misalignment
#def test_issue1537_model():
#    nlp = load_spacy('en')
#    doc = nlp(u'The sky is blue. The man is pink. The dog is purple.')
#    sents = [s.as_doc() for s in doc.sents]
#    print(list(sents[0].noun_chunks))
#    print(list(sents[1].noun_chunks))
