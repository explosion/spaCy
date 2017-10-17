from __future__ import unicode_literals

import pickle

from ...language import Language


def test_pickle_single_doc():
    nlp = Language()
    doc = nlp(u'pickle roundtrip')
    data = pickle.dumps(doc, 1)
    doc2 = pickle.loads(data)
    assert doc2.text == 'pickle roundtrip'


def test_list_of_docs_pickles_efficiently():
    nlp = Language()
    one_pickled = pickle.dumps(nlp(u'0'), -1)
    docs = list(nlp.pipe(str(i) for i in range(100)))
    many_pickled = pickle.dumps(docs, -1)
    assert len(many_pickled) < (len(one_pickled) * 2)
    many_unpickled = pickle.loads(many_pickled)
    assert many_unpickled[0].text == '0'
    assert many_unpickled[-1].text == '99'
    assert len(many_unpickled) == 99
