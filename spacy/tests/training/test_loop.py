from typing import Callable, Iterable, Iterator

import pytest
from thinc.api import Config, fix_random_seed

from spacy import Language
from spacy.training import Example
from spacy.training.initialize import init_nlp_student
from spacy.training.loop import distill, train
from spacy.util import load_model_from_config, registry


@pytest.fixture
def config_str():
    return """
    [nlp]
    lang = "en"
    pipeline = ["senter"]
    disabled = []
    before_creation = null
    after_creation = null
    after_pipeline_creation = null
    batch_size = 1000
    tokenizer = {"@tokenizers":"spacy.Tokenizer.v1"}

    [components]

    [components.senter]
    factory = "senter"

    [training]
    dev_corpus = "corpora.dev"
    train_corpus = "corpora.train"
    max_steps = 50
    seed = 1
    gpu_allocator = null

    [distillation]
    corpus = "corpora.train"
    dropout = 0.1
    max_epochs = 0
    max_steps = 50
    student_to_teacher = {}

    [distillation.batcher]
    @batchers = "spacy.batch_by_words.v1"
    size = 3000
    discard_oversize = false
    tolerance = 0.2

    [distillation.optimizer]
    @optimizers = "Adam.v1"
    beta1 = 0.9
    beta2 = 0.999
    L2_is_weight_decay = true
    L2 = 0.01
    grad_clip = 1.0
    use_averages = true
    eps = 1e-8
    learn_rate = 1e-4

    [corpora]

    [corpora.dev]
    @readers = "sentence_corpus"

    [corpora.train]
    @readers = "sentence_corpus"
    """


SENT_STARTS = [0] * 14
SENT_STARTS[0] = 1
SENT_STARTS[5] = 1
SENT_STARTS[9] = 1

TRAIN_DATA = [
    (
        "I like green eggs. Eat blue ham. I like purple eggs.",
        {"sent_starts": SENT_STARTS},
    ),
    (
        "She likes purple eggs. They hate ham. You like yellow eggs.",
        {"sent_starts": SENT_STARTS},
    ),
]


@pytest.mark.slow
def test_distill_loop(config_str):
    fix_random_seed(0)

    @registry.readers("sentence_corpus")
    def create_sentence_corpus() -> Callable[[Language], Iterable[Example]]:
        return SentenceCorpus()

    class SentenceCorpus:
        def __call__(self, nlp: Language) -> Iterator[Example]:
            for t in TRAIN_DATA:
                yield Example.from_dict(nlp.make_doc(t[0]), t[1])

    orig_config = Config().from_str(config_str)
    teacher = load_model_from_config(orig_config, auto_fill=True, validate=True)
    teacher.initialize()
    train(teacher)

    orig_config = Config().from_str(config_str)
    student = init_nlp_student(orig_config, teacher)
    student.initialize()
    distill(teacher, student)

    doc = student(TRAIN_DATA[0][0])
    assert doc.sents[0].text == "I like green eggs."
    assert doc.sents[1].text == "Eat blue ham."
    assert doc.sents[2].text == "I like purple eggs."
