from typing import Dict, Iterable, Callable
import pytest
from thinc.api import Config, fix_random_seed
from spacy import Language
from spacy.util import load_model_from_config, registry, resolve_dot_names
from spacy.schemas import ConfigSchemaTraining
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

    @registry.readers("myreader.v1")
    def myreader() -> Dict[str, Callable[[Language], Iterable[Example]]]:
        annots = {"cats": {"POS": 1.0, "NEG": 0.0}}

        def reader(nlp: Language):
            doc = nlp.make_doc(f"This is an example")
            return [Example.from_dict(doc, annots)]

        return {"train": reader, "dev": reader, "extra": reader, "something": reader}

    config = Config().from_str(config_string)
    nlp = load_model_from_config(config, auto_fill=True)
    T = registry.resolve(
        nlp.config.interpolate()["training"], schema=ConfigSchemaTraining
    )
    dot_names = [T["train_corpus"], T["dev_corpus"]]
    train_corpus, dev_corpus = resolve_dot_names(nlp.config, dot_names)
    assert isinstance(train_corpus, Callable)
    optimizer = T["optimizer"]
    # simulate a training loop
    nlp.initialize(lambda: train_corpus(nlp), sgd=optimizer)
    for example in train_corpus(nlp):
        nlp.update([example], sgd=optimizer)
    scores = nlp.evaluate(list(dev_corpus(nlp)))
    assert scores["cats_macro_auc"] == 0.0
    # ensure the pipeline runs
    doc = nlp("Quick test")
    assert doc.cats
    corpora = {"corpora": nlp.config.interpolate()["corpora"]}
    extra_corpus = registry.resolve(corpora)["corpora"]["extra"]
    assert isinstance(extra_corpus, Callable)


@pytest.mark.slow
@pytest.mark.parametrize(
    "reader,additional_config",
    [
        ("ml_datasets.imdb_sentiment.v1", {"train_limit": 10, "dev_limit": 10}),
        ("ml_datasets.dbpedia.v1", {"train_limit": 10, "dev_limit": 10}),
        ("ml_datasets.cmu_movies.v1", {"limit": 10, "freq_cutoff": 200, "split": 0.8}),
    ],
)
def test_cat_readers(reader, additional_config):
    nlp_config_string = """
    [training]
    seed = 0

    [training.score_weights]
    cats_macro_auc = 1.0

    [corpora]
    @readers = "PLACEHOLDER"

    [nlp]
    lang = "en"
    pipeline = ["tok2vec", "textcat_multilabel"]

    [components]

    [components.tok2vec]
    factory = "tok2vec"

    [components.textcat_multilabel]
    factory = "textcat_multilabel"
    """
    config = Config().from_str(nlp_config_string)
    fix_random_seed(config["training"]["seed"])
    config["corpora"]["@readers"] = reader
    config["corpora"].update(additional_config)
    nlp = load_model_from_config(config, auto_fill=True)
    T = registry.resolve(nlp.config["training"], schema=ConfigSchemaTraining)
    dot_names = [T["train_corpus"], T["dev_corpus"]]
    train_corpus, dev_corpus = resolve_dot_names(nlp.config, dot_names)
    optimizer = T["optimizer"]
    # simulate a training loop
    nlp.initialize(lambda: train_corpus(nlp), sgd=optimizer)
    for example in train_corpus(nlp):
        assert example.y.cats
        # this shouldn't fail if each training example has at least one positive label
        assert sorted(list(set(example.y.cats.values()))) == [0.0, 1.0]
        nlp.update([example], sgd=optimizer)
    # simulate performance benchmark on dev corpus
    dev_examples = list(dev_corpus(nlp))
    for example in dev_examples:
        # this shouldn't fail if each dev example has at least one positive label
        assert sorted(list(set(example.y.cats.values()))) == [0.0, 1.0]
    scores = nlp.evaluate(dev_examples)
    assert scores["cats_score"]
    # ensure the pipeline runs
    doc = nlp("Quick test")
    assert doc.cats
