# coding: utf-8
from __future__ import unicode_literals

from examples.pipeline.wiki_entity_linking import wikipedia_processor as wp, kb_creator, training_set_creator, run_el, train_el

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
ENTITY_DESCR = 'C:/Users/Sofie/Documents/data/wikipedia/entity_descriptions.csv'

KB_FILE = 'C:/Users/Sofie/Documents/data/wikipedia/kb'
VOCAB_DIR = 'C:/Users/Sofie/Documents/data/wikipedia/vocab'

TRAINING_DIR = 'C:/Users/Sofie/Documents/data/wikipedia/training_data_nel/'


if __name__ == "__main__":
    print("START", datetime.datetime.now())
    print()
    my_kb = None

    # one-time methods to create KB and write to file
    to_create_prior_probs = False
    to_create_entity_counts = False
    to_create_kb = True

    # read KB back in from file
    to_read_kb = True
    to_test_kb = True

    # create training dataset
    create_wp_training = False

    # run training
    run_training = False

    # apply named entity linking to the dev dataset
    apply_to_dev = False

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
                                     entity_def_output=ENTITY_DEFS,
                                     entity_descr_output=ENTITY_DESCR,
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
            my_nlp = spacy.load('en_core_web_sm')
            run_el.run_el_toy_example(kb=my_kb, nlp=my_nlp)
            print()

    # STEP 5: create a training dataset from WP
    if create_wp_training:
        print("STEP 5: create training dataset", datetime.datetime.now())
        training_set_creator.create_training(kb=my_kb, entity_def_input=ENTITY_DEFS, training_output=TRAINING_DIR)

    # STEP 7: apply the EL algorithm on the training dataset
    if run_training:
        print("STEP 6: training ", datetime.datetime.now())
        my_nlp = spacy.load('en_core_web_sm')
        train_el.train_model(kb=my_kb, nlp=my_nlp, training_dir=TRAINING_DIR, entity_descr_output=ENTITY_DESCR, limit=5)
        print()

    # STEP 8: apply the EL algorithm on the dev dataset
    if apply_to_dev:
        my_nlp = spacy.load('en_core_web_sm')
        run_el.run_el_dev(kb=my_kb, nlp=my_nlp, training_dir=TRAINING_DIR, limit=2000)
        print()


    # TODO coreference resolution
    # add_coref()

    print()
    print("STOP", datetime.datetime.now())
