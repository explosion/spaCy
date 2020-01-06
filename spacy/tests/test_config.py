import pytest
from spacy.util import registry
from pydantic import StrictFloat, StrictInt
import srsly


def is_json_equal(a, b):
    return srsly.json_dumps(a, sort_keys=True) == srsly.json_dumps(b, sort_keys=True)


@registry.optimizers.register("test_optimizer")
def optimizer(
    learn_rate: StrictFloat = 0.001,
    beta1: StrictFloat = 0.9,
    beta2: StrictFloat = 0.999,
):
    pass


@registry.schedules.register("test_schedule")
def schedule(start: StrictInt = 100, end: StrictInt = 1000):
    pass


@registry.architectures.register("test_arch")
def architecture(
    nr_feature_tokens: StrictInt = 3,
    hidden_width: StrictInt = 64,
    maxout_pieces: StrictInt = 3,
):
    pass


# I'm not sure what this test was intended to do? 
@pytest.mark.xfail
def test_config_validation_basic():
    config = {
        "optimizer": {
            "@optimizers": "test_optimizer",
            "learn_rate": 0.001,
            "beta1": 0.9,
            "beta2": 0.999,
        },
        "training": {
            "batch_size": {"@schedules": "test_schedule", "start": 100, "end": 1000},
            "patience": 10,
            "eval_frequency": 100,
            "dropout": 0.2,
            "init_tok2vec": None,
            "vectors": None,
            "max_epochs": 100,
            "orth_variant_level": 0.0,
            "gold_preproc": False,
            "max_length": 0,
            "use_gpu": 0,
            "scores": ["ents_p", "ents_r", "ents_f"],
            "score_weights": {"ents_f": 1.0},
            "limit": 0,
        },
        "nlp": {
            "lang": "en",
            "vectors": None,
            "pipeline": {
                "ner": {
                    "factory": "ner",
                    "model": {
                        "@architectures": "test_arch",
                        "nr_feature_tokens": 3,
                        "hidden_width": 64,
                        "maxout_pieces": 3,
                        "tok2vec": None,
                    },
                }
            },
        },
    }
    minimal_config = {"training": {"batch_size": 5}, "nlp": {"lang": "en"}}
    result = parse_config(config)
    assert is_json_equal(result, config)
    parse_config(minimal_config)
