from __future__ import unicode_literals, print_function
import json
import pathlib
import random

import spacy
from spacy.pipeline import EntityRecognizer
from spacy.gold import GoldParse
from spacy.tagger import Tagger

 
try:
    unicode
except:
    unicode = str


def train_ner(nlp, train_data, entity_types):
    # Add new words to vocab.
    for raw_text, _ in train_data:
        doc = nlp.make_doc(raw_text)
        for word in doc:
            _ = nlp.vocab[word.orth]

    # Train NER.
    ner = EntityRecognizer(nlp.vocab, entity_types=entity_types)
    for itn in range(5):
        random.shuffle(train_data)
        for raw_text, entity_offsets in train_data:
            doc = nlp.make_doc(raw_text)
            gold = GoldParse(doc, entities=entity_offsets)
            ner.update(doc, gold)
    return ner

def save_model(ner, model_dir):
    model_dir = pathlib.Path(model_dir)
    if not model_dir.exists():
        model_dir.mkdir()
    assert model_dir.is_dir()

    with (model_dir / 'config.json').open('wb') as file_:
        data = json.dumps(ner.cfg)
        if isinstance(data, unicode):
            data = data.encode('utf8')
        file_.write(data)
    ner.model.dump(str(model_dir / 'model'))
    if not (model_dir / 'vocab').exists():
        (model_dir / 'vocab').mkdir()
    ner.vocab.dump(str(model_dir / 'vocab' / 'lexemes.bin'))
    with (model_dir / 'vocab' / 'strings.json').open('w', encoding='utf8') as file_:
        ner.vocab.strings.dump(file_)


def main(model_dir=None):
    nlp = spacy.load('en', parser=False, entity=False, add_vectors=False)

    # v1.1.2 onwards
    if nlp.tagger is None:
        print('---- WARNING ----')
        print('Data directory not found')
        print('please run: `python -m spacy.en.download --force all` for better performance')
        print('Using feature templates for tagging')
        print('-----------------')
        nlp.tagger = Tagger(nlp.vocab, features=Tagger.feature_templates)

    train_data = [
        (
            'Who is Shaka Khan?',
            [(len('Who is '), len('Who is Shaka Khan'), 'PERSON')]
        ),
        (
            'I like London and Berlin.',
            [(len('I like '), len('I like London'), 'LOC'),
            (len('I like London and '), len('I like London and Berlin'), 'LOC')]
        )
    ]
    ner = train_ner(nlp, train_data, ['PERSON', 'LOC'])

    doc = nlp.make_doc('Who is Shaka Khan?')
    nlp.tagger(doc)
    ner(doc)
    for word in doc:
        print(word.text, word.orth, word.lower, word.tag_, word.ent_type_, word.ent_iob)

    if model_dir is not None:
        save_model(ner, model_dir)





if __name__ == '__main__':
    main('ner')
    # Who "" 2
    # is "" 2
    # Shaka "" PERSON 3
    # Khan "" PERSON 1
    # ? "" 2
