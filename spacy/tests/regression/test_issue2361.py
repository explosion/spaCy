from __future__ import unicode_literals
import pytest

from ...displacy import render
from ..util import get_doc

def test_issue2361(de_tokenizer):
    tokens = de_tokenizer('< > & " ')
    html = render(get_doc(tokens.vocab, [t.text for t in tokens]))

    assert '&lt;' in html
    assert '&gt;' in html
    assert '&amp;' in html
    assert '&quot;' in html
