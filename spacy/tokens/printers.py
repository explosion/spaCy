# coding: utf8
from __future__ import unicode_literals

from .doc import Doc
from ..symbols import HEAD, TAG, DEP, ENT_IOB, ENT_TYPE


def merge_ents(doc):
    """Helper: merge adjacent entities into single tokens; modifies the doc."""
    for ent in doc.ents:
        ent.merge(tag=ent.root.tag_, lemma=ent.text, ent_type=ent.label_)
    return doc


def format_POS(token, light, flat):
    """Helper: form the POS output for a token."""
    subtree = dict([
        ("word", token.text),
        ("lemma", token.lemma_),  # trigger
        ("NE", token.ent_type_),  # trigger
        ("POS_fine", token.tag_),
        ("POS_coarse", token.pos_),
        ("arc", token.dep_),
        ("modifiers", [])
    ])
    if light:
        subtree.pop("lemma")
        subtree.pop("NE")
    if flat:
        subtree.pop("arc")
        subtree.pop("modifiers")
    return subtree


def POS_tree(root, light=False, flat=False):
    """Helper: generate a POS tree for a root token. The doc must have
    `merge_ents(doc)` ran on it.
    """
    subtree = format_POS(root, light=light, flat=flat)
    for c in root.children:
        subtree["modifiers"].append(POS_tree(c))
    return subtree


def parse_tree(doc, light=False, flat=False):
    """Make a copy of the doc and construct a syntactic parse tree similar to
    displaCy. Generates the POS tree for all sentences in a doc.

    doc (Doc): The doc for parsing.
    RETURNS (dict): The parse tree.

    EXAMPLE:
        >>> doc = nlp('Bob brought Alice the pizza. Alice ate the pizza.')
        >>> trees = doc.print_tree()
        >>> trees[1]
        {'modifiers': [
            {'modifiers': [], 'NE': 'PERSON', 'word': 'Alice', 'arc': 'nsubj',
             'POS_coarse': 'PROPN', 'POS_fine': 'NNP', 'lemma': 'Alice'},
            {'modifiers': [
                {'modifiers': [], 'NE': '', 'word': 'the', 'arc': 'det',
                 'POS_coarse': 'DET', 'POS_fine': 'DT', 'lemma': 'the'}],
             'NE': '', 'word': 'pizza', 'arc': 'dobj', 'POS_coarse': 'NOUN',
             'POS_fine': 'NN', 'lemma': 'pizza'},
            {'modifiers': [], 'NE': '', 'word': '.', 'arc': 'punct',
             'POS_coarse': 'PUNCT', 'POS_fine': '.', 'lemma': '.'}],
            'NE': '', 'word': 'ate', 'arc': 'ROOT', 'POS_coarse': 'VERB',
            'POS_fine': 'VBD', 'lemma': 'eat'}
    """
    doc_clone = Doc(doc.vocab, words=[w.text for w in doc])
    doc_clone.from_array([HEAD, TAG, DEP, ENT_IOB, ENT_TYPE],
                         doc.to_array([HEAD, TAG, DEP, ENT_IOB, ENT_TYPE]))
    merge_ents(doc_clone)  # merge the entities into single tokens first
    return [POS_tree(sent.root, light=light, flat=flat)
            for sent in doc_clone.sents]
