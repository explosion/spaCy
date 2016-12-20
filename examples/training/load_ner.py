# Load NER
from __future__ import unicode_literals
import spacy
import pathlib
from spacy.pipeline import EntityRecognizer
from spacy.vocab import Vocab

def load_model(model_dir):
    model_dir = pathlib.Path(model_dir)
    nlp = spacy.load('en', parser=False, entity=False, add_vectors=False)
    with (model_dir / 'vocab' / 'strings.json').open('r', encoding='utf8') as file_:
        nlp.vocab.strings.load(file_)
    nlp.vocab.load_lexemes(model_dir / 'vocab' / 'lexemes.bin')
    ner = EntityRecognizer.load(model_dir, nlp.vocab, require=True)
    return (nlp, ner)

(nlp, ner) = load_model('ner')
doc = nlp.make_doc('Who is Shaka Khan?')
nlp.tagger(doc)
ner(doc)
for word in doc:
    print(word.text, word.orth, word.lower, word.tag_, word.ent_type_, word.ent_iob)
