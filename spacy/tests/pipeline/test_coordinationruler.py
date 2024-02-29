import pytest
from typing import List

from spacy.tokens import Doc
import spacy

from spacy.pipeline.coordinationruler import split_noun_coordination

@pytest.fixture
def nlp():
    return spacy.blank("en")

### NOUN CONSTRUCTION CASES ###
@pytest.fixture
def noun_construction_case1(nlp):
    words = ["apples", "and", "oranges"]
    spaces = [True, True, False]  # Indicates whether the word is followed by a space
    pos_tags = ["NOUN", "CCONJ", "NOUN"]
    dep_relations = ["nsubj", "cc", "conj"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    #set pos_ and dep_ attributes
    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep
        
    # # define head relationships manually
    doc[1].head = doc[2]  # "and" -> "oranges"
    doc[2].head = doc[0]  # "oranges" -> "apples"
    doc[0].head = doc[0] 
    
    return doc
    
@pytest.fixture
def noun_construction_case2(nlp):
    words = ["red", "apples", "and", "oranges"]
    spaces = [True, True, True, False]  # Indicates whether the word is followed by a space
    pos_tags = ["ADJ", "NOUN", "CCONJ", "NOUN"]
    dep_relations = ["amod", "nsubj", "cc", "conj"]

    # Create a Doc object manually
    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    #set pos_ and dep_ attributes
    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep
        
    # define head relationships manually
    doc[0].head = doc[1]  
    doc[2].head = doc[3]  
    doc[3].head = doc[1]  
    
    return doc

@pytest.fixture
def noun_construction_case3(nlp):
    words = ["apples", "and", "juicy", "oranges"]
    spaces = [True, True, True, False]  # Indicates whether the word is followed by a space.
    pos_tags = ["NOUN", "CCONJ", "ADJ", "NOUN"]
    dep_relations = ["nsubj", "cc", "amod", "conj"]

    #create a Doc object manually
    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    #set POS and dependency tags
    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    #defining head relationships manually
    doc[0].head = doc[0]  # "apples" as root, pointing to itself for simplicity.
    doc[1].head = doc[3]  # "and" -> "oranges"
    doc[2].head = doc[3]  # "juicy" -> "oranges"
    doc[3].head = doc[0]  # "oranges" -> "apples", indicating a conjunctive relationship
    
    return doc

@pytest.fixture
def noun_construction_case4(nlp):
    words = ["hot", "chicken", "wings", "and", "soup"]
    spaces = [True, True, True, True, False]  # Indicates whether the word is followed by a space.
    pos_tags= ["ADJ", "NOUN", "NOUN", "CCONJ", "NOUN"]
    dep_relations = ["amod", "compound", "ROOT", "cc", "conj"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    # Define head relationships manually for "hot chicken wings and soup".
    doc[0].head = doc[2]  # "hot" -> "wings"
    doc[1].head = doc[2]  # "chicken" -> "wings"
    doc[2].head = doc[2]  # "wings" as root
    doc[3].head = doc[4]  # "and" -> "soup"
    doc[4].head = doc[2]  # "soup" -> "wings"
    
    return doc

@pytest.fixture
def noun_construction_case5(nlp):
    words = ["green", "apples", "and", "rotten", "oranges"]
    spaces = [True, True, True, True, False]  # Indicates whether the word is followed by a space.
    pos_tags = ["ADJ", "NOUN", "CCONJ", "ADJ", "NOUN"]
    dep_relations = ["amod", "ROOT", "cc", "amod", "conj"]

    doc = Doc(nlp.vocab, words=words, spaces=spaces)

    # Set POS and dependency tags.
    for token, pos, dep in zip(doc, pos_tags, dep_relations):
        token.pos_ = pos
        token.dep_ = dep

    # Define head relationships manually for "green apples and rotten oranges".
    doc[0].head = doc[1]  # "green" -> "apples"
    doc[1].head = doc[1]  # "apples" as root
    doc[2].head = doc[4]  # "and" -> "oranges"
    doc[3].head = doc[4]  # "rotten" -> "oranges"
    doc[4].head = doc[1]  # "oranges" -> "apples"
    
    return doc

#test split_noun_coordination on 5 different cases
def test_split_noun_coordination(noun_construction_case1, 
                                 noun_construction_case2, 
                                 noun_construction_case3, 
                                 noun_construction_case4, 
                                 noun_construction_case5):
    
    #test 1: no modifier - it should return None from _split_doc
    case1_split = split_noun_coordination(noun_construction_case1)
    
    assert case1_split == None
    
    #test 2: modifier is at the beginning of the noun phrase
    case2_split = split_noun_coordination(noun_construction_case2)
    
    assert len(case2_split) == 2
    assert isinstance(case2_split, list)
    assert all(isinstance(phrase, str) for phrase in case2_split)
    assert case2_split == ["red apples", "red oranges"]
    

    #test 3: modifier is at the end of the noun phrase
    case3_split = split_noun_coordination(noun_construction_case3)

    assert len(case3_split) == 2
    assert isinstance(case3_split, list)
    assert all(isinstance(phrase, str) for phrase in case3_split)
    assert case3_split == ["juicy oranges", "juicy apples"]
    
    #test 4: deal with compound nouns
    case4_split = split_noun_coordination(noun_construction_case4)

    assert len(case4_split) == 2
    assert isinstance(case4_split, list)
    assert all(isinstance(phrase, str) for phrase in case4_split)
    assert case4_split == ["hot chicken wings", "hot soup"]
    
    
    #test 5: multiple modifiers
    case5_split = split_noun_coordination(noun_construction_case5)

    pass #this should return none i think