# coding: utf-8
from __future__ import unicode_literals

from ...vocab import Vocab
from ..util import get_doc

import pytest


@pytest.mark.xfail
def test_issue589():
    vocab = Vocab()
    vocab.strings.set_frozen(True)
    doc = get_doc(vocab, ['whata'])
