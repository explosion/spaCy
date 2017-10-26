#!/usr/bin/env python
# coding: utf8
"""
Example of training spaCy dependency parser, starting off with an existing model
or a blank model.

For more details, see the documentation:
* Training: https://alpha.spacy.io/usage/training
* Dependency Parse: https://alpha.spacy.io/usage/linguistic-features#dependency-parse

Developed for: spaCy 2.0.0a18
Last updated for: spaCy 2.0.0a18
"""
from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path

import spacy
from spacy.gold import GoldParse
from spacy.tokens import Doc


# training data
TRAIN_DATA = [
    (
        ['They', 'trade',  'mortgage', '-', 'backed', 'securities', '.'],
        [1, 1, 4, 4, 5, 1, 1],
        ['nsubj', 'ROOT', 'compound', 'punct', 'nmod', 'dobj', 'punct']
    ),
    (
        ['I', 'like', 'London', 'and', 'Berlin', '.'],
        [1, 1, 1, 2, 2, 1],
        ['nsubj', 'ROOT', 'dobj', 'cc', 'conj', 'punct']
    )
]


@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int))
def main(model=None, output_dir=None, n_iter=1000):
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

    # add labels to the parser
    for _, _, deps in TRAIN_DATA:
        for dep in deps:
            parser.add_label(dep)

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'parser']
    with nlp.disable_pipes(*other_pipes) as disabled:  # only train parser
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
    test_text = "I like securities."
    doc = nlp(test_text)
    print('Dependencies', [(t.text, t.dep_, t.head.text) for t in doc])

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the save model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        doc = nlp2(test_text)
        print('Dependencies', [(t.text, t.dep_, t.head.text) for t in doc])


if __name__ == '__main__':
    plac.call(main)

    # expected result:
    # [
    #   ('I', 'nsubj', 'like'),
    #   ('like', 'ROOT', 'like'),
    #   ('securities', 'dobj', 'like'),
    #   ('.', 'punct', 'like')
    # ]
