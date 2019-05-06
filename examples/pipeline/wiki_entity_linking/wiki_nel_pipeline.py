# coding: utf-8
from __future__ import unicode_literals

from . import wikipedia_processor as wp, kb_creator, training_set_creator

import spacy
from spacy.vocab import Vocab
from spacy.kb import KnowledgeBase
import datetime

"""
Demonstrate how to build a knowledge base from WikiData and run an Entity Linking algorithm.
"""

PRIOR_PROB = 'C:/Users/Sofie/Documents/data/wikipedia/prior_prob.csv'
ENTITY_COUNTS = 'C:/Users/Sofie/Documents/data/wikipedia/entity_freq.csv'
ENTITY_DEFS = 'C:/Users/Sofie/Documents/data/wikipedia/entity_defs.csv'

KB_FILE = 'C:/Users/Sofie/Documents/data/wikipedia/kb'
VOCAB_DIR = 'C:/Users/Sofie/Documents/data/wikipedia/vocab'

TRAINING_OUTPUT_SET_DIR = 'C:/Users/Sofie/Documents/data/wikipedia/training_nel/'
TRAINING_INPUT_SET_DIR = 'C:/Users/Sofie/Documents/data/wikipedia/training_nel_sample_3may2019/'


if __name__ == "__main__":
    print("START", datetime.datetime.now())
    print()
    my_kb = None

    # one-time methods to create KB and write to file
    to_create_prior_probs = False
    to_create_entity_counts = False
    to_create_kb = False

    # read KB back in from file
    to_read_kb = True
    to_test_kb = False

    create_wp_training = False

    # STEP 1 : create prior probabilities from WP
    # run only once !
    if to_create_prior_probs:
        print("STEP 1: to_create_prior_probs", datetime.datetime.now())
        wp.read_wikipedia_prior_probs(prior_prob_output=PRIOR_PROB)
        print()

    # STEP 2 : deduce entity frequencies from WP
    # run only once !
    if to_create_entity_counts:
        print("STEP 2: to_create_entity_counts", datetime.datetime.now())
        wp.write_entity_counts(prior_prob_input=PRIOR_PROB, count_output=ENTITY_COUNTS, to_print=False)
        print()

    # STEP 3 : create KB and write to file
    # run only once !
    if to_create_kb:
        print("STEP 3a: to_create_kb", datetime.datetime.now())
        my_nlp = spacy.load('en_core_web_sm')
        my_vocab = my_nlp.vocab
        my_kb = kb_creator.create_kb(my_vocab,
                                     max_entities_per_alias=10,
                                     min_occ=5,
                                     entity_output=ENTITY_DEFS,
                                     count_input=ENTITY_COUNTS,
                                     prior_prob_input=PRIOR_PROB,
                                     to_print=False)
        print("kb entities:", my_kb.get_size_entities())
        print("kb aliases:", my_kb.get_size_aliases())
        print()

        print("STEP 3b: write KB", datetime.datetime.now())
        my_kb.dump(KB_FILE)
        my_vocab.to_disk(VOCAB_DIR)
        print()

    # STEP 4 : read KB back in from file
    if to_read_kb:
        print("STEP 4: to_read_kb", datetime.datetime.now())
        my_vocab = Vocab()
        my_vocab.from_disk(VOCAB_DIR)
        my_kb = KnowledgeBase(vocab=my_vocab)
        my_kb.load_bulk(KB_FILE)
        print("kb entities:", my_kb.get_size_entities())
        print("kb aliases:", my_kb.get_size_aliases())
        print()

        # test KB
        if to_test_kb:
            kb_creator.test_kb(my_kb)
            print()

    # STEP 5: create a training dataset from WP
    if create_wp_training:
        print("STEP 5: create training dataset", datetime.datetime.now())
        training_set_creator.create_training(kb=my_kb, entity_input=ENTITY_DEFS, training_output=TRAINING_OUTPUT_SET_DIR)

    # TODO coreference resolution
    # add_coref()

    print()
    print("STOP", datetime.datetime.now())
