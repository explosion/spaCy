from typing import Dict, Iterable, Callable
import pytest
from thinc.api import Config
from spacy import Language
from spacy.util import load_model_from_config, registry, dot_to_object
from spacy.training import Example


def test_readers():
    config_string = """
    [training]

    [corpora]
    @readers = "myreader.v1"

    [nlp]
    lang = "en"
    pipeline = ["tok2vec", "textcat"]

    [components]

    [components.tok2vec]
    factory = "tok2vec"

    [components.textcat]
    factory = "textcat"
    """

    @registry.readers.register("myreader.v1")
    def myreader() -> Dict[str, Callable[[Language, str], Iterable[Example]]]:
        annots = {"cats": {"POS": 1.0, "NEG": 0.0}}

        def reader(nlp: Language):
            doc = nlp.make_doc(f"This is an example")
            return [Example.from_dict(doc, annots)]

        return {"train": reader, "dev": reader, "extra": reader, "something": reader}

    config = Config().from_str(config_string)
    nlp, resolved = load_model_from_config(config, auto_fill=True)

    train_corpus = dot_to_object(resolved, resolved["training"]["train_corpus"])
    assert isinstance(train_corpus, Callable)
    optimizer = resolved["training"]["optimizer"]
    # simulate a training loop
    nlp.begin_training(lambda: train_corpus(nlp), sgd=optimizer)
    for example in train_corpus(nlp):
        nlp.update([example], sgd=optimizer)
    dev_corpus = dot_to_object(resolved, resolved["training"]["dev_corpus"])
    scores = nlp.evaluate(list(dev_corpus(nlp)))
    assert scores["cats_score"]
    # ensure the pipeline runs
    doc = nlp("Quick test")
    assert doc.cats
    extra_corpus = resolved["corpora"]["extra"]
    assert isinstance(extra_corpus, Callable)


@pytest.mark.slow
@pytest.mark.parametrize(
    "reader,additional_config",
    [
        ("ml_datasets.imdb_sentiment.v1", {"train_limit": 10, "dev_limit": 2}),
        ("ml_datasets.dbpedia.v1", {"train_limit": 10, "dev_limit": 2}),
        ("ml_datasets.cmu_movies.v1", {"limit": 10, "freq_cutoff": 200, "split": 0.8}),
    ],
)
def test_cat_readers(reader, additional_config):
    nlp_config_string = """
    [training]

    [corpora]
    @readers = "PLACEHOLDER"

    [nlp]
    lang = "en"
    pipeline = ["tok2vec", "textcat"]

    [components]

    [components.tok2vec]
    factory = "tok2vec"

    [components.textcat]
    factory = "textcat"
    """
    config = Config().from_str(nlp_config_string)
    config["corpora"]["@readers"] = reader
    config["corpora"].update(additional_config)
    nlp, resolved = load_model_from_config(config, auto_fill=True)

    train_corpus = dot_to_object(resolved, resolved["training"]["train_corpus"])
    optimizer = resolved["training"]["optimizer"]
    # simulate a training loop
    nlp.begin_training(lambda: train_corpus(nlp), sgd=optimizer)
    for example in train_corpus(nlp):
        assert example.y.cats
        # this shouldn't fail if each training example has at least one positive label
        assert sorted(list(set(example.y.cats.values()))) == [0.0, 1.0]
        nlp.update([example], sgd=optimizer)
    # simulate performance benchmark on dev corpus
    dev_corpus = dot_to_object(resolved, resolved["training"]["dev_corpus"])
    dev_examples = list(dev_corpus(nlp))
    for example in dev_examples:
        # this shouldn't fail if each dev example has at least one positive label
        assert sorted(list(set(example.y.cats.values()))) == [0.0, 1.0]
    scores = nlp.evaluate(dev_examples)
    assert scores["cats_score"]
    # ensure the pipeline runs
    doc = nlp("Quick test")
    assert doc.cats
