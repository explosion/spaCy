from spacy import util


def test_load_en():
    rules = util.read_tokenization('en')
    assert len(rules) != 0
    aint = [rule for rule in rules if rule[0] == "ain't"][0]
    chunk, pieces = aint
    assert chunk == "ain't"
    assert pieces[0] == "are"
    assert pieces[1] == "not"
