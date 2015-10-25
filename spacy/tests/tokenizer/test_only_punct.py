from __future__ import unicode_literals


def test_only_pre1(en_tokenizer):
    assert len(en_tokenizer("(")) == 1


def test_only_pre2(en_tokenizer):
    assert len(en_tokenizer("((")) == 2
