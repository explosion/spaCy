import pytest

from spacy.lang.en import English
from spacy.cli.converters import conllu2json, iob2json, conll_ner2json
from spacy.cli.pretrain import make_docs


def test_cli_converters_conllu2json():
    # from NorNE: https://github.com/ltgoslo/norne/blob/3d23274965f513f23aa48455b28b1878dad23c05/ud/nob/no_bokmaal-ud-dev.conllu
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


def test_cli_converters_conllu2json_name_ner_map():
    lines = [
        "1\tDommer\tdommer\tNOUN\t_\tDefinite=Ind|Gender=Masc|Number=Sing\t2\tappos\t_\tname=O",
        "2\tFinn\tFinn\tPROPN\t_\tGender=Masc\t4\tnsubj\t_\tSpaceAfter=No|name=B-PER",
        "3\tEilertsen\tEilertsen\tPROPN\t_\t_\t2\tname\t_\tname=I-PER",
        "4\tavstår\tavstå\tVERB\t_\tMood=Ind|Tense=Pres|VerbForm=Fin\t0\troot\t_\tSpaceAfter=No|name=O",
        "5\t.\t$.\tPUNCT\t_\t_\t4\tpunct\t_\tname=B-BAD",
    ]
    input_data = "\n".join(lines)
    converted = conllu2json(input_data, n_sents=1, ner_map={"PER": "PERSON", "BAD": ""})
    assert len(converted) == 1
    assert converted[0]["id"] == 0
    assert len(converted[0]["paragraphs"]) == 1
    assert converted[0]["paragraphs"][0]["raw"] == "Dommer FinnEilertsen avstår."
    assert len(converted[0]["paragraphs"][0]["sentences"]) == 1
    sent = converted[0]["paragraphs"][0]["sentences"][0]
    assert len(sent["tokens"]) == 5
    tokens = sent["tokens"]
    assert [t["orth"] for t in tokens] == ["Dommer", "Finn", "Eilertsen", "avstår", "."]
    assert [t["tag"] for t in tokens] == ["NOUN", "PROPN", "PROPN", "VERB", "PUNCT"]
    assert [t["head"] for t in tokens] == [1, 2, -1, 0, -1]
    assert [t["dep"] for t in tokens] == ["appos", "nsubj", "name", "ROOT", "punct"]
    assert [t["ner"] for t in tokens] == ["O", "B-PERSON", "L-PERSON", "O", "O"]


def test_cli_converters_conllu2json_subtokens():
    # https://raw.githubusercontent.com/ohenrik/nb_news_ud_sm/master/original_data/no-ud-dev-ner.conllu
    lines = [
        "1\tDommer\tdommer\tNOUN\t_\tDefinite=Ind|Gender=Masc|Number=Sing\t2\tappos\t_\tname=O",
        "2-3\tFE\t_\t_\t_\t_\t_\t_\t_\t_",
        "2\tFinn\tFinn\tPROPN\t_\tGender=Masc\t4\tnsubj\t_\tname=B-PER",
        "3\tEilertsen\tEilertsen\tX\t_\tGender=Fem|Tense=past\t2\tname\t_\tname=I-PER",
        "4\tavstår\tavstå\tVERB\t_\tMood=Ind|Tense=Pres|VerbForm=Fin\t0\troot\t_\tSpaceAfter=No|name=O",
        "5\t.\t$.\tPUNCT\t_\t_\t4\tpunct\t_\tname=O",
    ]
    input_data = "\n".join(lines)
    converted = conllu2json(input_data, n_sents=1, merge_subtokens=True,
                            append_morphology=True)
    assert len(converted) == 1
    assert converted[0]["id"] == 0
    assert len(converted[0]["paragraphs"]) == 1
    assert converted[0]["paragraphs"][0]["raw"] == "Dommer FE avstår."
    assert len(converted[0]["paragraphs"][0]["sentences"]) == 1
    sent = converted[0]["paragraphs"][0]["sentences"][0]
    assert len(sent["tokens"]) == 4
    tokens = sent["tokens"]
    print(tokens)
    assert [t["orth"] for t in tokens] == ["Dommer", "FE", "avstår", "."]
    assert [t["tag"] for t in tokens] == [
        "NOUN__Definite=Ind|Gender=Masc|Number=Sing",
        "PROPN_X__Gender=Fem,Masc|Tense=past",
        "VERB__Mood=Ind|Tense=Pres|VerbForm=Fin",
        "PUNCT"
    ]
    assert [t["pos"] for t in tokens] == ['NOUN', 'PROPN', 'VERB', 'PUNCT']
    assert [t["morph"] for t in tokens] == ['Definite=Ind|Gender=Masc|Number=Sing', 'Gender=Fem,Masc|Tense=past', 'Mood=Ind|Tense=Pres|VerbForm=Fin', '']
    assert [t["lemma"] for t in tokens] == ['dommer', 'Finn Eilertsen', 'avstå', '$.']
    assert [t["head"] for t in tokens] == [1, 1, 0, -1]
    assert [t["dep"] for t in tokens] == ["appos", "nsubj", "ROOT", "punct"]
    assert [t["ner"] for t in tokens] == ["O", "U-PER", "O", "O"]


def test_cli_converters_iob2json():
    lines = [
        "I|O like|O London|I-GPE and|O New|B-GPE York|I-GPE City|I-GPE .|O",
        "I|O like|O London|B-GPE and|O New|B-GPE York|I-GPE City|I-GPE .|O",
        "I|PRP|O like|VBP|O London|NNP|I-GPE and|CC|O New|NNP|B-GPE York|NNP|I-GPE City|NNP|I-GPE .|.|O",
        "I|PRP|O like|VBP|O London|NNP|B-GPE and|CC|O New|NNP|B-GPE York|NNP|I-GPE City|NNP|I-GPE .|.|O",
    ]
    input_data = "\n".join(lines)
    converted = iob2json(input_data, n_sents=10)
    assert len(converted) == 1
    assert converted[0]["id"] == 0
    assert len(converted[0]["paragraphs"]) == 1
    assert len(converted[0]["paragraphs"][0]["sentences"]) == 4
    for i in range(0, 4):
        sent = converted[0]["paragraphs"][0]["sentences"][i]
        assert len(sent["tokens"]) == 8
        tokens = sent["tokens"]
        # fmt: off
        assert [t["orth"] for t in tokens] == ["I", "like", "London", "and", "New", "York", "City", "."]
        assert [t["ner"] for t in tokens] == ["O", "O", "U-GPE", "O", "B-GPE", "I-GPE", "L-GPE", "O"]
        # fmt: on


def test_cli_converters_conll_ner2json():
    lines = [
        "-DOCSTART- -X- O O",
        "",
        "I\tO",
        "like\tO",
        "London\tB-GPE",
        "and\tO",
        "New\tB-GPE",
        "York\tI-GPE",
        "City\tI-GPE",
        ".\tO",
        "",
        "I O",
        "like O",
        "London B-GPE",
        "and O",
        "New B-GPE",
        "York I-GPE",
        "City I-GPE",
        ". O",
        "",
        "I PRP O",
        "like VBP O",
        "London NNP B-GPE",
        "and CC O",
        "New NNP B-GPE",
        "York NNP I-GPE",
        "City NNP I-GPE",
        ". . O",
        "",
        "I PRP _ O",
        "like VBP _ O",
        "London NNP _ B-GPE",
        "and CC _ O",
        "New NNP _ B-GPE",
        "York NNP _ I-GPE",
        "City NNP _ I-GPE",
        ". . _ O",
        "",
        "I\tPRP\t_\tO",
        "like\tVBP\t_\tO",
        "London\tNNP\t_\tB-GPE",
        "and\tCC\t_\tO",
        "New\tNNP\t_\tB-GPE",
        "York\tNNP\t_\tI-GPE",
        "City\tNNP\t_\tI-GPE",
        ".\t.\t_\tO",
    ]
    input_data = "\n".join(lines)
    converted = conll_ner2json(input_data, n_sents=10)
    assert len(converted) == 1
    assert converted[0]["id"] == 0
    assert len(converted[0]["paragraphs"]) == 1
    assert len(converted[0]["paragraphs"][0]["sentences"]) == 5
    for i in range(0, 5):
        sent = converted[0]["paragraphs"][0]["sentences"][i]
        assert len(sent["tokens"]) == 8
        tokens = sent["tokens"]
        # fmt: off
        assert [t["orth"] for t in tokens] == ["I", "like", "London", "and", "New", "York", "City", "."]
        assert [t["ner"] for t in tokens] == ["O", "O", "U-GPE", "O", "B-GPE", "I-GPE", "L-GPE", "O"]
        # fmt: on


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
