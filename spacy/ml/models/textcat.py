from spacy.attrs import ORTH
from spacy.ml.extract_ngrams import extract_ngrams

from thinc.model import Model
from thinc.layers import chain, reduce_mean
from thinc.layers import Linear, list2ragged, Logistic, SparseLinear, Softmax


def build_text_classifier(
    architecture,
    tok2vec,
    nr_class=1,
    exclusive_classes=None,
    ngram_size=1,
    no_output_layer=False,
):
    if nr_class == 1:
        exclusive_classes = False
    if exclusive_classes is None:
        raise ValueError(
            "TextCategorizer Model must specify 'exclusive_classes'. "
            "This setting determines whether the model will output "
            "scores that sum to 1 for each example. If only one class "
            "is true for each example, you should set exclusive_classes=True. "
            "For 'multi_label' classification, set exclusive_classes=False."
        )
    if architecture == "bow":
        return build_bow_text_classifier(
            nr_class, exclusive_classes, ngram_size, no_output_layer
        )
    elif architecture == "cnn":
        return build_simple_cnn_text_classifier(tok2vec, nr_class, exclusive_classes)
    else:
        raise ValueError("Unexpected textcat arch")


def build_simple_cnn_text_classifier(tok2vec, nr_class, exclusive_classes):
    """
    Build a simple CNN text classifier, given a token-to-vector model as inputs.
    If exclusive_classes=True, a softmax non-linearity is applied, so that the
    outputs sum to 1. If exclusive_classes=False, a logistic non-linearity
    is applied instead, so that outputs are in the range [0, 1].
    """
    with Model.define_operators({">>": chain}):
        if exclusive_classes:
            output_layer = Softmax(nO=nr_class, nI=tok2vec.get_dim("nO"))
        else:
            # TODO: experiment with init_w=zero_init
            output_layer = Linear(nO=nr_class, nI=tok2vec.get_dim("nO")) >> Logistic()
        model = tok2vec >> list2ragged() >> reduce_mean() >> output_layer
    model.set_ref("tok2vec", tok2vec)
    model.set_dim("nO", nr_class)
    return model


def build_bow_text_classifier(nr_class, exclusive_classes, ngram_size, no_output_layer):
    with Model.define_operators({">>": chain}):
        model = extract_ngrams(ngram_size, attr=ORTH) >> SparseLinear(nr_class)
        model.to_cpu()
        if not no_output_layer:
            output_layer = (
                Softmax(nO=nr_class) if exclusive_classes else Logistic(nO=nr_class)
            )
            output_layer.to_cpu()
            model = model >> output_layer
    model.set_dim("nO", nr_class)
    return model
