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


example_words_1 = ["I", "like", "cats"]
example_words_2 = ["I", "like", "dogs"]
example_lemmas_1 = ["I", "like", "cat"]
example_lemmas_2 = ["I", "like", "dog"]
example_tags = ["PRP", "VBP", "NNS"]
example_morphs = [
    "Case=Nom|Number=Sing|Person=1|PronType=Prs",
    "Tense=Pres|VerbForm=Fin",
    "Number=Plur",
]
example_deps = ["nsubj", "ROOT", "dobj"]
example_pos = ["PRON", "VERB", "NOUN"]
example_ents = ["O", "O", "I-ANIMAL"]
example_spans = [(2, 3, "ANIMAL")]

TRAIN_EXAMPLE_1 = dict(
    words=example_words_1,
    lemmas=example_lemmas_1,
    tags=example_tags,
    morphs=example_morphs,
    deps=example_deps,
    heads=[1, 1, 1],
    pos=example_pos,
    ents=example_ents,
    spans=example_spans,
    cats={"CAT": 1.0, "DOG": 0.0},
)
TRAIN_EXAMPLE_2 = dict(
    words=example_words_2,
    lemmas=example_lemmas_2,
    tags=example_tags,
    morphs=example_morphs,
    deps=example_deps,
    heads=[1, 1, 1],
    pos=example_pos,
    ents=example_ents,
    spans=example_spans,
    cats={"CAT": 0.0, "DOG": 1.0},
)


@pytest.mark.slow
@pytest.mark.parametrize(
    "component,examples",
    # fmt: off
    [
        ("tagger", [TRAIN_EXAMPLE_1, TRAIN_EXAMPLE_2]),
        ("morphologizer", [TRAIN_EXAMPLE_1, TRAIN_EXAMPLE_2]),
        ("trainable_lemmatizer", [TRAIN_EXAMPLE_1, TRAIN_EXAMPLE_2]),
        ("parser", [TRAIN_EXAMPLE_1] * 30),
        ("ner", [TRAIN_EXAMPLE_1, TRAIN_EXAMPLE_2]),
        ("spancat", [TRAIN_EXAMPLE_1, TRAIN_EXAMPLE_2]),
        ("textcat", [TRAIN_EXAMPLE_1, TRAIN_EXAMPLE_2]),
    ]
    # fmt: on
)
def test_init_config_trainable(component, examples, en_vocab):
    if component == "textcat":
        train_docs = []
        for example in examples:
            doc = Doc(en_vocab, words=example["words"])
            doc.cats = example["cats"]
            train_docs.append(doc)
    elif component == "spancat":
        train_docs = []
        for example in examples:
            doc = Doc(en_vocab, words=example["words"])
            doc.spans["sc"] = [
                Span(doc, start, end, label) for start, end, label in example["spans"]
            ]
            train_docs.append(doc)
    else:
        train_docs = []
        for example in examples:
            # cats, spans are not valid kwargs for instantiating a Doc
            example = {k: v for k, v in example.items() if k not in ("cats", "spans")}
            doc = Doc(en_vocab, **example)
            train_docs.append(doc)

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


@pytest.mark.slow
@pytest.mark.parametrize(
    "component,examples",
    # fmt: off
    [("tagger,parser,morphologizer", [TRAIN_EXAMPLE_1, TRAIN_EXAMPLE_2] * 15)]
    # fmt: on
)
def test_init_config_trainable_multiple(component, examples, en_vocab):
    train_docs = []
    for example in examples:
        example = {k: v for k, v in example.items() if k not in ("cats", "spans")}
        doc = Doc(en_vocab, **example)
        train_docs.append(doc)

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
