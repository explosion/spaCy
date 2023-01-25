import os
from pathlib import Path
import pytest
import subprocess
from typer.testing import CliRunner

import spacy
from spacy.cli._util import app
from spacy.language import Language
from spacy.tokens import DocBin
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


NOOP_CONFIG = """
[paths]
train = null
dev = null
vectors = null
init_tok2vec = null

[system]
seed = 0
gpu_allocator = null

[nlp]
lang = "xx"
pipeline = ["noop", "noop2"]
disabled = []
before_creation = null
after_creation = null
after_pipeline_creation = null
batch_size = 1000
tokenizer = {"@tokenizers":"spacy.Tokenizer.v1"}

[components]

[components.noop]
factory = "noop"

[components.noop2]
factory = "noop2"

[corpora]

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths.dev}
gold_preproc = false
max_length = 0
limit = 0
augmenter = null

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths.train}
gold_preproc = false
max_length = 0
limit = 0
augmenter = null

[training]
seed = ${system.seed}
gpu_allocator = ${system.gpu_allocator}
dropout = 0.1
accumulate_gradient = 1
patience = 1600
max_epochs = 0
max_steps = 100
eval_frequency = 200
frozen_components = []
annotating_components = []
dev_corpus = "corpora.dev"

train_corpus = "corpora.train"
before_to_disk = null
before_update = null

[training.batcher]
@batchers = "spacy.batch_by_words.v1"
discard_oversize = false
tolerance = 0.2
get_length = null

[training.batcher.size]
@schedules = "compounding.v1"
start = 100
stop = 1000
compound = 1.001
t = 0.0

[training.logger]
@loggers = "spacy.ConsoleLogger.v1"
progress_bar = false

[training.optimizer]
@optimizers = "Adam.v1"
beta1 = 0.9
beta2 = 0.999
L2_is_weight_decay = true
L2 = 0.01
grad_clip = 1.0
use_averages = false
eps = 0.00000001
learn_rate = 0.001

[training.score_weights]

[pretraining]

[initialize]
vectors = ${paths.vectors}
init_tok2vec = ${paths.init_tok2vec}
vocab_data = null
lookups = null
before_init = null
after_init = null

[initialize.components]

[initialize.tokenizer]
"""


@pytest.fixture
def data_paths():
    nlp = spacy.blank("xx")
    doc = nlp("ok")
    with make_tempdir() as tdir:
        db = DocBin()
        # debug data will *fail* if there aren't enough docs
        for ii in range(100):
            db.add(doc)
        fpath = tdir / "data.spacy"
        db.to_disk(fpath)

        args = [
            "--paths.train",
            str(fpath),
            "--paths.dev",
            str(fpath),
        ]
        yield args


@pytest.fixture
def code_paths():
    noop_base = """
from spacy.language import Language

@Language.component("{}")
def noop(doc):
    return doc
"""

    with make_tempdir() as temp_d:
        # write code files to load
        paths = []
        for ff in ["noop", "noop2"]:
            pyfile = temp_d / f"{ff}.py"
            pyfile.write_text(noop_base.format(ff))
            paths.append(pyfile)

        args = ["--code", ",".join([str(pp) for pp in paths])]
        yield args


@pytest.fixture
def noop_config():
    with make_tempdir() as temp_d:
        cfg = temp_d / "config.cfg"
        cfg.write_text(NOOP_CONFIG)

        yield cfg


@pytest.mark.parametrize(
    "cmd",
    [
        ["debug", "config"],
        ["debug", "data"],
        ["train"],
        ["assemble"],
    ],
)
def test_multi_code(cmd, code_paths, data_paths, noop_config):
    # check that it fails without the code arg
    output = ["."] if cmd[0] in ("pretrain", "assemble") else []
    cmd = ["python", "-m", "spacy"] + cmd
    result = subprocess.run([*cmd, str(noop_config), *output, *data_paths])
    assert result.returncode == 1

    # check that it succeeds with the code arg
    result = subprocess.run(
        [
            *cmd,
            str(noop_config),
            *output,
            *data_paths,
            *code_paths,
        ]
    )
    assert result.returncode == 0
