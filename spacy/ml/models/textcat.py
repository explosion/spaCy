from pathlib import Path

from spacy import util
from spacy.attrs import ORTH
from spacy.util import registry
from spacy.ml.extract_ngrams import extract_ngrams

from thinc.model import Model
from thinc.layers import chain, reduce_mean
from thinc.layers import Linear, list2ragged, Logistic, SparseLinear, Softmax


def default_textcat_config():
    loc = Path(__file__).parent / "defaults" / "textcat_defaults.cfg"
    return util.load_from_config(loc, create_objects=False)


@registry.architectures.register("spacy.TextCatCNN.v1")
def build_simple_cnn_text_classifier(tok2vec, exclusive_classes):
    """
    Build a simple CNN text classifier, given a token-to-vector model as inputs.
    If exclusive_classes=True, a softmax non-linearity is applied, so that the
    outputs sum to 1. If exclusive_classes=False, a logistic non-linearity
    is applied instead, so that outputs are in the range [0, 1].
    """
    with Model.define_operators({">>": chain}):
        if exclusive_classes:
            output_layer = Softmax(nI=tok2vec.get_dim("nO"))
        else:
            # TODO: experiment with init_w=zero_init
            output_layer = Linear(nI=tok2vec.get_dim("nO")) >> Logistic()
        model = tok2vec >> list2ragged() >> reduce_mean() >> output_layer
    model.set_ref("tok2vec", tok2vec)
    return model


@registry.architectures.register("spacy.TextCatBOW.v1")
def build_bow_text_classifier(exclusive_classes, ngram_size, no_output_layer):
    # Note: original defaults were ngram_size=1 and no_output_layer=False
    with Model.define_operators({">>": chain}):
        model = extract_ngrams(ngram_size, attr=ORTH) >> SparseLinear()
        model.to_cpu()
        if not no_output_layer:
            output_layer = Softmax() if exclusive_classes else Logistic()
            output_layer.to_cpu()
            model = model >> output_layer
    return model
