# coding: utf-8
from __future__ import unicode_literals
import json
from tempfile import NamedTemporaryFile
import pytest

from ...cli.train import train


@pytest.mark.xfail
def test_cli_trained_model_can_be_saved(tmpdir):
    lang = 'nl'
    output_dir = str(tmpdir)
    train_file = NamedTemporaryFile('wb', dir=output_dir, delete=False)
    train_corpus = [
        {
            "id": "identifier_0",
            "paragraphs": [
                {
                    "raw": "Jan houdt van Marie.\n",
                    "sentences": [
                        {
                            "tokens": [
                                {
                                    "id": 0,
                                    "dep": "nsubj",
                                    "head": 1,
                                    "tag": "NOUN",
                                    "orth": "Jan",
                                    "ner": "B-PER"
                                },
                                {
                                    "id": 1,
                                    "dep": "ROOT",
                                    "head": 0,
                                    "tag": "VERB",
                                    "orth": "houdt",
                                    "ner": "O"
                                },
                                {
                                    "id": 2,
                                    "dep": "case",
                                    "head": 1,
                                    "tag": "ADP",
                                    "orth": "van",
                                    "ner": "O"
                                },
                                {
                                    "id": 3,
                                    "dep": "obj",
                                    "head": -2,
                                    "tag": "NOUN",
                                    "orth": "Marie",
                                    "ner": "B-PER"
                                },
                                {
                                    "id": 4,
                                    "dep": "punct",
                                    "head": -3,
                                    "tag": "PUNCT",
                                    "orth": ".",
                                    "ner": "O"
                                },
                                {
                                    "id": 5,
                                    "dep": "",
                                    "head": -1,
                                    "tag": "SPACE",
                                    "orth": "\n",
                                    "ner": "O"
                                }
                            ],
                            "brackets": []
                        }
                    ]
                }
            ]
        }
    ]

    train_file.write(json.dumps(train_corpus).encode('utf-8'))
    train_file.close()
    train_data = train_file.name
    dev_data = train_data

    # spacy train -n 1 -g -1 nl output_nl training_corpus.json training \
    # corpus.json
    train(lang, output_dir, train_data, dev_data, n_iter=1)

    assert True
