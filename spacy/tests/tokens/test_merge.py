from __future__ import unicode_literals
from spacy.en import English
import numpy as np
from spacy.attrs import HEAD


def test_merge_hang():
    text = 'through North and South Carolina'
    EN = English(parser=False)
    doc = EN(text, tag=True)
    heads = np.asarray([[0, 3, -1, -2, -4]], dtype='int32')
    doc.from_array([HEAD], heads.T)
    doc.merge(18, 32, '', '', 'ORG')
    doc.merge(8, 32, '', '', 'ORG')
