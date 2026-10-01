import pytest
from typing import Iterable
import spacy
from spacy.training import Example
from spacy.training.initialize import init_nlp
from spacy import util
from thinc.api import ConfigValidationError


class CountingCorpus:
    """Mock corpus reader that records how many examples were yielded per generator call."""

    def __init__(self, total_examples: int = 50):
        self.total_examples = total_examples
        self.call_counts = []

    def __call__(self, nlp) -> Iterable[Example]:
        nlp_blank = spacy.blank("en")
        idx = len(self.call_counts)
        self.call_counts.append(0)
        for i in range(self.total_examples):
            self.call_counts[idx] += 1
            doc = nlp_blank.make_doc(f"This is example number {i}")
            doc.cats = {"LABEL": 1.0}
            yield Example.from_dict(doc, {"cats": {"LABEL": 1.0}})


SAMPLE_LIMIT_CONFIG = """
[paths]
train = null
dev = null
vectors = null
init_tok2vec = null

[system]
gpu_allocator = null
seed = 0

[nlp]
lang = "en"
pipeline = ["textcat_multilabel"]

[components]

[components.textcat_multilabel]
factory = "textcat_multilabel"

[corpora]

[corpora.train]
@readers = "test_counting_train_corpus"
total_examples = 50

[corpora.dev]
@readers = "test_counting_dev_corpus"

[training]
train_corpus = "corpora.train"
dev_corpus = "corpora.dev"
seed = ${system.seed}
gpu_allocator = ${system.gpu_allocator}
dropout = 0.1
accumulate_gradient = 1
patience = 1600
max_epochs = 5
max_steps = 1000
eval_frequency = 100
score_weights = {}
frozen_components = []
annotating_components = []
before_to_disk = null
before_update = null
init_max_examples = 5

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

[training.logger]
@loggers = "spacy.ConsoleLogger.v1"
progress_bar = false

[initialize]
vectors = ${paths.vectors}
init_tok2vec = ${paths.init_tok2vec}
vocab_data = null
lookups = null
tokenizer = {}
before_init = null
after_init = null

[initialize.components]

[initialize.components.textcat_multilabel]
labels = ["LABEL"]
"""


@pytest.mark.issue(13804)
def test_init_nlp_corpus_sample_limit():
    """Verify that init_max_examples bounds each generator iteration during init_nlp."""
    train_corpus = CountingCorpus(total_examples=50)

    @spacy.registry.readers("test_counting_train_corpus")
    def create_train_corpus(total_examples: int = 50):
        return train_corpus

    @spacy.registry.readers("test_counting_dev_corpus")
    def create_dev_corpus():
        return CountingCorpus(total_examples=10)

    config = util.load_config_from_str(SAMPLE_LIMIT_CONFIG)
    init_nlp(config)

    # When init_max_examples = 5, no generator pass should yield more than 5 examples
    assert len(train_corpus.call_counts) > 0
    assert max(train_corpus.call_counts) == 5


@pytest.mark.issue(13804)
def test_init_nlp_default_unbounded_sample():
    """Verify that when init_max_examples is None, the full finite corpus is evaluated."""
    train_corpus = CountingCorpus(total_examples=30)

    @spacy.registry.readers("test_counting_train_corpus_unbounded")
    def create_train_corpus_unbounded(total_examples: int = 30):
        return train_corpus

    config_str = SAMPLE_LIMIT_CONFIG.replace(
        "test_counting_train_corpus", "test_counting_train_corpus_unbounded"
    ).replace("init_max_examples = 5", "init_max_examples = null")
    config = util.load_config_from_str(config_str)
    init_nlp(config)

    # All 30 examples should have been yielded in at least one pass
    assert len(train_corpus.call_counts) > 0
    assert max(train_corpus.call_counts) == 30


@pytest.mark.issue(13804)
def test_init_nlp_initialize_section_override():
    """Verify that init_max_examples configured under [initialize] is respected."""
    train_corpus = CountingCorpus(total_examples=40)

    @spacy.registry.readers("test_counting_train_corpus_init_section")
    def create_train_corpus(total_examples: int = 40):
        return train_corpus

    config_str = SAMPLE_LIMIT_CONFIG.replace(
        "test_counting_train_corpus", "test_counting_train_corpus_init_section"
    ).replace(
        "init_max_examples = 5", "init_max_examples = null"
    ).replace(
        "[initialize]\nvectors = ${paths.vectors}",
        "[initialize]\ninit_max_examples = 7\nvectors = ${paths.vectors}",
    )
    config = util.load_config_from_str(config_str)
    init_nlp(config)

    assert len(train_corpus.call_counts) > 0
    assert max(train_corpus.call_counts) == 7


@pytest.mark.issue(13804)
def test_init_nlp_streamed_corpus_custom_limit():
    """Verify that init_max_examples overrides the 100 default when max_epochs = -1."""
    train_corpus = CountingCorpus(total_examples=50)

    @spacy.registry.readers("test_counting_train_corpus_streamed")
    def create_train_corpus(total_examples: int = 50):
        return train_corpus

    config_str = SAMPLE_LIMIT_CONFIG.replace(
        "test_counting_train_corpus", "test_counting_train_corpus_streamed"
    ).replace(
        "max_epochs = 5", "max_epochs = -1"
    ).replace(
        "init_max_examples = 5", "init_max_examples = 12"
    )
    config = util.load_config_from_str(config_str)
    init_nlp(config)

    assert len(train_corpus.call_counts) > 0
    assert max(train_corpus.call_counts) == 12


@pytest.mark.issue(13804)
def test_init_nlp_negative_limit_rejected():
    """Verify that negative init_max_examples is rejected by schema validation."""
    config_str = SAMPLE_LIMIT_CONFIG.replace(
        "init_max_examples = 5", "init_max_examples = -5"
    )
    config = util.load_config_from_str(config_str)
    with pytest.raises(ConfigValidationError):
        init_nlp(config)

