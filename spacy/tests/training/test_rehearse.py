import pytest
import spacy

from typing import List
from spacy.training import Example


NER_TRAIN = [
    (
        'Who is Kofi Annan?',
        {
            'entities': [(7, 18, 'PERSON')],
            'tags': ['PRON', 'AUX', 'PROPN', 'PRON', 'PUNCT']
        }
    ),
    (
        'Who is Steve Jobs?',
        {
            'entities': [(7, 17, 'PERSON')],
            'tags': ['PRON', 'AUX', 'PROPN', 'PRON', 'PUNCT']
        }
    ),
    (
        'Bob is a nice person.',
        {
            'entities': [(0, 3, 'PERSON')],
            'tags': ['PROPN', 'AUX', 'DET', 'ADJ', 'NOUN', 'PUNCT']
        }
    ),
    (
        'Hi Anil, how are you?',
        {
            'entities': [(3, 7, 'PERSON')],
            'tags': ['INTJ', 'PROPN', 'PUNCT', 'ADV', 'AUX', 'PRON', 'PUNCT']
        }
    ),
    (
        'I like London and Berlin.',
        {
            'entities': [(7, 13, 'LOC'), (18, 24, 'LOC')],
            'tags': ['PROPN', 'VERB', 'PROPN', 'CCONJ', 'PROPN', 'PUNCT']
        }
    )
]

NER_REHEARSE = [
    (
        'Hi Anil',
        {
            'entities': [(3, 7, 'PERSON')],
            'tags': ['INTJ', 'PROPN']
        }
    ),
    (
        'Hi Ravish, how you doing?',
        {
            'entities': [(3, 9, 'PERSON')],
            'tags': ['INTJ', 'PROPN', 'PUNCT', 'ADV', 'AUX', 'PRON', 'PUNCT']
        }
    ),
    # UTENCIL new label
    (
        'Natasha bought new forks.',
        {
            'entities': [(0, 7, 'PERSON'), (19, 24, 'UTENSIL')],
            'tags': ['PROPN', 'VERB', 'ADJ', 'NOUN', 'PUNCT']
        }
    )
]

DATA = {
    'ner': (NER_TRAIN, NER_REHEARSE),
    'tagger': (NER_TRAIN, NER_REHEARSE)
}


def _add_ner_label(ner, data):
    for _, annotations in data:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])


def _add_tagger_label(tagger, data):
    for _, annotations in data:
        for tag in annotations.get('tags'):
            tagger.add_label(tag)


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
    else:
        raise NotImplementedError

    if rehearse:
        optimizer = nlp.resume_training()
    else:
        optimizer = nlp.begin_training()

    for _ in range(5):
        for text, annotation in data:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotation)
            if rehearse:
                nlp.rehearse([example], sgd=optimizer)
            else:
                nlp.update([example], sgd=optimizer)
    return nlp


@pytest.mark.parametrize("component", ['ner', 'tagger'])
def test_rehearse_ner(component):
    nlp = spacy.blank("en")
    nlp.add_pipe(component)
    train_data, rehearse_data = DATA[component]
    nlp = _opt_loop(nlp, component, train_data, False)
    _opt_loop(nlp, component, rehearse_data, True)
