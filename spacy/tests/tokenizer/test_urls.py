# coding: utf-8
from __future__ import unicode_literals

import pytest


URLS_BASIC = [
    "http://www.nytimes.com/2016/04/20/us/politics/new-york-primary-preview.html?hp&action=click&pgtype=Homepage&clickSource=story-heading&module=a-lede-package-region&region=top-news&WT.nav=top-news&_r=0",
    "www.red-stars.com",
    "mailto:foo.bar@baz.com",

]

URLS_FULL = URLS_BASIC + [
    "mailto:foo-bar@baz-co.com",
    "www.google.com?q=google",
    "http://foo.com/blah_(wikipedia)#cite-1"
]


# Punctuation we want to check is split away before the URL
PREFIXES = [
    "(", '"', ">"
]


# Punctuation we want to check is split away after the URL
SUFFIXES = [
    '"', ":", ">"]


@pytest.mark.parametrize("url", URLS_BASIC)
def test_tokenizer_handles_simple_url(tokenizer, url):
    tokens = tokenizer(url)
    assert len(tokens) == 1
    assert tokens[0].text == url


@pytest.mark.parametrize("url", URLS_BASIC)
def test_tokenizer_handles_simple_surround_url(tokenizer, url):
    tokens = tokenizer("(" + url + ")")
    assert len(tokens) == 3
    assert tokens[0].text == "("
    assert tokens[1].text == url
    assert tokens[2].text == ")"


@pytest.mark.slow
@pytest.mark.parametrize("prefix", PREFIXES)
@pytest.mark.parametrize("url", URLS_FULL)
def test_tokenizer_handles_prefixed_url(tokenizer, prefix, url):
    tokens = tokenizer(prefix + url)
    assert len(tokens) == 2
    assert tokens[0].text == prefix
    assert tokens[1].text == url


@pytest.mark.slow
@pytest.mark.parametrize("suffix", SUFFIXES)
@pytest.mark.parametrize("url", URLS_FULL)
def test_tokenizer_handles_suffixed_url(tokenizer, url, suffix):
    tokens = tokenizer(url + suffix)
    assert len(tokens) == 2
    assert tokens[0].text == url
    assert tokens[1].text == suffix


@pytest.mark.slow
@pytest.mark.parametrize("prefix", PREFIXES)
@pytest.mark.parametrize("suffix", SUFFIXES)
@pytest.mark.parametrize("url", URLS_FULL)
def test_tokenizer_handles_surround_url(tokenizer, prefix, suffix, url):
    tokens = tokenizer(prefix + url + suffix)
    assert len(tokens) == 3
    assert tokens[0].text == prefix
    assert tokens[1].text == url
    assert tokens[2].text == suffix


@pytest.mark.slow
@pytest.mark.parametrize("prefix1", PREFIXES)
@pytest.mark.parametrize("prefix2", PREFIXES)
@pytest.mark.parametrize("url", URLS_FULL)
def test_tokenizer_handles_two_prefix_url(tokenizer, prefix1, prefix2, url):
    tokens = tokenizer(prefix1 + prefix2 + url)
    assert len(tokens) == 3
    assert tokens[0].text == prefix1
    assert tokens[1].text == prefix2
    assert tokens[2].text == url


@pytest.mark.slow
@pytest.mark.parametrize("suffix1", SUFFIXES)
@pytest.mark.parametrize("suffix2", SUFFIXES)
@pytest.mark.parametrize("url", URLS_FULL)
def test_tokenizer_handles_two_prefix_url(tokenizer, suffix1, suffix2, url):
    tokens = tokenizer(url + suffix1 + suffix2)
    assert len(tokens) == 3
    assert tokens[0].text == url
    assert tokens[1].text == suffix1
    assert tokens[2].text == suffix2
