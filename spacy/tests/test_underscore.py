# coding: utf-8
from __future__ import unicode_literals

import pytest
from mock import Mock

from ..vocab import Vocab
from ..tokens import Doc, Span, Token
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


@pytest.mark.parametrize('obj', [Doc, Span, Token])
def test_doc_underscore_remove_extension(obj):
    ext_name = 'to_be_removed'
    obj.set_extension(ext_name, default=False)
    assert obj.has_extension(ext_name)
    obj.remove_extension(ext_name)
    assert not obj.has_extension(ext_name)


@pytest.mark.parametrize('obj', [Doc, Span, Token])
def test_underscore_raises_for_dup(obj):
    obj.set_extension('test', default=None)
    with pytest.raises(ValueError):
        obj.set_extension('test', default=None)


@pytest.mark.parametrize('invalid_kwargs', [
    {'getter': None, 'setter': lambda: None},
    {'default': None, 'method': lambda: None, 'getter': lambda: None},
    {'setter': lambda: None},
    {'default': None, 'method': lambda: None},
    {'getter': True}])
def test_underscore_raises_for_invalid(invalid_kwargs):
    invalid_kwargs['force'] = True
    with pytest.raises(ValueError):
        Doc.set_extension('test', **invalid_kwargs)


@pytest.mark.parametrize('valid_kwargs', [
    {'getter': lambda: None},
    {'getter': lambda: None, 'setter': lambda: None},
    {'default': 'hello'},
    {'default': None},
    {'method': lambda: None}])
def test_underscore_accepts_valid(valid_kwargs):
    valid_kwargs['force'] = True
    Doc.set_extension('test', **valid_kwargs)
