# coding: utf-8
from __future__ import unicode_literals

import pytest

from spacy.lang.en import English
from spacy.cli.converters import conllu2json
from spacy.cli.pretrain import make_docs


def test_cli_converters_conllu2json():
    # https://raw.githubusercontent.com/ohenrik/nb_news_ud_sm/master/original_data/no-ud-dev-ner.conllu
    lines = [
        "1\tDommer\tdommer\tNOUN\t_\tDefinite=Ind|Gender=Masc|Number=Sing\t2\tappos\t_\tO",
        "2\tFinn\tFinn\tPROPN\t_\tGender=Masc\t4\tnsubj\t_\tB-PER",
        "3\tEilertsen\tEilertsen\tPROPN\t_\t_\t2\tname\t_\tI-PER",
        "4\tavstår\tavstå\tVERB\t_\tMood=Ind|Tense=Pres|VerbForm=Fin\t0\troot\t_\tO",
    ]
    input_data = "\n".join(lines)
    converted = conllu2json(input_data, n_sents=1)
    assert len(converted) == 1
    assert converted[0]["id"] == 0
    assert len(converted[0]["paragraphs"]) == 1
    assert len(converted[0]["paragraphs"][0]["sentences"]) == 1
    sent = converted[0]["paragraphs"][0]["sentences"][0]
    assert len(sent["tokens"]) == 4
    tokens = sent["tokens"]
    assert [t["orth"] for t in tokens] == ["Dommer", "Finn", "Eilertsen", "avstår"]
    assert [t["tag"] for t in tokens] == ["NOUN", "PROPN", "PROPN", "VERB"]
    assert [t["head"] for t in tokens] == [1, 2, -1, 0]
    assert [t["dep"] for t in tokens] == ["appos", "nsubj", "name", "ROOT"]
    assert [t["ner"] for t in tokens] == ["O", "B-PER", "L-PER", "O"]


def test_pretrain_make_docs():
    nlp = English()

    valid_jsonl_text = {"text": "Some text"}
    docs, skip_count = make_docs(nlp, [valid_jsonl_text], 1, 10)
    assert len(docs) == 1
    assert skip_count == 0

    valid_jsonl_tokens = {"tokens": ["Some", "tokens"]}
    docs, skip_count = make_docs(nlp, [valid_jsonl_tokens], 1, 10)
    assert len(docs) == 1
    assert skip_count == 0

    invalid_jsonl_type = 0
    with pytest.raises(TypeError):
        make_docs(nlp, [invalid_jsonl_type], 1, 100)

    invalid_jsonl_key = {"invalid": "Does not matter"}
    with pytest.raises(ValueError):
        make_docs(nlp, [invalid_jsonl_key], 1, 100)

    empty_jsonl_text = {"text": ""}
    docs, skip_count = make_docs(nlp, [empty_jsonl_text], 1, 10)
    assert len(docs) == 0
    assert skip_count == 1

    empty_jsonl_tokens = {"tokens": []}
    docs, skip_count = make_docs(nlp, [empty_jsonl_tokens], 1, 10)
    assert len(docs) == 0
    assert skip_count == 1

    too_short_jsonl = {"text": "This text is not long enough"}
    docs, skip_count = make_docs(nlp, [too_short_jsonl], 10, 15)
    assert len(docs) == 0
    assert skip_count == 0

    too_long_jsonl = {"text": "This text contains way too much tokens for this test"}
    docs, skip_count = make_docs(nlp, [too_long_jsonl], 1, 5)
    assert len(docs) == 0
    assert skip_count == 0
