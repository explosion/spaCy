# coding: utf-8
from __future__ import unicode_literals

import random

from spacy.util import minibatch, compounding

from examples.pipeline.wiki_entity_linking import wikipedia_processor as wp, kb_creator, training_set_creator, run_el

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
EPOCHS = 10
DROPOUT = 0.1


def run_pipeline():
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

    # train the EL pipe
    train_pipe = True

    # test the EL pipe on a simple example
    to_test_pipeline = True

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
        train_limit = 100
        dev_limit = 20
        print("Training on", train_limit, "articles")
        print("Dev testing on", dev_limit, "articles")
        print()

        train_data = training_set_creator.read_training(nlp=nlp,
                                                        training_dir=TRAINING_DIR,
                                                        dev=False,
                                                        limit=train_limit,
                                                        to_print=False)

        dev_data = training_set_creator.read_training(nlp=nlp,
                                                      training_dir=TRAINING_DIR,
                                                      dev=True,
                                                      limit=dev_limit,
                                                        to_print=False)

        el_pipe = nlp.create_pipe(name='entity_linker', config={"kb": my_kb, "doc_cutoff": DOC_CHAR_CUTOFF})
        nlp.add_pipe(el_pipe, last=True)

        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "entity_linker"]
        with nlp.disable_pipes(*other_pipes):  # only train Entity Linking
            nlp.begin_training()

        for itn in range(EPOCHS):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 128.0, 1.001))

            with nlp.disable_pipes(*other_pipes):
                for batch in batches:
                    docs, golds = zip(*batch)
                    nlp.update(
                        docs,
                        golds,
                        drop=DROPOUT,
                        losses=losses,
                    )

            # print(" measuring accuracy 1-1")
            el_pipe.context_weight = 1
            el_pipe.prior_weight = 1
            dev_acc_1_1 = _measure_accuracy(dev_data, el_pipe)
            train_acc_1_1 = _measure_accuracy(train_data, el_pipe)

            # print(" measuring accuracy 0-1")
            el_pipe.context_weight = 0
            el_pipe.prior_weight = 1
            dev_acc_0_1 = _measure_accuracy(dev_data, el_pipe)
            train_acc_0_1 = _measure_accuracy(train_data, el_pipe)

            # print(" measuring accuracy 1-0")
            el_pipe.context_weight = 1
            el_pipe.prior_weight = 0
            dev_acc_1_0 = _measure_accuracy(dev_data, el_pipe)
            train_acc_1_0 = _measure_accuracy(train_data, el_pipe)

            print("Epoch, train loss, train/dev acc, 1-1, 0-1, 1-0:", itn, round(losses['entity_linker'], 2),
                  round(train_acc_1_1, 2), round(train_acc_0_1, 2), round(train_acc_1_0, 2), "/",
                  round(dev_acc_1_1, 2), round(dev_acc_0_1, 2), round(dev_acc_1_0, 2))

    # test Entity Linker
    if to_test_pipeline:
        print()
        run_el_toy_example(kb=my_kb, nlp=nlp)
        print()

    print()
    print("STOP", datetime.datetime.now())


def _measure_accuracy(data, el_pipe):
    correct = 0
    incorrect = 0

    docs = [d for d, g in data]
    docs = el_pipe.pipe(docs)

    golds = [g for d, g in data]

    for doc, gold in zip(docs, golds):
        correct_entries_per_article = dict()
        for entity in gold.links:
            start, end, gold_kb = entity
            correct_entries_per_article[str(start) + "-" + str(end)] = gold_kb

        for ent in doc.ents:
            if ent.label_ == "PERSON":  # TODO: expand to other types
                pred_entity = ent.kb_id_
                start = ent.start
                end = ent.end
                gold_entity = correct_entries_per_article.get(str(start) + "-" + str(end), None)
                if gold_entity is not None:
                    if gold_entity == pred_entity:
                        correct += 1
                    else:
                        incorrect += 1

    if correct == incorrect == 0:
        return 0

    acc = correct / (correct + incorrect)
    return acc


def run_el_toy_example(nlp, kb):
    text = "In The Hitchhiker's Guide to the Galaxy, written by Douglas Adams, " \
           "Douglas reminds us to always bring our towel. " \
           "The main character in Doug's novel is the man Arthur Dent, " \
           "but Douglas doesn't write about George Washington or Homer Simpson."
    doc = nlp(text)

    for ent in doc.ents:
        print("ent", ent.text, ent.label_, ent.kb_id_)

    print()

    # Q4426480 is her husband, Q3568763 her tutor
    text = "Ada Lovelace loved her husband William King dearly. " \
           "Ada Lovelace was tutored by her favorite physics tutor William King."
    doc = nlp(text)

    for ent in doc.ents:
        print("ent", ent.text, ent.label_, ent.kb_id_)


if __name__ == "__main__":
    run_pipeline()
