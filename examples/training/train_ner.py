#!/usr/bin/env python
# coding: utf8
"""
Example of training spaCy's named entity recognizer, starting off with an
existing model or a blank model.

For more details, see the documentation:
* Training: https://alpha.spacy.io/usage/training
* NER: https://alpha.spacy.io/usage/linguistic-features#named-entities

Developed for: spaCy 2.0.0a18
Last updated for: spaCy 2.0.0a18
"""
from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path

import spacy
from spacy.gold import GoldParse, biluo_tags_from_offsets


# training data
TRAIN_DATA = [
    ('Who is Shaka Khan?', [(7, 17, 'PERSON')]),
    ('I like London and Berlin.', [(7, 13, 'LOC'), (18, 24, 'LOC')])
]


@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int))
def main(model=None, output_dir=None, n_iter=100):
    """Load the model, set up the pipeline and train the entity recognizer."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('en')  # create blank Language class
        print("Created blank 'en' model")

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner, last=True)

    # function that allows begin_training to get the training data
    get_data = lambda: reformat_train_data(nlp.tokenizer, TRAIN_DATA)

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        optimizer = nlp.begin_training(get_data)
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            for raw_text, entity_offsets in TRAIN_DATA:
                doc = nlp.make_doc(raw_text)
                gold = GoldParse(doc, entities=entity_offsets)
                nlp.update(
                    [doc], # Batch of Doc objects
                    [gold], # Batch of GoldParse objects
                    drop=0.5, # Dropout -- make it harder to memorise data
                    sgd=optimizer, # Callable to update weights
                    losses=losses)
            print(losses)

    # test the trained model
    for text, _ in TRAIN_DATA:
        doc = nlp(text)
        print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
        print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])

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
        for text, _ in TRAIN_DATA:
            doc = nlp2(text)
            print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
            print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])


def reformat_train_data(tokenizer, examples):
    """Reformat data to match JSON format.
    https://alpha.spacy.io/api/annotation#json-input

    tokenizer (Tokenizer): Tokenizer to process the raw text.
    examples (list): The trainig data.
    RETURNS (list): The reformatted training data."""
    output = []
    for i, (text, entity_offsets) in enumerate(examples):
        doc = tokenizer(text)
        ner_tags = biluo_tags_from_offsets(tokenizer(text), entity_offsets)
        words = [w.text for w in doc]
        tags = ['-'] * len(doc)
        heads = [0] * len(doc)
        deps = [''] * len(doc)
        sentence = (range(len(doc)), words, tags, heads, deps, ner_tags)
        output.append((text, [(sentence, [])]))
    return output


if __name__ == '__main__':
    plac.call(main)
