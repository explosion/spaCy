# coding: utf-8
from __future__ import unicode_literals

import random

from spacy.util import minibatch, compounding

from examples.pipeline.wiki_entity_linking import wikipedia_processor as wp, kb_creator, training_set_creator, run_el
from examples.pipeline.wiki_entity_linking.train_el import EL_Model

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

MAX_CANDIDATES = 10
MIN_PAIR_OCC = 5
DOC_CHAR_CUTOFF = 300
EPOCHS = 5
DROPOUT = 0.1

if __name__ == "__main__":
    print("START", datetime.datetime.now())
    print()
    nlp = spacy.load('en_core_web_lg')
    my_kb = None

    # one-time methods to create KB and write to file
    to_create_prior_probs = False
    to_create_entity_counts = False
    to_create_kb = False

    # read KB back in from file
    to_read_kb = True
    to_test_kb = False

    # create training dataset
    create_wp_training = False

    train_pipe = True

    # run EL training
    run_el_training = False

    # apply named entity linking to the dev dataset
    apply_to_dev = False

    to_test_pipeline = False

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
        my_kb = kb_creator.create_kb(nlp,
                                     max_entities_per_alias=MAX_CANDIDATES,
                                     min_occ=MIN_PAIR_OCC,
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
        nlp.vocab.to_disk(VOCAB_DIR)
        print()

    # STEP 4 : read KB back in from file
    if to_read_kb:
        print("STEP 4: to_read_kb", datetime.datetime.now())
        my_vocab = Vocab()
        my_vocab.from_disk(VOCAB_DIR)
        my_kb = KnowledgeBase(vocab=my_vocab, entity_vector_length=64)  # TODO entity vectors
        my_kb.load_bulk(KB_FILE)
        print("kb entities:", my_kb.get_size_entities())
        print("kb aliases:", my_kb.get_size_aliases())
        print()

        # test KB
        if to_test_kb:
            run_el.run_kb_toy_example(kb=my_kb)
            print()

    # STEP 5: create a training dataset from WP
    if create_wp_training:
        print("STEP 5: create training dataset", datetime.datetime.now())
        training_set_creator.create_training(kb=my_kb, entity_def_input=ENTITY_DEFS, training_output=TRAINING_DIR)

    # STEP 6: create the entity linking pipe
    if train_pipe:
        id_to_descr = kb_creator._get_id_to_description(ENTITY_DESCR)

        train_data = training_set_creator.read_training(nlp=nlp,
                                                         training_dir=TRAINING_DIR,
                                                         id_to_descr=id_to_descr,
                                                         doc_cutoff=DOC_CHAR_CUTOFF,
                                                         dev=False,
                                                         limit=10,
                                                         to_print=False)

        el_pipe = nlp.create_pipe(name='entity_linker', config={"kb": my_kb})
        nlp.add_pipe(el_pipe, last=True)

        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "entity_linker"]
        with nlp.disable_pipes(*other_pipes):  # only train Entity Linking
            nlp.begin_training()

            for itn in range(EPOCHS):
                random.shuffle(train_data)
                losses = {}
                batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
                for batch in batches:
                    docs, golds = zip(*batch)
                    nlp.update(
                        docs,
                        golds,
                        drop=DROPOUT,
                        losses=losses,
                    )
                print("Losses", losses)

    ### BELOW CODE IS DEPRECATED ###

    # STEP 6: apply the EL algorithm on the training dataset - TODO deprecated - code moved to pipes.pyx
    if run_el_training:
        print("STEP 6: training", datetime.datetime.now())
        trainer = EL_Model(kb=my_kb, nlp=nlp)
        trainer.train_model(training_dir=TRAINING_DIR, entity_descr_output=ENTITY_DESCR, trainlimit=10000, devlimit=500)
        print()

    # STEP 7: apply the EL algorithm on the dev dataset (TODO: overlaps with code from run_el_training ?)
    if apply_to_dev:
        run_el.run_el_dev(kb=my_kb, nlp=nlp, training_dir=TRAINING_DIR, limit=2000)
        print()

    # test KB
    if to_test_pipeline:
        run_el.run_el_toy_example(kb=my_kb, nlp=nlp)
        print()

    # TODO coreference resolution
    # add_coref()

    print()
    print("STOP", datetime.datetime.now())
