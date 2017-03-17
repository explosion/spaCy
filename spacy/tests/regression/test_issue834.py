# coding: utf-8
from __future__ import unicode_literals


word2vec_str = """, -0.046107 -0.035951 -0.560418
de -0.648927 -0.400976 -0.527124
. 0.113685 0.439990 -0.634510
\u00A0 -1.499184 -0.184280 -0.598371"""


def test_issue834(en_vocab, text_file):
    """Test that no-break space (U+00A0) is detected as space by the load_vectors function."""
    text_file.write(word2vec_str)
    text_file.seek(0)
    vector_length = en_vocab.load_vectors(text_file)
    assert vector_length == 3
