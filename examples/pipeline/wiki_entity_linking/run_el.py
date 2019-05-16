# coding: utf-8
from __future__ import unicode_literals

import os
import spacy
import datetime
from os import listdir

from examples.pipeline.wiki_entity_linking import training_set_creator

# requires: pip install neuralcoref --no-binary neuralcoref
# import neuralcoref


def run_el_toy_example(nlp, kb):
    _prepare_pipeline(nlp, kb)

    candidates = kb.get_candidates("Bush")

    print("generating candidates for 'Bush' :")
    for c in candidates:
        print(" ", c.prior_prob, c.alias_, "-->", c.entity_ + " (freq=" + str(c.entity_freq) + ")")
    print()

    text = "In The Hitchhiker's Guide to the Galaxy, written by Douglas Adams, " \
           "Douglas reminds us to always bring our towel. " \
           "The main character in Doug's novel is the man Arthur Dent, " \
           "but Douglas doesn't write about George Washington or Homer Simpson."
    doc = nlp(text)

    for ent in doc.ents:
        print("ent", ent.text, ent.label_, ent.kb_id_)


def run_el_dev(nlp, kb, training_dir, limit=None):
    _prepare_pipeline(nlp, kb)

    correct_entries_per_article, _ = training_set_creator.read_training_entities(training_output=training_dir,
                                                                                 collect_correct=True,
                                                                                 collect_incorrect=False)

    predictions = list()
    golds = list()

    cnt = 0
    for f in listdir(training_dir):
        if not limit or cnt < limit:
            if is_dev(f):
                article_id = f.replace(".txt", "")
                if cnt % 500 == 0:
                    print(datetime.datetime.now(), "processed", cnt, "files in the dev dataset")
                cnt += 1
                with open(os.path.join(training_dir, f), mode="r", encoding='utf8') as file:
                    text = file.read()
                    doc = nlp(text)
                    for ent in doc.ents:
                        if ent.label_ == "PERSON":  # TODO: expand to other types
                            gold_entity = correct_entries_per_article[article_id].get(ent.text, None)
                            # only evaluating gold entities we know, because the training data is not complete
                            if gold_entity:
                                predictions.append(ent.kb_id_)
                                golds.append(gold_entity)

    print("Processed", cnt, "dev articles")
    print()
    evaluate(predictions, golds)


def is_dev(file_name):
    return file_name.endswith("3.txt")


def evaluate(predictions, golds, to_print=True):
    if len(predictions) != len(golds):
        raise ValueError("predictions and gold entities should have the same length")

    tp = 0
    fp = 0
    fn = 0

    for pred, gold in zip(predictions, golds):
        is_correct = pred == gold
        if not pred:
            if not is_correct:  # we don't care about tn
                fn += 1
        elif is_correct:
            tp += 1
        else:
            fp += 1

    if to_print:
        print("Evaluating", len(golds), "entities")
        print("tp", tp)
        print("fp", fp)
        print("fn", fn)

    precision = 100 * tp / (tp + fp + 0.0000001)
    recall = 100 * tp / (tp + fn + 0.0000001)
    fscore = 2 * recall * precision / (recall + precision + 0.0000001)

    if to_print:
        print("precision", round(precision, 1), "%")
        print("recall", round(recall, 1), "%")
        print("Fscore", round(fscore, 1), "%")

    return precision, recall, fscore


def _prepare_pipeline(nlp, kb):
    # TODO: the vocab objects are now different between nlp and kb - will be fixed when KB is written as part of NLP IO
    el_pipe = nlp.create_pipe(name='entity_linker', config={"kb": kb})
    nlp.add_pipe(el_pipe, last=True)


# TODO
def add_coref():
    """ Add coreference resolution to our model """
    nlp = spacy.load('en_core_web_sm')
    # nlp = spacy.load('en')

    # TODO: this doesn't work yet
    # neuralcoref.add_to_pipe(nlp)
    print("done adding to pipe")

    doc = nlp(u'My sister has a dog. She loves him.')
    print("done doc")

    print(doc._.has_coref)
    print(doc._.coref_clusters)


# TODO
def _run_ner_depr(nlp, clean_text, article_dict):
    doc = nlp(clean_text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":           # TODO: expand to non-persons
            ent_id = article_dict.get(ent.text)
            if ent_id:
                print(" -", ent.text, ent.label_, ent_id)
            else:
                print(" -", ent.text, ent.label_, '???')  # TODO: investigate these cases
