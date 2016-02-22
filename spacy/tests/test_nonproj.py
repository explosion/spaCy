from __future__ import unicode_literals
import pytest

from spacy.nonproj import ancestors, contains_cycle, is_non_projective_arc, is_non_projective_tree

def test_ancestors():
	tree = [1,2,2,4,5,2,2]
	cyclic_tree = [1,2,2,4,5,3,2]
	partial_tree = [1,2,2,4,5,None,2]
	assert([ a for a in ancestors(3,tree) ] == [4,5,2])
	assert([ a for a in ancestors(3,cyclic_tree) ] == [4,5,3,4,5,3,4])
	assert([ a for a in ancestors(3,partial_tree) ] == [4,5,None])

def test_contains_cycle():
	tree = [1,2,2,4,5,2,2]
	cyclic_tree = [1,2,2,4,5,3,2]
	partial_tree = [1,2,2,4,5,None,2]
	assert(contains_cycle(tree) == None)
	assert(contains_cycle(cyclic_tree) == set([3,4,5]))
	assert(contains_cycle(partial_tree) == None)

def test_is_non_projective_arc():
	nonproj_tree = [1,2,2,4,5,2,7,4,2]
	assert(is_non_projective_arc(0,nonproj_tree) == False)
	assert(is_non_projective_arc(1,nonproj_tree) == False)
	assert(is_non_projective_arc(2,nonproj_tree) == False)
	assert(is_non_projective_arc(3,nonproj_tree) == False)
	assert(is_non_projective_arc(4,nonproj_tree) == False)
	assert(is_non_projective_arc(5,nonproj_tree) == False)
	assert(is_non_projective_arc(6,nonproj_tree) == False)
	assert(is_non_projective_arc(7,nonproj_tree) == True)
	assert(is_non_projective_arc(8,nonproj_tree) == False)
	partial_tree = [1,2,2,4,5,None,7,4,2]
	assert(is_non_projective_arc(7,partial_tree) == False)

def test_is_non_projective_tree():
	proj_tree = [1,2,2,4,5,2,7,5,2]
	nonproj_tree = [1,2,2,4,5,2,7,4,2]
	partial_tree = [1,2,2,4,5,None,7,4,2]
	assert(is_non_projective_tree(proj_tree) == False)
	assert(is_non_projective_tree(nonproj_tree) == True)
	assert(is_non_projective_tree(partial_tree) == False)
