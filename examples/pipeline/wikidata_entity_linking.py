# coding: utf-8
from __future__ import unicode_literals

import random
import datetime
from pathlib import Path

from bin.wiki_entity_linking import training_set_creator, kb_creator, wikipedia_processor as wp
from bin.wiki_entity_linking.kb_creator import DESC_WIDTH

import spacy
from spacy.kb import KnowledgeBase
from spacy.util import minibatch, compounding

"""
Demonstrate how to build a knowledge base from WikiData and run an Entity Linking algorithm.
"""

ROOT_DIR = Path("C:/Users/Sofie/Documents/data/")
OUTPUT_DIR = ROOT_DIR / 'wikipedia'
TRAINING_DIR = OUTPUT_DIR / 'training_data_nel'

PRIOR_PROB = OUTPUT_DIR / 'prior_prob.csv'
ENTITY_COUNTS = OUTPUT_DIR / 'entity_freq.csv'
ENTITY_DEFS = OUTPUT_DIR / 'entity_defs.csv'
ENTITY_DESCR = OUTPUT_DIR / 'entity_descriptions.csv'

KB_FILE = OUTPUT_DIR / 'kb_1' / 'kb'
NLP_1_DIR = OUTPUT_DIR / 'nlp_1'
NLP_2_DIR = OUTPUT_DIR / 'nlp_2'

# get latest-all.json.bz2 from https://dumps.wikimedia.org/wikidatawiki/entities/
WIKIDATA_JSON = ROOT_DIR / 'wikidata' / 'wikidata-20190304-all.json.bz2'

# get enwiki-latest-pages-articles-multistream.xml.bz2 from https://dumps.wikimedia.org/enwiki/latest/
ENWIKI_DUMP = ROOT_DIR / 'wikipedia' / 'enwiki-20190320-pages-articles-multistream.xml.bz2'

# KB construction parameters
MAX_CANDIDATES = 10
MIN_ENTITY_FREQ = 20
MIN_PAIR_OCC = 5

# model training parameters
EPOCHS = 10
DROPOUT = 0.2
LEARN_RATE = 0.005
L2 = 1e-6
CONTEXT_WIDTH=128


def run_pipeline():
    # set the appropriate booleans to define which parts of the pipeline should be re(run)
    print("START", datetime.datetime.now())
    print()
    nlp_1 = spacy.load('en_core_web_lg')
    nlp_2 = None
    kb_2 = None

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
    measure_performance = True

    # test the EL pipe on a simple example
    to_test_pipeline = True

    # write the NLP object, read back in and test again
    to_write_nlp = True
    to_read_nlp = False
    test_from_file = False

    # STEP 1 : create prior probabilities from WP (run only once)
    if to_create_prior_probs:
        print("STEP 1: to_create_prior_probs", datetime.datetime.now())
        wp.read_wikipedia_prior_probs(wikipedia_input=ENWIKI_DUMP, prior_prob_output=PRIOR_PROB)
        print()

    # STEP 2 : deduce entity frequencies from WP (run only once)
    if to_create_entity_counts:
        print("STEP 2: to_create_entity_counts", datetime.datetime.now())
        wp.write_entity_counts(prior_prob_input=PRIOR_PROB, count_output=ENTITY_COUNTS, to_print=False)
        print()

    # STEP 3 : create KB and write to file (run only once)
    if to_create_kb:
        print("STEP 3a: to_create_kb", datetime.datetime.now())
        kb_1 = kb_creator.create_kb(nlp_1,
                                    max_entities_per_alias=MAX_CANDIDATES,
                                    min_entity_freq=MIN_ENTITY_FREQ,
                                    min_occ=MIN_PAIR_OCC,
                                    entity_def_output=ENTITY_DEFS,
                                    entity_descr_output=ENTITY_DESCR,
                                    count_input=ENTITY_COUNTS,
                                    prior_prob_input=PRIOR_PROB,
                                    wikidata_input=WIKIDATA_JSON)
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
            check_kb(kb_2)
            print()

    # STEP 5: create a training dataset from WP
    if create_wp_training:
        print("STEP 5: create training dataset", datetime.datetime.now())
        training_set_creator.create_training(wikipedia_input=ENWIKI_DUMP,
                                             entity_def_input=ENTITY_DEFS,
                                             training_output=TRAINING_DIR)

    # STEP 6: create and train the entity linking pipe
    if train_pipe:
        print("STEP 6: training Entity Linking pipe", datetime.datetime.now())
        el_pipe = nlp_2.create_pipe(name='entity_linker', config={"context_width": CONTEXT_WIDTH})
        el_pipe.set_kb(kb_2)
        nlp_2.add_pipe(el_pipe, last=True)

        other_pipes = [pipe for pipe in nlp_2.pipe_names if pipe != "entity_linker"]
        with nlp_2.disable_pipes(*other_pipes):  # only train Entity Linking
            optimizer = nlp_2.begin_training()
            optimizer.learn_rate = LEARN_RATE
            optimizer.L2 = L2

        # define the size (nr of entities) of training and dev set
        train_limit = 500000
        dev_limit = 5000

        train_data = training_set_creator.read_training(nlp=nlp_2,
                                                        training_dir=TRAINING_DIR,
                                                        dev=False,
                                                        limit=train_limit)

        print("Training on", len(train_data), "articles")
        print()

        dev_data = training_set_creator.read_training(nlp=nlp_2,
                                                      training_dir=TRAINING_DIR,
                                                      dev=True,
                                                      limit=dev_limit)

        print("Dev testing on", len(dev_data), "articles")
        print()

        if not train_data:
            print("Did not find any training data")
        else:
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
                                sgd=optimizer,
                                drop=DROPOUT,
                                losses=losses,
                            )
                            batchnr += 1
                        except Exception as e:
                            print("Error updating batch:", e)

                if batchnr > 0:
                    with el_pipe.model.use_params(optimizer.averages):
                        el_pipe.context_weight = 1
                        el_pipe.prior_weight = 0
                        dev_acc_context, dev_acc_context_dict = _measure_accuracy(dev_data, el_pipe)
                        losses['entity_linker'] = losses['entity_linker'] / batchnr
                        print("Epoch, train loss", itn, round(losses['entity_linker'], 2),
                              " / dev acc context avg", round(dev_acc_context, 3))

        # STEP 7: measure the performance of our trained pipe on an independent dev set
        if len(dev_data) and measure_performance:
            print()
            print("STEP 7: performance measurement of Entity Linking pipe", datetime.datetime.now())
            print()

            counts, acc_r, acc_r_label, acc_p, acc_p_label, acc_o, acc_o_label = _measure_baselines(dev_data, kb_2)
            print("dev counts:", sorted(counts.items(), key=lambda x: x[0]))
            print("dev acc oracle:", round(acc_o, 3), [(x, round(y, 3)) for x, y in acc_o_label.items()])
            print("dev acc random:", round(acc_r, 3), [(x, round(y, 3)) for x, y in acc_r_label.items()])
            print("dev acc prior:", round(acc_p, 3), [(x, round(y, 3)) for x, y in acc_p_label.items()])

            with el_pipe.model.use_params(optimizer.averages):
                # measuring combined accuracy (prior + context)
                el_pipe.context_weight = 1
                el_pipe.prior_weight = 1
                dev_acc_combo, dev_acc_combo_dict = _measure_accuracy(dev_data, el_pipe)
                print("dev acc combo avg:", round(dev_acc_combo, 3),
                      [(x, round(y, 3)) for x, y in dev_acc_combo_dict.items()])

                # using only context
                el_pipe.context_weight = 1
                el_pipe.prior_weight = 0
                dev_acc_context, dev_acc_context_dict = _measure_accuracy(dev_data, el_pipe)
                print("dev acc context avg:", round(dev_acc_context, 3),
                      [(x, round(y, 3)) for x, y in dev_acc_context_dict.items()])

            # reset for follow-up tests
            el_pipe.context_weight = 1
            el_pipe.prior_weight = 1

        # STEP 8: apply the EL pipe on a toy example
        if to_test_pipeline:
            print()
            print("STEP 8: applying Entity Linking to toy example", datetime.datetime.now())
            print()
            run_el_toy_example(nlp=nlp_2)

        # STEP 9: write the NLP pipeline (including entity linker) to file
        if to_write_nlp:
            print()
            print("STEP 9: testing NLP IO", datetime.datetime.now())
            print()
            print("writing to", NLP_2_DIR)
            nlp_2.to_disk(NLP_2_DIR)
            print()

    # verify that the IO has gone correctly
    if to_read_nlp:
        print("reading from", NLP_2_DIR)
        nlp_3 = spacy.load(NLP_2_DIR)

        print("running toy example with NLP 3")
        run_el_toy_example(nlp=nlp_3)

    # testing performance with an NLP model from file
    if test_from_file:
        nlp_2 = spacy.load(NLP_1_DIR)
        nlp_3 = spacy.load(NLP_2_DIR)
        el_pipe = nlp_3.get_pipe("entity_linker")

        dev_limit = 10000
        dev_data = training_set_creator.read_training(nlp=nlp_2,
                                                      training_dir=TRAINING_DIR,
                                                      dev=True,
                                                      limit=dev_limit)

        print("Dev testing from file on", len(dev_data), "articles")
        print()

        dev_acc_combo, dev_acc_combo_dict = _measure_accuracy(dev_data, el_pipe=el_pipe)
        print("dev acc combo avg:", round(dev_acc_combo, 3),
              [(x, round(y, 3)) for x, y in dev_acc_combo_dict.items()])

    print()
    print("STOP", datetime.datetime.now())


def _measure_accuracy(data, el_pipe=None):
    # If the docs in the data require further processing with an entity linker, set el_pipe
    correct_by_label = dict()
    incorrect_by_label = dict()

    docs = [d for d, g in data if len(d) > 0]
    if el_pipe is not None:
        docs = list(el_pipe.pipe(docs))
    golds = [g for d, g in data if len(d) > 0]

    for doc, gold in zip(docs, golds):
        try:
            correct_entries_per_article = dict()
            for entity in gold.links:
                start, end, gold_kb = entity
                correct_entries_per_article[str(start) + "-" + str(end)] = gold_kb

            for ent in doc.ents:
                ent_label = ent.label_
                pred_entity = ent.kb_id_
                start = ent.start_char
                end = ent.end_char
                gold_entity = correct_entries_per_article.get(str(start) + "-" + str(end), None)
                # the gold annotations are not complete so we can't evaluate missing annotations as 'wrong'
                if gold_entity is not None:
                    if gold_entity == pred_entity:
                        correct = correct_by_label.get(ent_label, 0)
                        correct_by_label[ent_label] = correct + 1
                    else:
                        incorrect = incorrect_by_label.get(ent_label, 0)
                        incorrect_by_label[ent_label] = incorrect + 1

        except Exception as e:
            print("Error assessing accuracy", e)

    acc, acc_by_label = calculate_acc(correct_by_label,  incorrect_by_label)
    return acc, acc_by_label


def _measure_baselines(data, kb):
    # Measure 3 performance baselines: random selection, prior probabilities, and 'oracle' prediction for upper bound
    counts_by_label = dict()

    random_correct_by_label = dict()
    random_incorrect_by_label = dict()

    oracle_correct_by_label = dict()
    oracle_incorrect_by_label = dict()

    prior_correct_by_label = dict()
    prior_incorrect_by_label = dict()

    docs = [d for d, g in data if len(d) > 0]
    golds = [g for d, g in data if len(d) > 0]

    for doc, gold in zip(docs, golds):
        try:
            correct_entries_per_article = dict()
            for entity in gold.links:
                start, end, gold_kb = entity
                correct_entries_per_article[str(start) + "-" + str(end)] = gold_kb

            for ent in doc.ents:
                ent_label = ent.label_
                start = ent.start_char
                end = ent.end_char
                gold_entity = correct_entries_per_article.get(str(start) + "-" + str(end), None)

                # the gold annotations are not complete so we can't evaluate missing annotations as 'wrong'
                if gold_entity is not None:
                    counts_by_label[ent_label] = counts_by_label.get(ent_label, 0) + 1
                    candidates = kb.get_candidates(ent.text)
                    oracle_candidate = ""
                    best_candidate = ""
                    random_candidate = ""
                    if candidates:
                        scores = []

                        for c in candidates:
                            scores.append(c.prior_prob)
                            if c.entity_ == gold_entity:
                                oracle_candidate = c.entity_

                        best_index = scores.index(max(scores))
                        best_candidate = candidates[best_index].entity_
                        random_candidate = random.choice(candidates).entity_

                    if gold_entity == best_candidate:
                        prior_correct_by_label[ent_label] = prior_correct_by_label.get(ent_label, 0) + 1
                    else:
                        prior_incorrect_by_label[ent_label] = prior_incorrect_by_label.get(ent_label, 0) + 1

                    if gold_entity == random_candidate:
                        random_correct_by_label[ent_label] = random_correct_by_label.get(ent_label, 0) + 1
                    else:
                        random_incorrect_by_label[ent_label] = random_incorrect_by_label.get(ent_label, 0) + 1

                    if gold_entity == oracle_candidate:
                        oracle_correct_by_label[ent_label] = oracle_correct_by_label.get(ent_label, 0) + 1
                    else:
                        oracle_incorrect_by_label[ent_label] = oracle_incorrect_by_label.get(ent_label, 0) + 1

        except Exception as e:
            print("Error assessing accuracy", e)

    acc_prior, acc_prior_by_label = calculate_acc(prior_correct_by_label, prior_incorrect_by_label)
    acc_random, acc_random_by_label = calculate_acc(random_correct_by_label, random_incorrect_by_label)
    acc_oracle, acc_oracle_by_label = calculate_acc(oracle_correct_by_label, oracle_incorrect_by_label)

    return counts_by_label, acc_random, acc_random_by_label, acc_prior, acc_prior_by_label, acc_oracle, acc_oracle_by_label


def calculate_acc(correct_by_label, incorrect_by_label):
    acc_by_label = dict()
    total_correct = 0
    total_incorrect = 0
    all_keys = set()
    all_keys.update(correct_by_label.keys())
    all_keys.update(incorrect_by_label.keys())
    for label in sorted(all_keys):
        correct = correct_by_label.get(label, 0)
        incorrect = incorrect_by_label.get(label, 0)
        total_correct += correct
        total_incorrect += incorrect
        if correct == incorrect == 0:
            acc_by_label[label] = 0
        else:
            acc_by_label[label] = correct / (correct + incorrect)
    acc = 0
    if not (total_correct == total_incorrect == 0):
        acc = total_correct / (total_correct + total_incorrect)
    return acc, acc_by_label


def check_kb(kb):
    for mention in ("Bush", "Douglas Adams", "Homer", "Brazil", "China"):
        candidates = kb.get_candidates(mention)

        print("generating candidates for " + mention + " :")
        for c in candidates:
            print(" ", c.prior_prob, c.alias_, "-->", c.entity_ + " (freq=" + str(c.entity_freq) + ")")
        print()


def run_el_toy_example(nlp):
    text = "In The Hitchhiker's Guide to the Galaxy, written by Douglas Adams, " \
           "Douglas reminds us to always bring our towel, even in China or Brazil. " \
           "The main character in Doug's novel is the man Arthur Dent, " \
           "but Douglas doesn't write about George Washington or Homer Simpson."
    doc = nlp(text)
    print(text)
    for ent in doc.ents:
        print(" ent", ent.text, ent.label_, ent.kb_id_)
    print()


if __name__ == "__main__":
    run_pipeline()
