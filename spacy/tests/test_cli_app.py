import os
from pathlib import Path

import pytest
from typer.testing import CliRunner
from spacy.tokens import DocBin, Doc, Span
from spacy.lang.en import English

from spacy.cli._util import app
from .util import make_tempdir


def test_convert_auto():
    with make_tempdir() as d_in, make_tempdir() as d_out:
        for f in ["data1.iob", "data2.iob", "data3.iob"]:
            Path(d_in / f).touch()

        # ensure that "automatic" suffix detection works
        result = CliRunner().invoke(app, ["convert", str(d_in), str(d_out)])
        assert "Generated output file" in result.stdout
        out_files = os.listdir(d_out)
        assert len(out_files) == 3
        assert "data1.spacy" in out_files
        assert "data2.spacy" in out_files
        assert "data3.spacy" in out_files


def test_convert_auto_conflict():
    with make_tempdir() as d_in, make_tempdir() as d_out:
        for f in ["data1.iob", "data2.iob", "data3.json"]:
            Path(d_in / f).touch()

        # ensure that "automatic" suffix detection warns when there are different file types
        result = CliRunner().invoke(app, ["convert", str(d_in), str(d_out)])
        assert "All input files must be same type" in result.stdout
        out_files = os.listdir(d_out)
        assert len(out_files) == 0


def test_benchmark_accuracy_alias():
    # Verify that the `evaluate` alias works correctly.
    result_benchmark = CliRunner().invoke(app, ["benchmark", "accuracy", "--help"])
    result_evaluate = CliRunner().invoke(app, ["evaluate", "--help"])
    assert result_benchmark.stdout == result_evaluate.stdout.replace(
        "spacy evaluate", "spacy benchmark accuracy"
    )


@pytest.mark.slow
@pytest.mark.parametrize(
    "component,examples",
    [
        (
            "tagger",
            [
                dict(words=["I", "like", "cats"], tags=["PRP", "VBP", "NNS"]),
                dict(words=["I", "like", "dogs"], tags=["PRP", "VBP", "NNS"]),
            ],
        ),
        (
            "morphologizer",
            [
                dict(
                    words=["I", "like", "cats"],
                    morphs=[
                        "Case=Nom|Number=Sing|Person=1|PronType=Prs",
                        "Tense=Pres|VerbForm=Fin",
                        "Number=Plur",
                    ],
                ),
                dict(
                    words=["I", "like", "dogs"],
                    morphs=[
                        "Case=Nom|Number=Sing|Person=1|PronType=Prs",
                        "Tense=Pres|VerbForm=Fin",
                        "Number=Plur",
                    ],
                ),
            ],
        ),
        (
            "trainable_lemmatizer",
            [
                dict(words=["I", "like", "cats"], lemmas=["I", "like", "cat"]),
                dict(words=["I", "like", "dogs"], lemmas=["I", "like", "dog"]),
            ],
        ),
        (
            "parser",
            [
                dict(
                    words=["I", "like", "cats", "."],
                    deps=["nsubj", "ROOT", "dobj", "punct"],
                    heads=[1, 1, 1, 1],
                    pos=["PRON", "VERB", "NOUN", "PUNCT"],
                ),
            ]
            * 30,
        ),
        (
            "ner",
            [
                dict(words=["I", "like", "cats"], ents=["O", "O", "I-ANIMAL"]),
                dict(words=["I", "like", "dogs"], ents=["O", "O", "I-ANIMAL"]),
            ],
        ),
        (
            "spancat",
            [
                dict(words=["I", "like", "cats"], spans=[(2, 3, "ANIMAL")]),
                dict(words=["I", "like", "dogs"], spans=[(2, 3, "ANIMAL")]),
            ],
        ),
        (
            "textcat",
            [
                dict(words=["I", "like", "cats"], cats={"CAT": 1.0, "DOG": 0.0}),
                dict(words=["I", "like", "dogs"], cats={"CAT": 0.0, "DOG": 1.0}),
            ],
        ),
    ],
)
def test_init_config_trainable(component, examples):
    nlp = English()
    if component == "textcat":
        train_docs = []
        for example in examples:
            doc = Doc(nlp.vocab, words=example["words"])
            doc.cats = example["cats"]
            train_docs.append(doc)
    elif component == "spancat":
        train_docs = []
        for example in examples:
            doc = Doc(nlp.vocab, words=example["words"])
            doc.spans["sc"] = [
                Span(doc, start, end, label) for start, end, label in example["spans"]
            ]
            train_docs.append(doc)
    else:
        train_docs = [Doc(nlp.vocab, **example) for example in examples]

    with make_tempdir() as d_in:
        train_bin = DocBin(docs=train_docs)
        train_bin.to_disk(d_in / "train.spacy")
        dev_bin = DocBin(docs=train_docs)
        dev_bin.to_disk(d_in / "dev.spacy")
        init_config_result = CliRunner().invoke(
            app,
            [
                "init",
                "config",
                f"{d_in}/config.cfg",
                "--lang",
                "en",
                "--pipeline",
                component,
            ],
        )
        assert init_config_result.exit_code == 0
        train_result = CliRunner().invoke(
            app,
            [
                "train",
                f"{d_in}/config.cfg",
                "--paths.train",
                f"{d_in}/train.spacy",
                "--paths.dev",
                f"{d_in}/dev.spacy",
                "--output",
                f"{d_in}/model",
            ],
        )
        assert train_result.exit_code == 0
        assert Path(d_in / "model" / "model-last").exists()
