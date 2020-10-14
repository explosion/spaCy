from spacy.util import filter_spans


def test_issue6207(en_tokenizer):
    doc = en_tokenizer("zero one two three four five six")

    # Make spans
    s1 = doc[:4]
    s2 = doc[3:6]  # overlaps with s1
    s3 = doc[5:7]  # overlaps with s2, not s1

    result = filter_spans((s1, s2, s3))
    assert s1 in result
    assert s2 not in result
    assert s3 in result
