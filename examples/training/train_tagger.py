#!/usr/bin/env python
# coding: utf8
"""
A simple example for training a part-of-speech tagger with a custom tag map.
To allow us to update the tag map with our custom one, this example starts off
with a blank Language class and modifies its defaults.

For more details, see the documentation:
* Training: https://alpha.spacy.io/usage/training
* POS Tagging: https://alpha.spacy.io/usage/linguistic-features#pos-tagging

Developed for: spaCy 2.0.0a18
Last updated for: spaCy 2.0.0a18
"""
from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path

import spacy
from spacy.util import get_lang_class
from spacy.tokens import Doc
from spacy.gold import GoldParse


# You need to define a mapping from your data's part-of-speech tag names to the
# Universal Part-of-Speech tag set, as spaCy includes an enum of these tags.
# See here for the Universal Tag Set:
# http://universaldependencies.github.io/docs/u/pos/index.html
# You may also specify morphological features for your tags, from the universal
# scheme.
TAG_MAP = {
    'N': {"pos": "NOUN"},
    'V': {"pos": "VERB"},
    'J': {"pos": "ADJ"}
}

# Usually you'll read this in, of course. Data formats vary.
# Ensure your strings are unicode.
TRAIN_DATA = [
    (["I", "like", "green", "eggs"], ["N", "V", "J", "N"]),
    (["Eat", "blue", "ham"], ["V", "J", "N"])
]


@plac.annotations(
    lang=("ISO Code of language to use", "option", "l", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int))
def main(lang='en', output_dir=None, n_iter=25):
    """Create a new model, set up the pipeline and train the tagger. In order to
    train the tagger with a custom tag map, we're creating a new Language
    instance with a custom vocab.
    """
    lang_cls = get_lang_class(lang)  # get Language class
    lang_cls.Defaults.tag_map.update(TAG_MAP)  # add tag map to defaults
    nlp = lang_cls()  # initialise Language class

    # add the tagger to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    tagger = nlp.create_pipe('tagger')
    nlp.add_pipe(tagger)

    optimizer = nlp.begin_training(lambda: [])
    for i in range(n_iter):
        random.shuffle(TRAIN_DATA)
        losses = {}
        for words, tags in TRAIN_DATA:
            doc = Doc(nlp.vocab, words=words)
            gold = GoldParse(doc, tags=tags)
            nlp.update([doc], [gold], sgd=optimizer, losses=losses)
        print(losses)

    # test the trained model
    test_text = "I like blue eggs"
    doc = nlp(test_text)
    print('Tags', [(t.text, t.tag_, t.pos_) for t in doc])

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
        print('Tags', [(t.text, t.tag_, t.pos_) for t in doc])


if __name__ == '__main__':
    plac.call(main)

    # Expected output:
    # [
    #   ('I', 'N', 'NOUN'),
    #   ('like', 'V', 'VERB'),
    #   ('blue', 'J', 'ADJ'),
    #   ('eggs', 'N', 'NOUN')
    # ]
