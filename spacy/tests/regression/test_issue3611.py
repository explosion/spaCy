# coding: utf8
from __future__ import unicode_literals

import pytest
import spacy
from spacy.util import minibatch, compounding


def test_issue3611():
    """ Test whether adding n-grams in the textcat works even when n > token length of some docs """
    unique_classes = ["offensive", "inoffensive"]
    x_train = ["This is an offensive text",
               "This is the second offensive text",
               "inoff"]
    y_train = ["offensive", "offensive", "inoffensive"]

    # preparing the data
    pos_cats = list()
    for train_instance in y_train:
        pos_cats.append({label: label == train_instance for label in unique_classes})
    train_data = list(zip(x_train, [{'cats': cats} for cats in pos_cats]))

    # set up the spacy model with a text categorizer component
    nlp = spacy.blank('en')

    textcat = nlp.create_pipe(
        "textcat",
        config={
            "exclusive_classes": True,
            "architecture": "bow",
            "ngram_size": 2
        }
    )

    for label in unique_classes:
        textcat.add_label(label)
    nlp.add_pipe(textcat, last=True)

    # training the network
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'textcat']
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        for i in range(3):
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))

            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(docs=texts, golds=annotations, sgd=optimizer, drop=0.1, losses=losses)


