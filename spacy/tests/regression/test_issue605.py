from ...attrs import LOWER, ORTH
from ...tokens import Doc
from ...vocab import Vocab
from ...matcher import Matcher


def return_false(doc, ent_id, label, start, end):
    return False


def test_matcher_accept():
    doc = Doc(Vocab(), words=[u'The', u'golf', u'club', u'is', u'broken'])

    golf_pattern =     [ 
        { ORTH: "golf"},
        { ORTH: "club"}
    ]
    matcher = Matcher(doc.vocab)

    matcher.add_entity(u'Sport_Equipment', acceptor=return_false)
    matcher.add_pattern(u"Sport_Equipment", golf_pattern)
    match = matcher(doc)

    assert match == []
