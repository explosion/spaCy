from typing import List, Dict, Callable, Tuple, Optional, Iterable, Any, cast
from thinc.api import Config, Model, get_current_ops, set_dropout_rate, Ops
from thinc.api import Optimizer, Softmax_v2
from thinc.types import Ragged, Ints2d, Floats2d, Ints1d

import numpy

from ..compat import Protocol, runtime_checkable
from ..scorer import Scorer
from ..language import Language
from .trainable_pipe import TrainablePipe
from ..tokens import Doc, SpanGroup, Span
from ..vocab import Vocab
from ..training import Example, validate_examples
from ..errors import Errors
from ..util import registry


@registry.layers("spacy.Softmax.v1")
def build_linear_logistic(nO=None, nI=None) -> Model[Floats2d, Floats2d]:
    """An output layer for multi-label classification. It uses a linear layer
    followed by a logistic activation.
    """
    return Softmax_v2(nI=nI, nO=nO)


spancat_exclusive_default_config = """
[model]
@architectures = "spacy.SpanCategorizerExclusive.v1"
scorer = {"@layers": "spacy.Softmax.v1"}

[model.reducer]
@layers = spacy.mean_max_reducer.v1
hidden_size = 128

[model.tok2vec]
@architectures = "spacy.Tok2Vec.v1"
[model.tok2vec.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = 96
rows = [5000, 2000, 1000, 1000]
attrs = ["ORTH", "PREFIX", "SUFFIX", "SHAPE"]
include_static_vectors = false

[model.tok2vec.encode]
@architectures = "spacy.MaxoutWindowEncoder.v1"
width = ${model.tok2vec.embed.width}
window_size = 1
maxout_pieces = 3
depth = 4
"""

DEFAULT_SPANCAT_MODEL = Config().from_str(spancat_exclusive_default_config)["model"]


@runtime_checkable
class Suggester(Protocol):
    def __call__(self, docs: Iterable[Doc], *, ops: Optional[Ops] = None) -> Ragged:
        ...


@Language.factory(
    "spancat_exclusive",
    assigns=["doc.spans"],
    default_config={
        "spans_key": "sc",
        "model": DEFAULT_SPANCAT_MODEL,
        "suggester": {"@misc": "spacy.ngram_suggester.v1", "sizes": [1, 2, 3]},
        "scorer": {"@scorers": "spacy.spancat_scorer.v1"},
    },
)
def make_spancat(
    nlp: Language,
    name: str,
    suggester: Suggester,
    model: Model[Tuple[List[Doc], Ragged], Floats2d],
):
    pass
