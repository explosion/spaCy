from typing import Callable, Iterable, Iterator
import pytest

from thinc.api import Config
from spacy.language import Language
from spacy.training import Example
from spacy.training.loop import train
from spacy.lang.en import English
from spacy.util import registry, load_model_from_config


@pytest.fixture
def config_str():
    return """
    [nlp]
    lang = "en"
    pipeline = ["sentencizer","assert_sents"]
    disabled = []
    before_creation = null
    after_creation = null
    after_pipeline_creation = null
    batch_size = 1000
    tokenizer = {"@tokenizers":"spacy.Tokenizer.v1"}

    [components]

    [components.assert_sents]
    factory = "assert_sents"

    [components.sentencizer]
    factory = "sentencizer"
    punct_chars = null

    [training]
    dev_corpus = "corpora.dev"
    train_corpus = "corpora.train"
    annotating_components = ["sentencizer"]
    max_steps = 2

    [corpora]

    [corpora.dev]
    @readers = "unannotated_corpus"

    [corpora.train]
    @readers = "unannotated_corpus"
    """


def test_annotates_on_update():
    # The custom component checks for sentence annotation
    @Language.factory("assert_sents", default_config={})
    def assert_sents(nlp, name):
        return AssertSents(name)

    class AssertSents:
        def __init__(self, name, **cfg):
            self.name = name
            pass

        def __call__(self, doc):
            if not doc.has_annotation("SENT_START"):
                raise ValueError("No sents")
            return doc

        def update(self, examples, *, drop=0.0, sgd=None, losses=None):
            for example in examples:
                if not example.predicted.has_annotation("SENT_START"):
                    raise ValueError("No sents")
            return {}

    nlp = English()
    nlp.add_pipe("sentencizer")
    nlp.add_pipe("assert_sents")

    # When the pipeline runs, annotations are set
    nlp("This is a sentence.")

    examples = []
    for text in ["a a", "b b", "c c"]:
        examples.append(Example(nlp.make_doc(text), nlp(text)))

    for example in examples:
        assert not example.predicted.has_annotation("SENT_START")

    # If updating without setting annotations, assert_sents will raise an error
    with pytest.raises(ValueError):
        nlp.update(examples)

    # Updating while setting annotations for the sentencizer succeeds
    nlp.update(examples, annotates=["sentencizer"])


def test_annotating_components_from_config(config_str):
    @registry.readers("unannotated_corpus")
    def create_unannotated_corpus() -> Callable[[Language], Iterable[Example]]:
        return UnannotatedCorpus()

    class UnannotatedCorpus:
        def __call__(self, nlp: Language) -> Iterator[Example]:
            for text in ["a a", "b b", "c c"]:
                doc = nlp.make_doc(text)
                yield Example(doc, doc)

    orig_config = Config().from_str(config_str)
    nlp = load_model_from_config(orig_config, auto_fill=True, validate=True)
    assert nlp.config["training"]["annotating_components"] == ["sentencizer"]
    train(nlp)

    nlp.config["training"]["annotating_components"] = []
    with pytest.raises(ValueError):
        train(nlp)
