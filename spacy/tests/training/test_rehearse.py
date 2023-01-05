import pytest
import spacy

from thinc.api import Config

from typing import List
from spacy.training import Example


TRAIN_DATA = [
    (
        "Who is Kofi Annan?",
        {
            "entities": [(7, 18, "PERSON")],
            "tags": ["PRON", "AUX", "PROPN", "PRON", "PUNCT"],
            "heads": [1, 1, 3, 1, 1],
            "deps": ["attr", "ROOT", "compound", "nsubj", "punct"],
            "morphs": [
                "",
                "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin",
                "Number=Sing",
                "Number=Sing",
                "PunctType=Peri",
            ],
            "cats": {"question": 1.0},
        },
    ),
    (
        "Who is Steve Jobs?",
        {
            "entities": [(7, 17, "PERSON")],
            "tags": ["PRON", "AUX", "PROPN", "PRON", "PUNCT"],
            "heads": [1, 1, 3, 1, 1],
            "deps": ["attr", "ROOT", "compound", "nsubj", "punct"],
            "morphs": [
                "",
                "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin",
                "Number=Sing",
                "Number=Sing",
                "PunctType=Peri",
            ],
            "cats": {"question": 1.0},
        },
    ),
    (
        "Bob is a nice person.",
        {
            "entities": [(0, 3, "PERSON")],
            "tags": ["PROPN", "AUX", "DET", "ADJ", "NOUN", "PUNCT"],
            "heads": [1, 1, 4, 4, 1, 1],
            "deps": ["nsubj", "ROOT", "det", "amod", "attr", "punct"],
            "morphs": [
                "Number=Sing",
                "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin",
                "Definite=Ind|PronType=Art",
                "Degree=Pos",
                "Number=Sing",
                "PunctType=Peri",
            ],
            "cats": {"statement": 1.0},
        },
    ),
    (
        "Hi Anil, how are you?",
        {
            "entities": [(3, 7, "PERSON")],
            "tags": ["INTJ", "PROPN", "PUNCT", "ADV", "AUX", "PRON", "PUNCT"],
            "deps": ["intj", "npadvmod", "punct", "advmod", "ROOT", "nsubj", "punct"],
            "heads": [4, 0, 4, 4, 4, 4, 4],
            "morphs": [
                "",
                "Number=Sing",
                "PunctType=Comm",
                "",
                "Mood=Ind|Tense=Pres|VerbForm=Fin",
                "Case=Nom|Person=2|PronType=Prs",
                "PunctType=Peri",
            ],
            "cats": {"greeting": 1.0, "question": 1.0},
        },
    ),
    (
        "I like London and Berlin.",
        {
            "entities": [(7, 13, "LOC"), (18, 24, "LOC")],
            "tags": ["PROPN", "VERB", "PROPN", "CCONJ", "PROPN", "PUNCT"],
            "deps": ["nsubj", "ROOT", "dobj", "cc", "conj", "punct"],
            "heads": [1, 1, 1, 2, 2, 1],
            "morphs": [
                "Case=Nom|Number=Sing|Person=1|PronType=Prs",
                "Tense=Pres|VerbForm=Fin",
                "Number=Sing",
                "ConjType=Cmp",
                "Number=Sing",
                "PunctType=Peri",
            ],
            "cats": {"statement": 1.0},
        },
    ),
]

REHEARSE_DATA = [
    (
        "Hi Anil",
        {
            "entities": [(3, 7, "PERSON")],
            "tags": ["INTJ", "PROPN"],
            "deps": ["ROOT", "npadvmod"],
            "heads": [0, 0],
            "morphs": ["", "Number=Sing"],
            "cats": {"greeting": 1.0},
        },
    ),
    (
        "Hi Ravish, how you doing?",
        {
            "entities": [(3, 9, "PERSON")],
            "tags": ["INTJ", "PROPN", "PUNCT", "ADV", "AUX", "PRON", "PUNCT"],
            "deps": ["intj", "ROOT", "punct", "advmod", "nsubj", "advcl", "punct"],
            "heads": [1, 1, 1, 5, 5, 1, 1],
            "morphs": [
                "",
                "VerbForm=Inf",
                "PunctType=Comm",
                "",
                "Case=Nom|Person=2|PronType=Prs",
                "Aspect=Prog|Tense=Pres|VerbForm=Part",
                "PunctType=Peri",
            ],
            "cats": {"greeting": 1.0, "question": 1.0},
        },
    ),
    # UTENSIL new label
    (
        "Natasha bought new forks.",
        {
            "entities": [(0, 7, "PERSON"), (19, 24, "UTENSIL")],
            "tags": ["PROPN", "VERB", "ADJ", "NOUN", "PUNCT"],
            "deps": ["nsubj", "ROOT", "amod", "dobj", "punct"],
            "heads": [1, 1, 3, 1, 1],
            "morphs": [
                "Number=Sing",
                "Tense=Past|VerbForm=Fin",
                "Degree=Pos",
                "Number=Plur",
                "PunctType=Peri",
            ],
            "cats": {"statement": 1.0},
        },
    ),
]

TEXTCAT_MULTILABEL_LISTENER_CONFIG = """
[nlp]
lang = "en"
pipeline = ["tok2vec","textcat_multilabel"]
disabled = []
before_creation = null
after_creation = null
after_pipeline_creation = null
batch_size = 1000
tokenizer = {"@tokenizers":"spacy.Tokenizer.v1"}

[components]

[components.textcat_multilabel]
factory = "textcat_multilabel"
threshold = 0.5

[components.textcat_multilabel.model]
@architectures = "spacy.TextCatEnsemble.v2"
nO = null

[components.textcat_multilabel.model.linear_model]
@architectures = "spacy.TextCatBOW.v2"
exclusive_classes = false
ngram_size = 1
no_output_layer = false 

[components.textcat_multilabel.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = 64
upstream = "*"

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v2"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = 64
attrs = ["ORTH", "SHAPE"]
rows = [5000, 2500]
include_static_vectors = true 

[components.tok2vec.model.encode]
@architectures = "spacy.MishWindowEncoder.v2"
width = 64
depth = 4
window_size = 1
"""

NER_LISTENER_CONFIG = """
[nlp]
lang = "en"
pipeline = ["tok2vec","ner"]
batch_size = 1000

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v2"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = ${components.tok2vec.model.encode.width}
attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
rows = [5000, 1000, 2500, 2500]
include_static_vectors = false

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = 96
depth = 4
window_size = 1
maxout_pieces = 3

[components.ner]
factory = "ner"

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "ner"
extra_state_tokens = false
hidden_width = 64
maxout_pieces = 2
use_upper = true
nO = null

[components.ner.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.encode.width}
"""


def _add_ner_label(ner, data):
    for _, annotations in data:
        for ent in annotations["entities"]:
            ner.add_label(ent[2])


def _add_tagger_label(tagger, data):
    for _, annotations in data:
        for tag in annotations["tags"]:
            tagger.add_label(tag)


def _add_parser_label(parser, data):
    for _, annotations in data:
        for dep in annotations["deps"]:
            parser.add_label(dep)


def _add_textcat_label(textcat, data):
    for _, annotations in data:
        for cat in annotations["cats"]:
            textcat.add_label(cat)


def _optimize(nlp, component: str, data: List, rehearse: bool):
    """Run either train or rehearse."""
    pipe = nlp.get_pipe(component)
    if component == "ner":
        _add_ner_label(pipe, data)
    elif component == "tagger":
        _add_tagger_label(pipe, data)
    elif component == "parser":
        _add_parser_label(pipe, data)
    elif component == "textcat_multilabel":
        _add_textcat_label(pipe, data)
    else:
        raise NotImplementedError

    if rehearse:
        optimizer = nlp.resume_training()
    else:
        optimizer = nlp.initialize()

    for _ in range(5):
        for text, annotation in data:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotation)
            if rehearse:
                nlp.rehearse([example], sgd=optimizer)
            else:
                nlp.update([example], sgd=optimizer)
    return nlp


@pytest.mark.parametrize("component", ["ner", "tagger", "parser", "textcat_multilabel"])
def test_rehearse(component):
    nlp = spacy.blank("en")
    nlp.add_pipe(component)
    nlp = _optimize(nlp, component, TRAIN_DATA, False)
    _optimize(nlp, component, REHEARSE_DATA, True)


@pytest.mark.issue(12044)
def test_rehearse_textcat_multilabel_listener():
    """Test nlp.rehearse on a textcat_multilabel pipeline with a tok2vec listener"""
    config = Config().from_str(TEXTCAT_MULTILABEL_LISTENER_CONFIG)
    nlp = spacy.blank("en", config=config)
    nlp = _optimize(nlp, "textcat_multilabel", TRAIN_DATA, False)
    _optimize(nlp, "textcat_multilabel", REHEARSE_DATA, True)


@pytest.mark.issue(12044)
def test_rehearse_ner_listener():
    """Test nlp.rehearse on a ner pipeline with a tok2vec listener"""
    config = Config().from_str(NER_LISTENER_CONFIG)
    nlp = spacy.blank("en", config=config)
    nlp = _optimize(nlp, "ner", TRAIN_DATA, False)
    _optimize(nlp, "ner", REHEARSE_DATA, True)
