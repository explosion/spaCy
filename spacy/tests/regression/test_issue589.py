import pytest

from ...vocab import Vocab
from ...tokens import Doc


def test_issue589():
    vocab = Vocab()
    vocab.strings.set_frozen(True)
    doc = Doc(vocab, words=[u'whata'])
