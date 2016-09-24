from spacy.deprecated import align_tokens


def test_perfect_align():
    ref = ['I', 'align', 'perfectly']
    indices = []
    i = 0
    for token in ref:
        indices.append((i, i + len(token)))
        i += len(token)
    aligned = list(align_tokens(ref, indices))
    assert aligned[0] == ('I', [(0, 1)])
    assert aligned[1] == ('align', [(1, 6)])
    assert aligned[2] == ('perfectly', [(6, 15)])


def test_hyphen_align():
    ref = ['I', 'must', 're-align']
    indices = [(0, 1), (1, 5), (5, 7), (7, 8), (8, 13)]
    aligned = list(align_tokens(ref, indices))
    assert aligned[0] == ('I', [(0, 1)])
    assert aligned[1] == ('must', [(1, 5)])
    assert aligned[2] == ('re-align', [(5, 7), (7, 8), (8, 13)])


def test_align_continue():
    ref = ['I', 'must', 're-align', 'and', 'continue']
    indices = [(0, 1), (1, 5), (5, 7), (7, 8), (8, 13), (13, 16), (16, 24)]
    aligned = list(align_tokens(ref, indices))
    assert aligned[2] == ('re-align', [(5, 7), (7, 8), (8, 13)])
    assert aligned[3] == ('and', [(13, 16)])
    assert aligned[4] == ('continue', [(16, 24)])
