import pytest
import spacy

from spacy.training import loggers


@pytest.fixture()
def nlp():
    nlp = spacy.blank("en")
    nlp.add_pipe("ner")
    return nlp


@pytest.fixture()
def info():
    return {
        "losses": {"ner": 100},
        "other_scores": {"ENTS_F": 0.85, "ENTS_P": 0.90, "ENTS_R": 0.80},
        "epoch": 100,
        "step": 125,
        "score": 85,
    }


def test_console_logger(nlp, info):
    console_logger = loggers.console_logger(
        progress_bar=True, console_output=True, output_file=None
    )
    log_step, finalize = console_logger(nlp)
    log_step(info)
