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
    "mailto:foo-bar@baz-co.com?subject=hi",
    "www.google.com?q=google",
    "http://foo.com/blah_(wikipedia)#cite-1",
]

# URL SHOULD_MATCH and SHOULD_NOT_MATCH patterns courtesy of https://mathiasbynens.be/demo/url-regex
URLS_SHOULD_MATCH = [
    "http://foo.com/blah_blah",
    "http://foo.com/blah_blah/",
    "http://www.example.com/wpstyle/?p=364",
    "https://www.example.com/foo/?bar=baz&inga=42&quux",
    "http://userid:password@example.com:8080",
    "http://userid:password@example.com:8080/",
    "http://userid@example.com",
    "http://userid@example.com/",
    "http://userid@example.com:8080",
    "http://userid@example.com:8080/",
    "http://userid:password@example.com",
    "http://userid:password@example.com/",
    "http://142.42.1.1/",
    "http://142.42.1.1:8080/",
    "http://foo.com/blah_(wikipedia)#cite-1",
    "http://foo.com/blah_(wikipedia)_blah#cite-1",
    "http://foo.com/unicode_(✪)_in_parens",
    "http://foo.com/(something)?after=parens",
    "http://code.google.com/events/#&product=browser",
    "http://j.mp",
    "ftp://foo.bar/baz",
    "http://foo.bar/?q=Test%20URL-encoded%20stuff",
    "http://-.~_!$&'()*+,;=:%40:80%2f::::::@example.com",
    "http://1337.net",
    "http://a.b-c.de",
    "http://223.255.255.254",
    "http://a.b--c.de/",  # this is a legit domain name see: https://gist.github.com/dperini/729294 comment on 9/9/2014
    "ssh://login@server.com:12345/repository.git",
    "svn+ssh://user@ssh.yourdomain.com/path",
    pytest.param(
        "chrome://extensions/?id=mhjfbmdgcfjbbpaeojofohoefgiehjai",
        marks=pytest.mark.xfail(),
    ),
    pytest.param(
        "chrome-extension://mhjfbmdgcfjbbpaeojofohoefgiehjai", marks=pytest.mark.xfail()
    ),
    "http://foo.com/blah_blah_(wikipedia)",
    "http://foo.com/blah_blah_(wikipedia)_(again)",
    pytest.param("http://⌘.ws", marks=pytest.mark.xfail()),
    pytest.param("http://⌘.ws/", marks=pytest.mark.xfail()),
    pytest.param("http://☺.damowmow.com/", marks=pytest.mark.xfail()),
    pytest.param("http://✪df.ws/123", marks=pytest.mark.xfail()),
    pytest.param("http://➡.ws/䨹", marks=pytest.mark.xfail()),
    pytest.param("http://مثال.إختبار", marks=pytest.mark.xfail()),
    pytest.param("http://例子.测试", marks=pytest.mark.xfail()),
    pytest.param("http://उदाहरण.परीक्षा", marks=pytest.mark.xfail()),
]

URLS_SHOULD_NOT_MATCH = [
    "http://",
    "http://.",
    "http://..",
    "http://../",
    "http://?",
    "http://??",
    "http://??/",
    "http://#",
    "http://##",
    "http://##/",
    "http://foo.bar?q=Spaces should be encoded",
    "//",
    "//a",
    "///a",
    "///",
    "http:///a",
    "rdar://1234",
    "h://test",
    "http:// shouldfail.com",
    ":// should fail",
    "http://foo.bar/foo(bar)baz quux",
    "http://-error-.invalid/",
    "http://a.b-.co",
    "http://0.0.0.0",
    "http://10.1.1.0",
    "http://10.1.1.255",
    "http://224.1.1.1",
    "http://123.123.123",
    "http://3628126748",
    "http://.www.foo.bar/",
    "http://.www.foo.bar./",
    "http://10.1.1.1",
    "NASDAQ:GOOG",
    "http://-a.b.co",
    pytest.param("foo.com", marks=pytest.mark.xfail()),
    "http://1.1.1.1.1",
    "http://www.foo.bar./",
]


# Punctuation we want to check is split away before the URL
PREFIXES = ["(", '"', ">"]


# Punctuation we want to check is split away after the URL
SUFFIXES = ['"', ":", ">"]


@pytest.mark.parametrize("url", URLS_SHOULD_MATCH)
def test_should_match(en_tokenizer, url):
    assert en_tokenizer.token_match(url) is not None


@pytest.mark.parametrize("url", URLS_SHOULD_NOT_MATCH)
def test_should_not_match(en_tokenizer, url):
    assert en_tokenizer.token_match(url) is None


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
def test_tokenizer_handles_two_suffix_url(tokenizer, suffix1, suffix2, url):
    tokens = tokenizer(url + suffix1 + suffix2)
    assert len(tokens) == 3
    assert tokens[0].text == url
    assert tokens[1].text == suffix1
    assert tokens[2].text == suffix2
