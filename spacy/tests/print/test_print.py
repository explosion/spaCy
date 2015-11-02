# -*- coding: utf-8 -*-
import pytest


def test_print_doc(EN):
    try:
        doc = EN(u'I sat down for coffee at the coffee store')
        print(doc)
    except Exception:
        pytest.fail("Printing failed")


def test_repr_doc(EN):
    try:
        doc = EN(u'I sat down for coffee at the coffee store')
        print(repr(doc))
    except Exception:
        pytest.fail("Printing failed")


def test_print_doc_unicode(EN):
    try:
        doc = EN(u'I sat down for coffee at the café')
        print(doc)
    except Exception:
        pytest.fail("Printing failed")


def test_repr_doc_unicode(EN):
    try:
        doc = EN(u'I sat down for coffee at the café')
        print(repr(doc))
    except Exception:
        pytest.fail("Printing failed")


def test_print_span(EN):
    try:
        doc = EN(u'I sat down for coffee at the coffee store')[-3:]
        print(doc)
    except Exception:
        pytest.fail("Printing failed")


def test_repr_span(EN):
    try:
        doc = EN(u'I sat down for coffee at the coffee store')[-3:]
        print(repr(doc))
    except Exception:
        pytest.fail("Printing failed")


def test_print_span_unicode(EN):
    try:
        doc = EN(u'I sat down for coffee at the café')[-3:]
        print(doc)
    except Exception:
        pytest.fail("Printing failed")


def test_repr_span_unicode(EN):
    try:
        doc = EN(u'I sat down for coffee at the café')[-3:]
        print(repr(doc))
    except Exception:
        pytest.fail("Printing failed")


def test_print_token(EN):
    try:
        doc = EN(u'I sat down for coffee at the coffee store')[-1]
        print(doc)
    except Exception:
        pytest.fail("Printing failed")


def test_repr_token(EN):
    try:
        doc = EN(u'I sat down for coffee at the coffee store')[-1]
        print(repr(doc))
    except Exception:
        pytest.fail("Printing failed")


def test_print_token_unicode(EN):
    try:
        doc = EN(u'I sat down for coffee at the café')[-1]
        print(doc)
    except Exception:
        pytest.fail("Printing failed")


def test_repr_token_unicode(EN):
    try:
        doc = EN(u'I sat down for coffee at the café')[-1]
        print(repr(doc))
    except Exception:
        pytest.fail("Printing failed")
