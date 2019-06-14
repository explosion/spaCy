# coding: utf-8
from __future__ import unicode_literals

import random

from spacy.util import minibatch, compounding

from examples.pipeline.wiki_entity_linking import wikipedia_processor as wp, kb_creator, training_set_creator, run_el
from examples.pipeline.wiki_entity_linking.kb_creator import DESC_WIDTH

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

KB_FILE = 'C:/Users/Sofie/Documents/data/wikipedia/kb_1/kb'
NLP_1_DIR = 'C:/Users/Sofie/Documents/data/wikipedia/nlp_1'
NLP_2_DIR = 'C:/Users/Sofie/Documents/data/wikipedia/nlp_2'

TRAINING_DIR = 'C:/Users/Sofie/Documents/data/wikipedia/training_data_nel/'

MAX_CANDIDATES = 10
MIN_PAIR_OCC = 5
DOC_SENT_CUTOFF = 2
EPOCHS = 10
DROPOUT = 0.1


def run_pipeline():
    print("START", datetime.datetime.now())
    print()
    nlp_1 = spacy.load('en_core_web_lg')
    nlp_2 = None
    kb_1 = None
    kb_2 = None

    # one-time methods to create KB and write to file
    to_create_prior_probs = False
    to_create_entity_counts = False
    to_create_kb = False  # TODO: entity_defs should also contain entities not in the KB

    # read KB back in from file
    to_read_kb = False
    to_test_kb = False

    # create training dataset
    create_wp_training = True

    # train the EL pipe
    train_pipe = False
    measure_performance = False

    # test the EL pipe on a simple example
    to_test_pipeline = False

    # write the NLP object, read back in and test again
    test_nlp_io = False

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
        kb_1 = kb_creator.create_kb(nlp_1,
                                     max_entities_per_alias=MAX_CANDIDATES,
                                     min_occ=MIN_PAIR_OCC,
                                     entity_def_output=ENTITY_DEFS,
                                     entity_descr_output=ENTITY_DESCR,
                                     count_input=ENTITY_COUNTS,
                                     prior_prob_input=PRIOR_PROB,
                                     to_print=False)
        print("kb entities:", kb_1.get_size_entities())
        print("kb aliases:", kb_1.get_size_aliases())
        print()

        print("STEP 3b: write KB and NLP", datetime.datetime.now())
        kb_1.dump(KB_FILE)
        nlp_1.to_disk(NLP_1_DIR)
        print()

    # STEP 4 : read KB back in from file
    if to_read_kb:
        print("STEP 4: to_read_kb", datetime.datetime.now())
        nlp_2 = spacy.load(NLP_1_DIR)
        kb_2 = KnowledgeBase(vocab=nlp_2.vocab, entity_vector_length=DESC_WIDTH)
        kb_2.load_bulk(KB_FILE)
        print("kb entities:", kb_2.get_size_entities())
        print("kb aliases:", kb_2.get_size_aliases())
        print()

        # test KB
        if to_test_kb:
            run_el.run_kb_toy_example(kb=kb_2)
            print()

    # STEP 5: create a training dataset from WP
    if create_wp_training:
        print("STEP 5: create training dataset", datetime.datetime.now())
        training_set_creator.create_training(entity_def_input=ENTITY_DEFS, training_output=TRAINING_DIR)

    # STEP 6: create the entity linking pipe
    if train_pipe:
        print("STEP 6: training Entity Linking pipe", datetime.datetime.now())
        train_limit = 50
        dev_limit = 10
        print("Training on", train_limit, "articles")
        print("Dev testing on", dev_limit, "articles")
        print()

        train_data = training_set_creator.read_training(nlp=nlp_2,
                                                        training_dir=TRAINING_DIR,
                                                        dev=False,
                                                        limit=train_limit,
                                                        to_print=False)

        dev_data = training_set_creator.read_training(nlp=nlp_2,
                                                      training_dir=TRAINING_DIR,
                                                      dev=True,
                                                      limit=dev_limit,
                                                      to_print=False)

        el_pipe = nlp_2.create_pipe(name='entity_linker', config={"doc_cutoff": DOC_SENT_CUTOFF})
        el_pipe.set_kb(kb_2)
        nlp_2.add_pipe(el_pipe, last=True)

        other_pipes = [pipe for pipe in nlp_2.pipe_names if pipe != "entity_linker"]
        with nlp_2.disable_pipes(*other_pipes):  # only train Entity Linking
            nlp_2.begin_training()

        for itn in range(EPOCHS):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 128.0, 1.001))
            batchnr = 0

            with nlp_2.disable_pipes(*other_pipes):
                for batch in batches:
                    try:
                        docs, golds = zip(*batch)
                        nlp_2.update(
                            docs,
                            golds,
                            drop=DROPOUT,
                            losses=losses,
                        )
                        batchnr += 1
                    except Exception as e:
                        print("Error updating batch", e)

            losses['entity_linker'] = losses['entity_linker'] / batchnr
            print("Epoch, train loss", itn, round(losses['entity_linker'], 2))

        if measure_performance:
            print()
            print("STEP 7: performance measurement of Entity Linking pipe", datetime.datetime.now())
            print()

            # print(" measuring accuracy 1-1")
            el_pipe.context_weight = 1
            el_pipe.prior_weight = 1
            dev_acc_1_1 = _measure_accuracy(dev_data, el_pipe)
            train_acc_1_1 = _measure_accuracy(train_data, el_pipe)
            print("train/dev acc combo:", round(train_acc_1_1, 2), round(dev_acc_1_1, 2))

            # baseline using only prior probabilities
            el_pipe.context_weight = 0
            el_pipe.prior_weight = 1
            dev_acc_0_1 = _measure_accuracy(dev_data, el_pipe)
            train_acc_0_1 = _measure_accuracy(train_data, el_pipe)
            print("train/dev acc prior:", round(train_acc_0_1, 2), round(dev_acc_0_1, 2))

            # using only context
            el_pipe.context_weight = 1
            el_pipe.prior_weight = 0
            dev_acc_1_0 = _measure_accuracy(dev_data, el_pipe)
            train_acc_1_0 = _measure_accuracy(train_data, el_pipe)
            print("train/dev acc context:", round(train_acc_1_0, 2), round(dev_acc_1_0, 2))
            print()

            # reset for follow-up tests
            el_pipe.context_weight = 1
            el_pipe.prior_weight = 1


    if to_test_pipeline:
        print()
        print("STEP 8: applying Entity Linking to toy example", datetime.datetime.now())
        print()
        run_el_toy_example(nlp=nlp_2)
        print()

    if test_nlp_io:
        print()
        print("STEP 9: testing NLP IO", datetime.datetime.now())
        print()
        print("writing to", NLP_2_DIR)
        nlp_2.to_disk(NLP_2_DIR)
        print()
        print("reading from", NLP_2_DIR)
        nlp_3 = spacy.load(NLP_2_DIR)

        print()
        print("running toy example with NLP 2")
        run_el_toy_example(nlp=nlp_3)

    print()
    print("STOP", datetime.datetime.now())


def _measure_accuracy(data, el_pipe):
    correct = 0
    incorrect = 0

    docs = [d for d, g in data if len(d) > 0]
    docs = el_pipe.pipe(docs)
    golds = [g for d, g in data if len(d) > 0]

    for doc, gold in zip(docs, golds):
        try:
            correct_entries_per_article = dict()
            for entity in gold.links:
                start, end, gold_kb = entity
                correct_entries_per_article[str(start) + "-" + str(end)] = gold_kb

            for ent in doc.ents:
                if ent.label_ == "PERSON":  # TODO: expand to other types
                    pred_entity = ent.kb_id_
                    start = ent.start_char
                    end = ent.end_char
                    gold_entity = correct_entries_per_article.get(str(start) + "-" + str(end), None)
                    # the gold annotations are not complete so we can't evaluate missing annotations as 'wrong'
                    if gold_entity is not None:
                        if gold_entity == pred_entity:
                            correct += 1
                        else:
                            incorrect += 1

        except Exception as e:
            print("Error assessing accuracy", e)

    if correct == incorrect == 0:
        return 0

    acc = correct / (correct + incorrect)
    return acc


def run_el_toy_example(nlp):
    text = "In The Hitchhiker's Guide to the Galaxy, written by Douglas Adams, " \
           "Douglas reminds us to always bring our towel. " \
           "The main character in Doug's novel is the man Arthur Dent, " \
           "but Douglas doesn't write about George Washington or Homer Simpson."
    doc = nlp(text)

    for ent in doc.ents:
        print("ent", ent.text, ent.label_, ent.kb_id_)

    print()

    # Q4426480 is her husband, Q3568763 her tutor
    text = "Ada Lovelace was the countess of Lovelace. She is known for her programming work on the analytical engine."\
           "Ada Lovelace loved her husband William King dearly. " \
           "Ada Lovelace was tutored by her favorite physics tutor William King."
    doc = nlp(text)

    for ent in doc.ents:
        print("ent", ent.text, ent.label_, ent.kb_id_)


if __name__ == "__main__":
    run_pipeline()
