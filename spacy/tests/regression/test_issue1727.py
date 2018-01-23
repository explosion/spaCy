'''Test that models with no pretrained vectors can be deserialized correctly
after vectors are added.'''
from __future__ import unicode_literals
import numpy
from ...pipeline import Tagger
from ...vectors import Vectors
from ...vocab import Vocab
from ..util import make_tempdir


def test_issue1727():
    data = numpy.ones((3, 300), dtype='f')
    keys = [u'I', u'am', u'Matt']
    vectors = Vectors(data=data, keys=keys)
    tagger = Tagger(Vocab())
    tagger.add_label('PRP')
    tagger.begin_training()

    assert tagger.cfg.get('pretrained_dims', 0) == 0
    tagger.vocab.vectors = vectors

    with make_tempdir() as path:
        tagger.to_disk(path)
        tagger = Tagger(Vocab()).from_disk(path)
        assert tagger.cfg.get('pretrained_dims', 0) == 0
