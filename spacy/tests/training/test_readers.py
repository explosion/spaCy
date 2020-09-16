import pytest
from thinc.api import Config
from spacy.util import load_model_from_config


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
    
    [training.corpus]
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
    config["training"]["corpus"]["@readers"] = reader
    config["training"]["corpus"].update(additional_config)
    nlp, resolved = load_model_from_config(config, auto_fill=True)

    train_corpus = resolved["training"]["corpus"]["train"]
    optimizer = resolved["training"]["optimizer"]
    # simulate a training loop
    nlp.begin_training(lambda: train_corpus(nlp), sgd=optimizer)
    for example in train_corpus(nlp):
        assert example.y.cats
        # this shouldn't fail if each training example has at least one positive label
        assert sorted(list(set(example.y.cats.values()))) == [0.0, 1.0]
        nlp.update([example], sgd=optimizer)
    # simulate performance benchmark on dev corpus
    dev_corpus = resolved["training"]["corpus"]["dev"]
    dev_examples = list(dev_corpus(nlp))
    for example in dev_examples:
        # this shouldn't fail if each dev example has at least one positive label
        assert sorted(list(set(example.y.cats.values()))) == [0.0, 1.0]
    scores = nlp.evaluate(dev_examples)
    assert scores["cats_score"]
    # ensure the pipeline runs
    doc = nlp("Quick test")
    assert doc.cats
