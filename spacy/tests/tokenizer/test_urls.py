from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize("text", [
    u"http://www.nytimes.com/2016/04/20/us/politics/new-york-primary-preview.html?hp&action=click&pgtype=Homepage&clickSource=story-heading&module=a-lede-package-region&region=top-news&WT.nav=top-news&_r=0",
    u"www.google.com?q=google",
    u"google.com",
    u"www.red-stars.com",
    pytest.mark.xfail(u"red-stars.com"),
    u"http://foo.com/blah_(wikipedia)#cite-1",
    u"http://www.example.com/wpstyle/?bar=baz&inga=42&quux",
    u"mailto:foo.bar@baz.com",
    u"mailto:foo-bar@baz-co.com"
])
def test_simple_url(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert tokens[0].orth_ == text
