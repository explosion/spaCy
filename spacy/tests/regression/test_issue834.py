# coding: utf-8

from io import StringIO

word2vec_str = """, -0.046107 -0.035951 -0.560418
de -0.648927 -0.400976 -0.527124
. 0.113685 0.439990 -0.634510
  -1.499184 -0.184280 -0.598371"""


def test_issue834(en_vocab):
    f = StringIO(word2vec_str)
    vector_length = en_vocab.load_vectors(f)
    assert vector_length == 3
