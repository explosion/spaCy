# coding: utf-8
"""Script to take a previously created Knowledge Base and train an entity linking
pipeline. The provided KB directory should hold the kb, the original nlp object and
its vocab used to create the KB, and a few auxiliary files such as the entity definitions,
as created by the script `wikidata_create_kb`.

For the Wikipedia dump: get enwiki-latest-pages-articles-multistream.xml.bz2
from https://dumps.wikimedia.org/enwiki/latest/

"""
from __future__ import unicode_literals

import random
import datetime
from pathlib import Path
import plac

from bin.wiki_entity_linking import training_set_creator

import spacy
from spacy.kb import KnowledgeBase
from spacy.util import minibatch, compounding


def now():
    return datetime.datetime.now()


@plac.annotations(
    dir_kb=("Directory with KB, NLP and related files", "positional", None, Path),
    output_dir=("Output directory", "option", "o", Path),
    loc_training=("Location to training data", "option", "k", Path),
    wp_xml=("Path to the downloaded Wikipedia XML dump.", "option", "w", Path),
    epochs=("Number of training iterations (default 10)", "option", "e", int),
    dropout=("Dropout to prevent overfitting (default 0.5)", "option", "p", float),
    lr=("Learning rate (default 0.005)", "option", "n", float),
    l2=("L2 regularization", "option", "r", float),
    train_inst=("# training instances (default 90% of all)", "option", "t", int),
    dev_inst=("# test instances (default 10% of all)", "option", "d", int),
    limit=("Optional threshold to limit lines read from WP dump", "option", "l", int),
)
def main(
    dir_kb,
    output_dir=None,
    loc_training=None,
    wp_xml=None,
    epochs=10,
    dropout=0.5,
    lr=0.005,
    l2=1e-6,
    train_inst=None,
    dev_inst=None,
    limit=None,
):
    print(now(), "Creating Entity Linker with Wikipedia and WikiData")
    print()

    # STEP 0: set up IO
    if output_dir and not output_dir.exists():
        output_dir.mkdir()

    # STEP 1 : load the NLP object
    nlp_dir = dir_kb / "nlp"
    print(now(), "STEP 1: loading model from", nlp_dir)
    nlp = spacy.load(nlp_dir)

    # check that there is a NER component in the pipeline
    if "ner" not in nlp.pipe_names:
        raise ValueError("The `nlp` object should have a pre-trained `ner` component.")

    # STEP 2 : read the KB
    print()
    print(now(), "STEP 2: reading the KB from", dir_kb / "kb")
    kb = KnowledgeBase(vocab=nlp.vocab)
    kb.load_bulk(dir_kb / "kb")

    # STEP 3: create a training dataset from WP
    print()
    if loc_training:
        print(now(), "STEP 3: reading training dataset from", loc_training)
    else:
        if not wp_xml:
            raise ValueError(
                "Either provide a path to a preprocessed training directory, "
                "or to the original Wikipedia XML dump."
            )

        if output_dir:
            loc_training = output_dir / "training_data"
        else:
            loc_training = dir_kb / "training_data"
        if not loc_training.exists():
            loc_training.mkdir()
        print(now(), "STEP 3: creating training dataset at", loc_training)

        if limit is not None:
            print("Warning: reading only", limit, "lines of Wikipedia dump.")

        loc_entity_defs = dir_kb / "entity_defs.csv"
        training_set_creator.create_training(
            wikipedia_input=wp_xml,
            entity_def_input=loc_entity_defs,
            training_output=loc_training,
            limit=limit,
        )

    # STEP 4: parse the training data
    print()
    print(now(), "STEP 4: parse the training & evaluation data")

    # for training, get pos & neg instances that correspond to entries in the kb
    print("Parsing training data, limit =", train_inst)
    train_data = training_set_creator.read_training(
        nlp=nlp, training_dir=loc_training, dev=False, limit=train_inst, kb=kb
    )

    print("Training on", len(train_data), "articles")
    print()

    print("Parsing dev testing data, limit =", dev_inst)
    # for testing, get all pos instances, whether or not they are in the kb
    dev_data = training_set_creator.read_training(
        nlp=nlp, training_dir=loc_training, dev=True, limit=dev_inst, kb=None
    )

    print("Dev testing on", len(dev_data), "articles")
    print()

    # STEP 5: create and train the entity linking pipe
    print()
    print(now(), "STEP 5: training Entity Linking pipe")

    el_pipe = nlp.create_pipe(
        name="entity_linker", config={"pretrained_vectors": nlp.vocab.vectors.name}
    )
    el_pipe.set_kb(kb)
    nlp.add_pipe(el_pipe, last=True)

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "entity_linker"]
    with nlp.disable_pipes(*other_pipes):  # only train Entity Linking
        optimizer = nlp.begin_training()
        optimizer.learn_rate = lr
        optimizer.L2 = l2

    if not train_data:
        print("Did not find any training data")
    else:
        for itn in range(epochs):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 128.0, 1.001))
            batchnr = 0

            with nlp.disable_pipes(*other_pipes):
                for batch in batches:
                    try:
                        docs, golds = zip(*batch)
                        nlp.update(
                            docs=docs,
                            golds=golds,
                            sgd=optimizer,
                            drop=dropout,
                            losses=losses,
                        )
                        batchnr += 1
                    except Exception as e:
                        print("Error updating batch:", e)

                if batchnr > 0:
                    el_pipe.cfg["incl_context"] = True
                    el_pipe.cfg["incl_prior"] = True
                    dev_acc_context, _ = _measure_acc(dev_data, el_pipe)
                    losses["entity_linker"] = losses["entity_linker"] / batchnr
                    print(
                        "Epoch, train loss",
                        itn,
                        round(losses["entity_linker"], 2),
                        " / dev accuracy avg",
                        round(dev_acc_context, 3),
                    )

    # STEP 6: measure the performance of our trained pipe on an independent dev set
    print()
    if len(dev_data):
        print()
        print(now(), "STEP 6: performance measurement of Entity Linking pipe")
        print()

        counts, acc_r, acc_r_d, acc_p, acc_p_d, acc_o, acc_o_d = _measure_baselines(
            dev_data, kb
        )
        print("dev counts:", sorted(counts.items(), key=lambda x: x[0]))

        oracle_by_label = [(x, round(y, 3)) for x, y in acc_o_d.items()]
        print("dev accuracy oracle:", round(acc_o, 3), oracle_by_label)

        random_by_label = [(x, round(y, 3)) for x, y in acc_r_d.items()]
        print("dev accuracy random:", round(acc_r, 3), random_by_label)

        prior_by_label = [(x, round(y, 3)) for x, y in acc_p_d.items()]
        print("dev accuracy prior:", round(acc_p, 3), prior_by_label)

        # using only context
        el_pipe.cfg["incl_context"] = True
        el_pipe.cfg["incl_prior"] = False
        dev_acc_context, dev_acc_cont_d = _measure_acc(dev_data, el_pipe)
        context_by_label = [(x, round(y, 3)) for x, y in dev_acc_cont_d.items()]
        print("dev accuracy context:", round(dev_acc_context, 3), context_by_label)

        # measuring combined accuracy (prior + context)
        el_pipe.cfg["incl_context"] = True
        el_pipe.cfg["incl_prior"] = True
        dev_acc_combo, dev_acc_combo_d = _measure_acc(dev_data, el_pipe)
        combo_by_label = [(x, round(y, 3)) for x, y in dev_acc_combo_d.items()]
        print("dev accuracy prior+context:", round(dev_acc_combo, 3), combo_by_label)

    # STEP 7: apply the EL pipe on a toy example
    print()
    print(now(), "STEP 7: applying Entity Linking to toy example")
    print()
    run_el_toy_example(nlp=nlp)

    # STEP 8: write the NLP pipeline (including entity linker) to file
    if output_dir:
        print()
        nlp_loc = output_dir / "nlp"
        print(now(), "STEP 8: Writing trained NLP to", nlp_loc)
        nlp.to_disk(nlp_loc)
        print()

    print()
    print(now(), "Done!")


def _measure_acc(data, el_pipe=None, error_analysis=False):
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
            for entity, kb_dict in gold.links.items():
                start, end = entity
                # only evaluating on positive examples
                for gold_kb, value in kb_dict.items():
                    if value:
                        offset = _offset(start, end)
                        correct_entries_per_article[offset] = gold_kb

            for ent in doc.ents:
                ent_label = ent.label_
                pred_entity = ent.kb_id_
                start = ent.start_char
                end = ent.end_char
                offset = _offset(start, end)
                gold_entity = correct_entries_per_article.get(offset, None)
                # the gold annotations are not complete so we can't evaluate missing annotations as 'wrong'
                if gold_entity is not None:
                    if gold_entity == pred_entity:
                        correct = correct_by_label.get(ent_label, 0)
                        correct_by_label[ent_label] = correct + 1
                    else:
                        incorrect = incorrect_by_label.get(ent_label, 0)
                        incorrect_by_label[ent_label] = incorrect + 1
                        if error_analysis:
                            print(ent.text, "in", doc)
                            print(
                                "Predicted",
                                pred_entity,
                                "should have been",
                                gold_entity,
                            )
                            print()

        except Exception as e:
            print("Error assessing accuracy", e)

    acc, acc_by_label = calculate_acc(correct_by_label, incorrect_by_label)
    return acc, acc_by_label


def _measure_baselines(data, kb):
    # Measure 3 performance baselines: random selection, prior probabilities, and 'oracle' prediction for upper bound
    counts_d = dict()

    random_correct_d = dict()
    random_incorrect_d = dict()

    oracle_correct_d = dict()
    oracle_incorrect_d = dict()

    prior_correct_d = dict()
    prior_incorrect_d = dict()

    docs = [d for d, g in data if len(d) > 0]
    golds = [g for d, g in data if len(d) > 0]

    for doc, gold in zip(docs, golds):
        try:
            correct_entries_per_article = dict()
            for entity, kb_dict in gold.links.items():
                start, end = entity
                for gold_kb, value in kb_dict.items():
                    # only evaluating on positive examples
                    if value:
                        offset = _offset(start, end)
                        correct_entries_per_article[offset] = gold_kb

            for ent in doc.ents:
                label = ent.label_
                start = ent.start_char
                end = ent.end_char
                offset = _offset(start, end)
                gold_entity = correct_entries_per_article.get(offset, None)

                # the gold annotations are not complete so we can't evaluate missing annotations as 'wrong'
                if gold_entity is not None:
                    counts_d[label] = counts_d.get(label, 0) + 1
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
                        prior_correct_d[label] = prior_correct_d.get(label, 0) + 1
                    else:
                        prior_incorrect_d[label] = prior_incorrect_d.get(label, 0) + 1

                    if gold_entity == random_candidate:
                        random_correct_d[label] = random_correct_d.get(label, 0) + 1
                    else:
                        random_incorrect_d[label] = random_incorrect_d.get(label, 0) + 1

                    if gold_entity == oracle_candidate:
                        oracle_correct_d[label] = oracle_correct_d.get(label, 0) + 1
                    else:
                        oracle_incorrect_d[label] = oracle_incorrect_d.get(label, 0) + 1

        except Exception as e:
            print("Error assessing accuracy", e)

    acc_prior, acc_prior_d = calculate_acc(prior_correct_d, prior_incorrect_d)
    acc_rand, acc_rand_d = calculate_acc(random_correct_d, random_incorrect_d)
    acc_oracle, acc_oracle_d = calculate_acc(oracle_correct_d, oracle_incorrect_d)

    return (
        counts_d,
        acc_rand,
        acc_rand_d,
        acc_prior,
        acc_prior_d,
        acc_oracle,
        acc_oracle_d,
    )


def _offset(start, end):
    return "{}_{}".format(start, end)


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
            print(
                " ",
                c.prior_prob,
                c.alias_,
                "-->",
                c.entity_ + " (freq=" + str(c.entity_freq) + ")",
            )
        print()


def run_el_toy_example(nlp):
    text = (
        "In The Hitchhiker's Guide to the Galaxy, written by Douglas Adams, "
        "Douglas reminds us to always bring our towel, even in China or Brazil. "
        "The main character in Doug's novel is the man Arthur Dent, "
        "but Dougledydoug doesn't write about George Washington or Homer Simpson."
    )
    doc = nlp(text)
    print(text)
    for ent in doc.ents:
        print(" ent", ent.text, ent.label_, ent.kb_id_)
    print()


if __name__ == "__main__":
    plac.call(main)
