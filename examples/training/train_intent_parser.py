#!/usr/bin/env python
# coding: utf-8
"""Using the parser to recognise your own semantics

spaCy's parser component can be used to trained to predict any type of tree
structure over your input text. You can also predict trees over whole documents
or chat logs, with connections between the sentence-roots used to annotate
discourse structure. In this example, we'll build a message parser for a common
"chat intent": finding local businesses. Our message semantics will have the
following types of relations: ROOT, PLACE, QUALITY, ATTRIBUTE, TIME, LOCATION.

"show me the best hotel in berlin"
('show', 'ROOT', 'show')
('best', 'QUALITY', 'hotel') --> hotel with QUALITY best
('hotel', 'PLACE', 'show') --> show PLACE hotel
('berlin', 'LOCATION', 'hotel') --> hotel with LOCATION berlin
"""
from __future__ import unicode_literals, print_function

import plac
import random
import spacy
from spacy.gold import GoldParse
from spacy.tokens import Doc
from pathlib import Path


# training data: words, head and dependency labels
# for no relation, we simply chose an arbitrary dependency label, e.g. '-'
TRAIN_DATA = [
    (
        ['find', 'a', 'cafe', 'with', 'great', 'wifi'],
        [0, 2, 0, 5, 5, 2],  # index of token head
        ['ROOT', '-', 'PLACE', '-', 'QUALITY', 'ATTRIBUTE']
    ),
    (
        ['find', 'a', 'hotel', 'near', 'the', 'beach'],
        [0, 2, 0, 5, 5, 2],
        ['ROOT', '-', 'PLACE', 'QUALITY', '-', 'ATTRIBUTE']
    ),
    (
        ['find', 'me', 'the', 'closest', 'gym', 'that', "'s", 'open', 'late'],
        [0, 0, 4, 4, 0, 6, 4, 6, 6],
        ['ROOT', '-', '-', 'QUALITY', 'PLACE', '-', '-', 'ATTRIBUTE', 'TIME']
    ),
    (
        ['show', 'me', 'the', 'cheapest', 'store', 'that', 'sells', 'flowers'],
        [0, 0, 4, 4, 0, 4, 4, 4],  # attach "flowers" to store!
        ['ROOT', '-', '-', 'QUALITY', 'PLACE', '-', '-', 'PRODUCT']
    ),
    (
        ['find', 'a', 'nice', 'restaurant', 'in', 'london'],
        [0, 3, 3, 0, 3, 3],
        ['ROOT', '-', 'QUALITY', 'PLACE', '-', 'LOCATION']
    ),
    (
        ['show', 'me', 'the', 'coolest', 'hostel', 'in', 'berlin'],
        [0, 0, 4, 4, 0, 4, 4],
        ['ROOT', '-', '-', 'QUALITY', 'PLACE', '-', 'LOCATION']
    ),
    (
        ['find', 'a', 'good', 'italian', 'restaurant', 'near', 'work'],
        [0, 4, 4, 4, 0, 4, 5],
        ['ROOT', '-', 'QUALITY', 'ATTRIBUTE', 'PLACE', 'ATTRIBUTE', 'LOCATION']
    )
]


@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int))
def main(model=None, output_dir=None, n_iter=100):
    """Load the model, set up the pipeline and train the parser."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('en')  # create blank Language class
        print("Created blank 'en' model")

    # add the parser to the pipeline if it doesn't exist
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'parser' not in nlp.pipe_names:
        parser = nlp.create_pipe('parser')
        nlp.add_pipe(parser, first=True)
    # otherwise, get it, so we can add labels to it
    else:
        parser = nlp.get_pipe('parser')

    for _, _, deps in TRAIN_DATA:
        for dep in deps:
            parser.add_label(dep)

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'parser']
    with nlp.disable_pipes(*other_pipes):  # only train parser
        optimizer = nlp.begin_training(lambda: [])
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            for words, heads, deps in TRAIN_DATA:
                doc = Doc(nlp.vocab, words=words)
                gold = GoldParse(doc, heads=heads, deps=deps)
                nlp.update([doc], [gold], sgd=optimizer, losses=losses)
            print(losses)

    # test the trained model
    test_model(nlp)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        test_model(nlp2)


def test_model(nlp):
    texts = ["find a hotel with good wifi",
             "find me the cheapest gym near work",
             "show me the best hotel in berlin"]
    docs = nlp.pipe(texts)
    for doc in docs:
        print(doc.text)
        print([(t.text, t.dep_, t.head.text) for t in doc if t.dep_ != '-'])


if __name__ == '__main__':
    plac.call(main)

    # Expected output:
    # find a hotel with good wifi
    # [
    #   ('find', 'ROOT', 'find'),
    #   ('hotel', 'PLACE', 'find'),
    #   ('good', 'QUALITY', 'wifi'),
    #   ('wifi', 'ATTRIBUTE', 'hotel')
    # ]
    # find me the cheapest gym near work
    # [
    #   ('find', 'ROOT', 'find'),
    #   ('cheapest', 'QUALITY', 'gym'),
    #   ('gym', 'PLACE', 'find')
    # ]
    # show me the best hotel in berlin
    # [
    #   ('show', 'ROOT', 'show'),
    #   ('best', 'QUALITY', 'hotel'),
    #   ('hotel', 'PLACE', 'show'),
    #   ('berlin', 'LOCATION', 'hotel')
    # ]
