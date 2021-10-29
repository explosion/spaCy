import pytest
from spacy.lang.en import English
import numpy as np
import spacy
from spacy.tokens import Doc
from spacy.matcher import PhraseMatcher
from spacy.tokens import DocBin
from spacy.util import load_config_from_str
from spacy.training import Example
from spacy.training.initialize import init_nlp
import pickle

from ..util import make_tempdir


def test_issue6730(en_vocab):
    """Ensure that the KB does not accept empty strings, but otherwise IO works fine."""
    from spacy.kb import KnowledgeBase

    kb = KnowledgeBase(en_vocab, entity_vector_length=3)
    kb.add_entity(entity="1", freq=148, entity_vector=[1, 2, 3])

    with pytest.raises(ValueError):
        kb.add_alias(alias="", entities=["1"], probabilities=[0.4])
    assert kb.contains_alias("") is False

    kb.add_alias(alias="x", entities=["1"], probabilities=[0.2])
    kb.add_alias(alias="y", entities=["1"], probabilities=[0.1])

    with make_tempdir() as tmp_dir:
        kb.to_disk(tmp_dir)
        kb.from_disk(tmp_dir)
    assert kb.get_size_aliases() == 2
    assert set(kb.get_alias_strings()) == {"x", "y"}


def test_issue6755(en_tokenizer):
    doc = en_tokenizer("This is a magnificent sentence.")
    span = doc[:0]
    assert span.text_with_ws == ""
    assert span.text == ""


@pytest.mark.parametrize(
    "sentence, start_idx,end_idx,label",
    [("Welcome to Mumbai, my friend", 11, 17, "GPE")],
)
def test_issue6815_1(sentence, start_idx, end_idx, label):
    nlp = English()
    doc = nlp(sentence)
    span = doc[:].char_span(start_idx, end_idx, label=label)
    assert span.label_ == label


@pytest.mark.parametrize(
    "sentence, start_idx,end_idx,kb_id", [("Welcome to Mumbai, my friend", 11, 17, 5)]
)
def test_issue6815_2(sentence, start_idx, end_idx, kb_id):
    nlp = English()
    doc = nlp(sentence)
    span = doc[:].char_span(start_idx, end_idx, kb_id=kb_id)
    assert span.kb_id == kb_id


@pytest.mark.parametrize(
    "sentence, start_idx,end_idx,vector",
    [("Welcome to Mumbai, my friend", 11, 17, np.array([0.1, 0.2, 0.3]))],
)
def test_issue6815_3(sentence, start_idx, end_idx, vector):
    nlp = English()
    doc = nlp(sentence)
    span = doc[:].char_span(start_idx, end_idx, vector=vector)
    assert (span.vector == vector).all()


def test_issue6839(en_vocab):
    """Ensure that PhraseMatcher accepts Span as input"""
    # fmt: off
    words = ["I", "like", "Spans", "and", "Docs", "in", "my", "input", ",", "and", "nothing", "else", "."]
    # fmt: on
    doc = Doc(en_vocab, words=words)
    span = doc[:8]
    pattern = Doc(en_vocab, words=["Spans", "and", "Docs"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add("SPACY", [pattern])
    matches = matcher(span)
    assert matches


CONFIG_ISSUE_6908 = """
[paths]
train = "TRAIN_PLACEHOLDER"
raw = null
init_tok2vec = null
vectors = null

[system]
seed = 0
gpu_allocator = null

[nlp]
lang = "en"
pipeline = ["textcat"]
tokenizer = {"@tokenizers":"spacy.Tokenizer.v1"}
disabled = []
before_creation = null
after_creation = null
after_pipeline_creation = null
batch_size = 1000

[components]

[components.textcat]
factory = "TEXTCAT_PLACEHOLDER"

[corpora]

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths:train}

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths:train}


[training]
train_corpus = "corpora.train"
dev_corpus = "corpora.dev"
seed = ${system.seed}
gpu_allocator = ${system.gpu_allocator}
frozen_components = []
before_to_disk = null

[pretraining]

[initialize]
vectors = ${paths.vectors}
init_tok2vec = ${paths.init_tok2vec}
vocab_data = null
lookups = null
before_init = null
after_init = null

[initialize.components]

[initialize.components.textcat]
labels = ['label1', 'label2']

[initialize.tokenizer]
"""


@pytest.mark.parametrize(
    "component_name",
    ["textcat", "textcat_multilabel"],
)
def test_issue6908(component_name):
    """Test intializing textcat with labels in a list"""

    def create_data(out_file):
        nlp = spacy.blank("en")
        doc = nlp.make_doc("Some text")
        doc.cats = {"label1": 0, "label2": 1}
        out_data = DocBin(docs=[doc]).to_bytes()
        with out_file.open("wb") as file_:
            file_.write(out_data)

    with make_tempdir() as tmp_path:
        train_path = tmp_path / "train.spacy"
        create_data(train_path)
        config_str = CONFIG_ISSUE_6908.replace("TEXTCAT_PLACEHOLDER", component_name)
        config_str = config_str.replace("TRAIN_PLACEHOLDER", train_path.as_posix())
        config = load_config_from_str(config_str)
        init_nlp(config)


CONFIG_ISSUE_6950 = """
[nlp]
lang = "en"
pipeline = ["tok2vec", "tagger"]

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v1"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = ${components.tok2vec.model.encode:width}
attrs = ["NORM","PREFIX","SUFFIX","SHAPE"]
rows = [5000,2500,2500,2500]
include_static_vectors = false

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v1"
width = 96
depth = 4
window_size = 1
maxout_pieces = 3

[components.ner]
factory = "ner"

[components.tagger]
factory = "tagger"

[components.tagger.model]
@architectures = "spacy.Tagger.v1"
nO = null

[components.tagger.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.encode:width}
upstream = "*"
"""


def test_issue6950():
    """Test that the nlp object with initialized tok2vec with listeners pickles
    correctly (and doesn't have lambdas).
    """
    nlp = English.from_config(load_config_from_str(CONFIG_ISSUE_6950))
    nlp.initialize(lambda: [Example.from_dict(nlp.make_doc("hello"), {"tags": ["V"]})])
    pickle.dumps(nlp)
    nlp("hello")
    pickle.dumps(nlp)
