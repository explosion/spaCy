from spacy.gold import _min_edit_path


def test_min_edit_path():
    '''Test problem that arose from Chinese parsing, where alignment didn't match
    at the start, depending on which direction followed. The solution was that
    a regular expression did not have re.UNICODE flag, causing it to over match.
    '''

    cand_words = [u'\u53cc\u65b9', u'D', u'-', u'RAM']
    gold_words = [u'\u53cc\u65b9', u'D-RAM']
    cost, alignment = _min_edit_path(cand_words, gold_words)
    assert alignment[0] == 'M'
    cost, alignment = _min_edit_path(gold_words, cand_words)
    assert alignment[0] == 'M'
