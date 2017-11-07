# coding: utf8

from __future__ import unicode_literals
from ...language import Language


def test_simple_train():
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe('textcat'))
    nlp.get_pipe('textcat').add_label('answer')
    nlp.begin_training()
    for i in range(5):
        for text, answer in [('aaaa', 1.), ('bbbb', 0), ('aa', 1.),
                            ('bbbbbbbbb', 0.), ('aaaaaa', 1)]:
            nlp.update([text], [{'cats': {'answer': answer}}])
    doc = nlp(u'aaa')
    assert 'answer' in doc.cats
    assert doc.cats['answer'] >= 0.5
