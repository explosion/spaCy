import pytest
import spacy

from typing import List
from spacy.training import Example


TRAIN_DATA = [
    (
        'Who is Kofi Annan?',
        {
            'entities': [(7, 18, 'PERSON')],
            'tags': ['PRON', 'AUX', 'PROPN', 'PRON', 'PUNCT'],
            'heads': [1, 1, 3, 1, 1],
            'deps': ['attr', 'ROOT', 'compound', 'nsubj', 'punct']
        }
    ),
    (
        'Who is Steve Jobs?',
        {
            'entities': [(7, 17, 'PERSON')],
            'tags': ['PRON', 'AUX', 'PROPN', 'PRON', 'PUNCT'],
            'heads': [1, 1, 3, 1, 1],
            'deps': ['attr', 'ROOT', 'compound', 'nsubj', 'punct']
        }
    ),
    (
        'Bob is a nice person.',
        {
            'entities': [(0, 3, 'PERSON')],
            'tags': ['PROPN', 'AUX', 'DET', 'ADJ', 'NOUN', 'PUNCT'],
            'heads': [1, 1, 4, 4, 1, 1],
            'deps': ['nsubj', 'ROOT', 'det', 'amod', 'attr', 'punct']
        }
    ),
    (
        'Hi Anil, how are you?',
        {
            'entities': [(3, 7, 'PERSON')],
            'tags': ['INTJ', 'PROPN', 'PUNCT', 'ADV', 'AUX', 'PRON', 'PUNCT'],
            'deps': ['intj', 'npadvmod', 'punct', 'advmod', 'ROOT', 'nsubj', 'punct'],
            'heads': [4, 0, 4, 4, 4, 4, 4]
        }
    ),
    (
        'I like London and Berlin.',
        {
            'entities': [(7, 13, 'LOC'), (18, 24, 'LOC')],
            'tags': ['PROPN', 'VERB', 'PROPN', 'CCONJ', 'PROPN', 'PUNCT'],
            'deps': ['nsubj', 'ROOT', 'dobj', 'cc', 'conj', 'punct'],
            'heads': [1, 1, 1, 2, 2, 1]
        }
    )
]

REHEARSE_DATA = [
    (
        'Hi Anil',
        {
            'entities': [(3, 7, 'PERSON')],
            'tags': ['INTJ', 'PROPN'],
            'deps': ['ROOT', 'npadvmod'],
            'heads': [0, 0]
        }
    ),
    (
        'Hi Ravish, how you doing?',
        {
            'entities': [(3, 9, 'PERSON')],
            'tags': ['INTJ', 'PROPN', 'PUNCT', 'ADV', 'AUX', 'PRON', 'PUNCT'],
            'deps': ['intj', 'ROOT', 'punct', 'advmod', 'nsubj', 'advcl', 'punct'],
            'heads': [1, 1, 1, 5, 5, 1, 1]
        }
    ),
    # UTENCIL new label
    (
        'Natasha bought new forks.',
        {
            'entities': [(0, 7, 'PERSON'), (19, 24, 'UTENSIL')],
            'tags': ['PROPN', 'VERB', 'ADJ', 'NOUN', 'PUNCT'],
            'deps': ['nsubj', 'ROOT', 'amod', 'dobj', 'punct'],
            'heads': [1, 1, 3, 1, 1]
        }
    )
]


def _add_ner_label(ner, data):
    for _, annotations in data:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])


def _add_tagger_label(tagger, data):
    for _, annotations in data:
        for tag in annotations.get('tags'):
            tagger.add_label(tag)


def _add_parser_label(parser, data):
    for _, annotations in data:
        for dep in annotations.get('deps'):
            parser.add_label(dep)


def _opt_loop(
        nlp,
        component: str,
        data: List,
        rehearse: bool
):
    """Run either train or rehearse."""
    pipe = nlp.get_pipe(component)
    if component == 'ner':
        _add_ner_label(pipe, data)
    elif component == 'tagger':
        _add_tagger_label(pipe, data)
    elif component == 'parser':
        _add_tagger_label(pipe, data)
    else:
        raise NotImplementedError

    if rehearse:
        optimizer = nlp.resume_training()
    else:
        optimizer = nlp.initialize()

    for _ in range(5):
        for text, annotation in data:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotation)
            if rehearse:
                nlp.rehearse([example], sgd=optimizer)
            else:
                nlp.update([example], sgd=optimizer)
    return nlp


@pytest.mark.parametrize("component", ['ner', 'tagger', 'parser'])
def test_rehearse(component):
    nlp = spacy.blank("en")
    nlp.add_pipe(component)
    nlp = _opt_loop(nlp, component, TRAIN_DATA, False)
    _opt_loop(nlp, component, REHEARSE_DATA, True)


test_rehearse('parser')
