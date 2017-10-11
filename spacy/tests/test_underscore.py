from mock import Mock
from ..tokens.underscore import Underscore


def test_create_doc_underscore():
    doc = Mock()
    doc.doc = doc
    uscore = Underscore(Underscore.doc_extensions, doc)
    assert uscore._doc is doc
    assert uscore._start is None
    assert uscore._end is None


def test_doc_underscore_getattr_setattr():
    doc = Mock()
    doc.doc = doc
    doc.user_data = {}
    Underscore.doc_extensions['hello'] = (False, None, None, None)
    doc._ = Underscore(Underscore.doc_extensions, doc)
    assert doc._.hello == False
    doc._.hello = True
    assert doc._.hello == True


def test_create_span_underscore():
    span = Mock(doc=Mock(), start=0, end=2)
    uscore = Underscore(Underscore.span_extensions, span,
                        start=span.start, end=span.end)
    assert uscore._doc is span.doc
    assert uscore._start is span.start
    assert uscore._end is span.end


def test_span_underscore_getter_setter():
    span = Mock(doc=Mock(), start=0, end=2)
    Underscore.span_extensions['hello'] = (None, None,
                                           lambda s: (s.start, 'hi'),
                                           lambda s, value: setattr(s, 'start',
                                                                    value))
    span._ = Underscore(Underscore.span_extensions, span,
                        start=span.start, end=span.end)

    assert span._.hello == (0, 'hi')
    span._.hello = 1
    assert span._.hello == (1, 'hi')


def test_token_underscore_method():
    token = Mock(doc=Mock(), idx=7, say_cheese=lambda token: 'cheese')
    Underscore.token_extensions['hello'] = (None, token.say_cheese,
                                            None, None)
    token._ = Underscore(Underscore.token_extensions, token, start=token.idx)
    assert token._.hello() == 'cheese'
