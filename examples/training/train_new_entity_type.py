from __future__ import unicode_literals, print_function

import random
from pathlib import Path

import spacy
from spacy.gold import GoldParse
from spacy.tagger import Tagger


def train_ner(nlp, train_data, output_dir):
    # Add new words to vocab
    for raw_text, _ in train_data:
        doc = nlp.make_doc(raw_text)
        for word in doc:
            _ = nlp.vocab[word.orth]

    for itn in range(20):
        random.shuffle(train_data)
        for raw_text, entity_offsets in train_data:
            gold = GoldParse(doc, entities=entity_offsets)
            doc = nlp.make_doc(raw_text)
            nlp.tagger(doc)
            loss = nlp.entity.update(doc, gold)
    nlp.end_training()
    if output_dir:
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.save_to_directory(output_dir)


def main(model_name, output_directory=None):
    print("Loading initial model", model_name)
    nlp = spacy.load(model_name)
    if output_directory is not None:
        output_directory = Path(output_directory)

    train_data = [
        (
            "Horses are too tall and they pretend to care about your feelings",
            [(0, 6, 'ANIMAL')],
        ),
        (
            "horses are too tall and they pretend to care about your feelings",
            [(0, 6, 'ANIMAL')]
        ),
        (
            "horses pretend to care about your feelings",
            [(0, 6, 'ANIMAL')]
        ),
        (
            "they pretend to care about your feelings, those horses",
            [(48, 54, 'ANIMAL')]
        )
    ]
    nlp.entity.add_label('ANIMAL')
    train_ner(nlp, train_data, output_directory)

    # Test that the entity is recognized
    doc = nlp('Do you like horses?')
    for ent in doc.ents:
        print(ent.label_, ent.text)
    if output_directory:
        print("Loading from", output_directory)
        nlp2 = spacy.load('en', path=output_directory)
        nlp2.entity.add_label('ANIMAL')
        doc2 = nlp2('Do you like horses?')
        for ent in doc2.ents:
            print(ent.label_, ent.text)


if __name__ == '__main__':
    import plac
    plac.call(main)
