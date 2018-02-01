'''Test sentence boundaries are deserialized correctly,
even for non-projective sentences.'''
from __future__ import unicode_literals

import pytest
import numpy
from ... tokens import Doc
from ... vocab import Vocab
from ... attrs import HEAD, DEP


def test_issue1799():
    problem_sentence = 'Just what I was looking for.'
    heads_deps = numpy.asarray([[1, 397], [4, 436], [2, 426], [1, 402],
                                [0, 8206900633647566924], [18446744073709551615, 440],
                                [18446744073709551614, 442]], dtype='uint64')
    doc = Doc(Vocab(), words='Just what I was looking for .'.split())
    doc.vocab.strings.add('ROOT')
    doc = doc.from_array([HEAD, DEP], heads_deps)
    assert len(list(doc.sents)) == 1
