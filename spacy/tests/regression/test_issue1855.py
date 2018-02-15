# coding: utf-8
from __future__ import unicode_literals
import re

from ...matcher import Matcher

import pytest

pattern1	= [{'ORTH':'A','OP':'1'},{'ORTH':'A','OP':'*'}]
pattern2	= [{'ORTH':'A','OP':'*'},{'ORTH':'A','OP':'1'}]
pattern3	= [{'ORTH':'A','OP':'1'},{'ORTH':'A','OP':'1'}]
pattern4	= [{'ORTH':'B','OP':'1'},{'ORTH':'A','OP':'*'},{'ORTH':'B','OP':'1'}]
pattern5 	= [{'ORTH':'B','OP':'*'},{'ORTH':'A','OP':'*'},{'ORTH':'B','OP':'1'}]

re_pattern1	= 'AA*'
re_pattern2 = 'A*A'
re_pattern3	= 'AA'
re_pattern4	= 'BA*B'
re_pattern5	= 'B*A*B'

@pytest.fixture
def text():
	return "(ABBAAAAAB)."

@pytest.fixture
def doc(en_tokenizer,text):
    doc = en_tokenizer(' '.join(text))
    return doc

@pytest.mark.xfail
@pytest.mark.parametrize('pattern,re_pattern',[
	(pattern1,re_pattern1),
	(pattern2,re_pattern2),
	(pattern3,re_pattern3),
	(pattern4,re_pattern4),
	(pattern5,re_pattern5)])
def test_greedy_matching(doc,text,pattern,re_pattern):
	"""
	Test that the greedy matching behavior of the * op
	is consistant with other re implementations
	"""
	matcher = Matcher(doc.vocab)
	matcher.add(re_pattern,None,pattern)
	matches = matcher(doc)
	re_matches = [m.span() for m in re.finditer(re_pattern,text)]
	for match,re_match in zip(matches,re_matches):
		assert match[1:]==re_match

@pytest.mark.xfail
@pytest.mark.parametrize('pattern,re_pattern',[
	(pattern1,re_pattern1),
	(pattern2,re_pattern2),
	(pattern3,re_pattern3),
	(pattern4,re_pattern4),
	(pattern5,re_pattern5)])
def test_match_consuming(doc,text,pattern,re_pattern):
	"""
	Test that matcher.__call__ consumes tokens on a match
	similar to re.findall
	"""
	matcher = Matcher(doc.vocab)
	matcher.add(re_pattern,None,pattern)
	matches = matcher(doc)
	re_matches = [m.span() for m in re.finditer(re_pattern,text)]
	assert len(matches)==len(re_matches)
