from __future__ import unicode_literals
import pytest

from spacy.tokens.doc import Doc
from spacy.vocab import Vocab
from spacy.tokenizer import Tokenizer
from spacy.attrs import DEP, HEAD
import numpy

from spacy.syntax.nonproj import ancestors, contains_cycle, is_nonproj_arc, is_nonproj_tree, PseudoProjectivity

def test_ancestors():
	tree = [1,2,2,4,5,2,2]
	cyclic_tree = [1,2,2,4,5,3,2]
	partial_tree = [1,2,2,4,5,None,2]
	multirooted_tree = [3,2,0,3,3,7,7,3,7,10,7,10,11,12,18,16,18,17,12,3]
	assert([ a for a in ancestors(3,tree) ] == [4,5,2])
	assert([ a for a in ancestors(3,cyclic_tree) ] == [4,5,3,4,5,3,4])
	assert([ a for a in ancestors(3,partial_tree) ] == [4,5,None])
	assert([ a for a in ancestors(17,multirooted_tree) ] == [])

def test_contains_cycle():
	tree = [1,2,2,4,5,2,2]
	cyclic_tree = [1,2,2,4,5,3,2]
	partial_tree = [1,2,2,4,5,None,2]
	multirooted_tree = [3,2,0,3,3,7,7,3,7,10,7,10,11,12,18,16,18,17,12,3]
	assert(contains_cycle(tree) == None)
	assert(contains_cycle(cyclic_tree) == set([3,4,5]))
	assert(contains_cycle(partial_tree) == None)
	assert(contains_cycle(multirooted_tree) == None)

def test_is_nonproj_arc():
	nonproj_tree = [1,2,2,4,5,2,7,4,2]
	partial_tree = [1,2,2,4,5,None,7,4,2]
	multirooted_tree = [3,2,0,3,3,7,7,3,7,10,7,10,11,12,18,16,18,17,12,3]
	assert(is_nonproj_arc(0,nonproj_tree) == False)
	assert(is_nonproj_arc(1,nonproj_tree) == False)
	assert(is_nonproj_arc(2,nonproj_tree) == False)
	assert(is_nonproj_arc(3,nonproj_tree) == False)
	assert(is_nonproj_arc(4,nonproj_tree) == False)
	assert(is_nonproj_arc(5,nonproj_tree) == False)
	assert(is_nonproj_arc(6,nonproj_tree) == False)
	assert(is_nonproj_arc(7,nonproj_tree) == True)
	assert(is_nonproj_arc(8,nonproj_tree) == False)
	assert(is_nonproj_arc(7,partial_tree) == False)
	assert(is_nonproj_arc(17,multirooted_tree) == False)
	assert(is_nonproj_arc(16,multirooted_tree) == True)

def test_is_nonproj_tree():
	proj_tree = [1,2,2,4,5,2,7,5,2]
	nonproj_tree = [1,2,2,4,5,2,7,4,2]
	partial_tree = [1,2,2,4,5,None,7,4,2]
	multirooted_tree = [3,2,0,3,3,7,7,3,7,10,7,10,11,12,18,16,18,17,12,3]
	assert(is_nonproj_tree(proj_tree) == False)
	assert(is_nonproj_tree(nonproj_tree) == True)
	assert(is_nonproj_tree(partial_tree) == False)
	assert(is_nonproj_tree(multirooted_tree) == True)

def test_pseudoprojectivity():
	tree = [1,2,2]
	nonproj_tree = [1,2,2,4,5,2,7,4,2]
	labels = ['NK','SB','ROOT','NK','OA','OC','SB','RC','--']
	nonproj_tree2 = [9,1,3,1,5,6,9,8,6,1,6,12,13,10,1]
	labels2 = ['MO','ROOT','NK','SB','MO','NK','OA','NK','AG','OC','MNR','MO','NK','NK','--']

	assert(PseudoProjectivity.decompose('X||Y') == ('X','Y'))
	assert(PseudoProjectivity.decompose('X') == ('X',''))

	assert(PseudoProjectivity.is_decorated('X||Y') == True)
	assert(PseudoProjectivity.is_decorated('X') == False)

	PseudoProjectivity._lift(0,tree)
	assert(tree == [2,2,2])

	np_arc = PseudoProjectivity._get_smallest_nonproj_arc(nonproj_tree)
	assert(np_arc == 7)

	np_arc = PseudoProjectivity._get_smallest_nonproj_arc(nonproj_tree2)
	assert(np_arc == 10)

	proj_heads, deco_labels = PseudoProjectivity.projectivize(nonproj_tree,labels)
	assert(proj_heads == [1,2,2,4,5,2,7,5,2])
	assert(deco_labels == ['NK','SB','ROOT','NK','OA','OC','SB','RC||OA','--'])
	# deproj_heads, undeco_labels = PseudoProjectivity.deprojectivize(proj_heads,deco_labels)
	# assert(deproj_heads == nonproj_tree)
	# assert(undeco_labels == labels)

	proj_heads, deco_labels = PseudoProjectivity.projectivize(nonproj_tree2,labels2)
	assert(proj_heads == [1,1,3,1,5,6,9,8,6,1,9,12,13,10,1])
	assert(deco_labels == ['MO||OC','ROOT','NK','SB','MO','NK','OA','NK','AG','OC','MNR||OA','MO','NK','NK','--'])
	# deproj_heads, undeco_labels = PseudoProjectivity.deprojectivize(proj_heads,deco_labels)
	# assert(deproj_heads == nonproj_tree2)
	# assert(undeco_labels == labels2)

	# if decoration is wrong such that there is no head with the desired label
	# the structure is kept and the label is undecorated
	# deproj_heads, undeco_labels = PseudoProjectivity.deprojectivize([1,2,2,4,5,2,7,5,2],['NK','SB','ROOT','NK','OA','OC','SB','RC||DA','--'])
	# assert(deproj_heads == [1,2,2,4,5,2,7,5,2])
	# assert(undeco_labels == ['NK','SB','ROOT','NK','OA','OC','SB','RC','--'])

	# if there are two potential new heads, the first one is chosen even if it's wrong
	# deproj_heads, undeco_labels = PseudoProjectivity.deprojectivize([1,1,3,1,5,6,9,8,6,1,9,12,13,10,1], \
	# 	                                            ['MO||OC','ROOT','NK','OC','MO','NK','OA','NK','AG','OC','MNR||OA','MO','NK','NK','--'])
	# assert(deproj_heads == [3,1,3,1,5,6,9,8,6,1,6,12,13,10,1])
	# assert(undeco_labels == ['MO','ROOT','NK','OC','MO','NK','OA','NK','AG','OC','MNR','MO','NK','NK','--'])















