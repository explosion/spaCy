from spacy.gold import Corpus
from spacy.lang.en import English

from ..util import make_tempdir
from ...gold.converters import json2docs
from ...tokens import DocBin


def test_issue4402():
    nlp = English()
    with make_tempdir() as tmpdir:
        output_file = tmpdir / "test4402.spacy"
        docs = json2docs([json_data])
        data = DocBin(docs=docs, attrs =["ORTH", "SENT_START", "ENT_IOB", "ENT_TYPE"]).to_bytes()
        with output_file.open("wb") as file_:
            file_.write(data)
        corpus = Corpus(train_loc=str(output_file), dev_loc=str(output_file))

        train_data = list(corpus.train_dataset(nlp))
        assert len(train_data) == 2

        split_train_data = []
        for eg in train_data:
            split_train_data.extend(eg.split_sents())
        assert len(split_train_data) == 4


json_data =\
    {
        "id": 0,
        "paragraphs": [
            {
                "raw": "How should I cook bacon in an oven?\nI've heard of people cooking bacon in an oven.",
                "sentences": [
                    {
                        "tokens": [
                            {"id": 0, "orth": "How", "ner": "O"},
                            {"id": 1, "orth": "should", "ner": "O"},
                            {"id": 2, "orth": "I", "ner": "O"},
                            {"id": 3, "orth": "cook", "ner": "O"},
                            {"id": 4, "orth": "bacon", "ner": "O"},
                            {"id": 5, "orth": "in", "ner": "O"},
                            {"id": 6, "orth": "an", "ner": "O"},
                            {"id": 7, "orth": "oven", "ner": "O"},
                            {"id": 8, "orth": "?", "ner": "O"},
                        ],
                        "brackets": [],
                    },
                    {
                        "tokens": [
                            {"id": 9, "orth": "\n", "ner": "O"},
                            {"id": 10, "orth": "I", "ner": "O"},
                            {"id": 11, "orth": "'ve", "ner": "O"},
                            {"id": 12, "orth": "heard", "ner": "O"},
                            {"id": 13, "orth": "of", "ner": "O"},
                            {"id": 14, "orth": "people", "ner": "O"},
                            {"id": 15, "orth": "cooking", "ner": "O"},
                            {"id": 16, "orth": "bacon", "ner": "O"},
                            {"id": 17, "orth": "in", "ner": "O"},
                            {"id": 18, "orth": "an", "ner": "O"},
                            {"id": 19, "orth": "oven", "ner": "O"},
                            {"id": 20, "orth": ".", "ner": "O"},
                        ],
                        "brackets": [],
                    },
                ],
                "cats": [
                    {"label": "baking", "value": 1.0},
                    {"label": "not_baking", "value": 0.0},
                ],
            },
            {
                "raw": "What is the difference between white and brown eggs?\n",
                "sentences": [
                    {
                        "tokens": [
                            {"id": 0, "orth": "What", "ner": "O"},
                            {"id": 1, "orth": "is", "ner": "O"},
                            {"id": 2, "orth": "the", "ner": "O"},
                            {"id": 3, "orth": "difference", "ner": "O"},
                            {"id": 4, "orth": "between", "ner": "O"},
                            {"id": 5, "orth": "white", "ner": "O"},
                            {"id": 6, "orth": "and", "ner": "O"},
                            {"id": 7, "orth": "brown", "ner": "O"},
                            {"id": 8, "orth": "eggs", "ner": "O"},
                            {"id": 9, "orth": "?", "ner": "O"},
                        ],
                        "brackets": [],
                    },
                    {"tokens": [{"id": 10, "orth": "\n", "ner": "O"}], "brackets": []},
                ],
                "cats": [
                    {"label": "baking", "value": 0.0},
                    {"label": "not_baking", "value": 1.0},
                ],
            },
        ],
    }
