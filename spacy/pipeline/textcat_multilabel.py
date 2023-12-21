from itertools import islice
from typing import Any, Callable, Dict, Iterable, List, Optional

from thinc.api import Config, Model
from thinc.types import Floats2d

from ..errors import Errors
from ..language import Language
from ..scorer import Scorer
from ..tokens import Doc
from ..training import Example, validate_get_examples
from ..util import registry
from ..vocab import Vocab
from .textcat import TextCategorizer

multi_label_default_config = """
[model]
@architectures = "spacy.TextCatEnsemble.v2"

[model.tok2vec]
@architectures = "spacy.Tok2Vec.v2"

[model.tok2vec.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = 64
rows = [2000, 2000, 500, 1000, 500]
attrs = ["NORM", "LOWER", "PREFIX", "SUFFIX", "SHAPE"]
include_static_vectors = false

[model.tok2vec.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = ${model.tok2vec.embed.width}
window_size = 1
maxout_pieces = 3
depth = 2

[model.linear_model]
@architectures = "spacy.TextCatBOW.v3"
exclusive_classes = false
length = 262144
ngram_size = 1
no_output_layer = false
"""
DEFAULT_MULTI_TEXTCAT_MODEL = Config().from_str(multi_label_default_config)["model"]

multi_label_bow_config = """
[model]
@architectures = "spacy.TextCatBOW.v3"
exclusive_classes = false
ngram_size = 1
no_output_layer = false
"""

multi_label_cnn_config = """
[model]
@architectures = "spacy.TextCatReduce.v1"
exclusive_classes = false
use_reduce_first = false
use_reduce_last = false
use_reduce_max = false
use_reduce_mean = true

[model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v2"
pretrained_vectors = null
width = 96
depth = 4
embed_size = 2000
window_size = 1
maxout_pieces = 3
subword_features = true
"""


@Language.factory(
    "textcat_multilabel",
    assigns=["doc.cats"],
    default_config={
        "threshold": 0.5,
        "model": DEFAULT_MULTI_TEXTCAT_MODEL,
        "scorer": {"@scorers": "spacy.textcat_multilabel_scorer.v2"},
    },
    default_score_weights={
        "cats_score": 1.0,
        "cats_score_desc": None,
        "cats_micro_p": None,
        "cats_micro_r": None,
        "cats_micro_f": None,
        "cats_macro_p": None,
        "cats_macro_r": None,
        "cats_macro_f": None,
        "cats_macro_auc": None,
        "cats_f_per_type": None,
    },
)
def make_multilabel_textcat(
    nlp: Language,
    name: str,
    model: Model[List[Doc], List[Floats2d]],
    threshold: float,
    scorer: Optional[Callable],
) -> "MultiLabel_TextCategorizer":
    """Create a MultiLabel_TextCategorizer component. The text categorizer predicts categories
    over a whole document. It can learn one or more labels, and the labels are considered
    to be non-mutually exclusive, which means that there can be zero or more labels
    per doc).

    model (Model[List[Doc], List[Floats2d]]): A model instance that predicts
        scores for each category.
    threshold (float): Cutoff to consider a prediction "positive".
    scorer (Optional[Callable]): The scoring method.
    """
    return MultiLabel_TextCategorizer(
        nlp.vocab, model, name, threshold=threshold, scorer=scorer
    )


def textcat_multilabel_score(examples: Iterable[Example], **kwargs) -> Dict[str, Any]:
    return Scorer.score_cats(
        examples,
        "cats",
        multi_label=True,
        **kwargs,
    )


@registry.scorers("spacy.textcat_multilabel_scorer.v2")
def make_textcat_multilabel_scorer():
    return textcat_multilabel_score


class MultiLabel_TextCategorizer(TextCategorizer):
    """Pipeline component for multi-label text classification.

    DOCS: https://spacy.io/api/textcategorizer
    """

    def __init__(
        self,
        vocab: Vocab,
        model: Model,
        name: str = "textcat_multilabel",
        *,
        threshold: float,
        scorer: Optional[Callable] = textcat_multilabel_score,
    ) -> None:
        """Initialize a text categorizer for multi-label classification.

        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name, used to add entries to the
            losses during training.
        threshold (float): Cutoff to consider a prediction "positive".
        scorer (Optional[Callable]): The scoring method.

        DOCS: https://spacy.io/api/textcategorizer#init
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self._rehearsal_model = None
        cfg = {"labels": [], "threshold": threshold}
        self.cfg = dict(cfg)
        self.scorer = scorer

    @property
    def support_missing_values(self):
        return True

    def initialize(  # type: ignore[override]
        self,
        get_examples: Callable[[], Iterable[Example]],
        *,
        nlp: Optional[Language] = None,
        labels: Optional[Iterable[str]] = None,
    ):
        """Initialize the pipe for training, using a representative set
        of data examples.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        nlp (Language): The current nlp object the component is part of.
        labels: The labels to add to the component, typically generated by the
            `init labels` command. If no labels are provided, the get_examples
            callback is used to extract the labels from the data.

        DOCS: https://spacy.io/api/textcategorizer#initialize
        """
        validate_get_examples(get_examples, "MultiLabel_TextCategorizer.initialize")
        if labels is None:
            for example in get_examples():
                for cat in example.y.cats:
                    self.add_label(cat)
        else:
            for label in labels:
                self.add_label(label)
        subbatch = list(islice(get_examples(), 10))
        self._validate_categories(subbatch)

        doc_sample = [eg.reference for eg in subbatch]
        label_sample, _ = self._examples_to_truth(subbatch)
        self._require_labels()
        assert len(doc_sample) > 0, Errors.E923.format(name=self.name)
        assert len(label_sample) > 0, Errors.E923.format(name=self.name)
        self.model.initialize(X=doc_sample, Y=label_sample)

    def _validate_categories(self, examples: Iterable[Example]):
        """This component allows any type of single- or multi-label annotations.
        This method overwrites the more strict one from 'textcat'."""
        # check that annotation values are valid
        for ex in examples:
            for val in ex.reference.cats.values():
                if not (val == 1.0 or val == 0.0):
                    raise ValueError(Errors.E851.format(val=val))
