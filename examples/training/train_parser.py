from __future__ import unicode_literals, print_function
import json
import pathlib
import random

import spacy
from spacy.pipeline import DependencyParser
from spacy.gold import GoldParse
from spacy.tokens import Doc


def train_parser(nlp, train_data, left_labels, right_labels):
    parser = DependencyParser(
                nlp.vocab,
                left_labels=left_labels,
                right_labels=right_labels)
    for itn in range(1000):
        random.shuffle(train_data)
        loss = 0
        for words, heads, deps in train_data:
            doc = Doc(nlp.vocab, words=words)
            gold = GoldParse(doc, heads=heads, deps=deps)
            loss += parser.update(doc, gold)
    parser.model.end_training()
    return parser


def main(model_dir=None):
    if model_dir is not None:
        model_dir = pathlib.Path(model_dir)
        if not model_dir.exists():
            model_dir.mkdir()
        assert model_dir.is_dir()

    nlp = spacy.load('en', tagger=False, parser=False, entity=False, add_vectors=False)

    train_data = [
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
    left_labels = set()
    right_labels = set()
    for _, heads, deps in train_data:
        for i, (head, dep) in enumerate(zip(heads, deps)):
            if i < head:
                left_labels.add(dep)
            elif i > head:
                right_labels.add(dep)
    parser = train_parser(nlp, train_data, sorted(left_labels), sorted(right_labels))

    doc = Doc(nlp.vocab, words=['I', 'like', 'securities', '.'])
    parser(doc)
    for word in doc:
        print(word.text, word.dep_, word.head.text)

    if model_dir is not None:
        with (model_dir / 'config.json').open('w') as file_:
            json.dump(parser.cfg, file_)
        parser.model.dump(str(model_dir / 'model'))


if __name__ == '__main__':
    main()
    # I nsubj like
    # like ROOT like
    # securities dobj like
    # . cc securities
