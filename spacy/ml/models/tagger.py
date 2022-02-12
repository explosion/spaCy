from typing import Optional, List
from thinc.api import zero_init, with_array, Softmax_v2, chain, Model
from thinc.types import Floats2d

from ...util import registry
from ...tokens import Doc


@registry.architectures("spacy.Tagger.v2")
def build_tagger_model(
    tok2vec: Model[List[Doc], List[Floats2d]], nO: Optional[int] = None, normalize=False
) -> Model[List[Doc], List[Floats2d]]:
    """Build a tagger model, using a provided token-to-vector component. The tagger
    model simply adds a linear layer with softmax activation to predict scores
    given the token vectors.

    tok2vec (Model[List[Doc], List[Floats2d]]): The token-to-vector subnetwork.
    nO (int or None): The number of tags to output. Inferred from the data if None.
    """
    # TODO: glorot_uniform_init seems to work a bit better than zero_init here?!
    t2v_width = tok2vec.get_dim("nO") if tok2vec.has_dim("nO") else None
    output_layer = Softmax_v2(
        nO, t2v_width, init_W=zero_init, normalize_outputs=normalize
    )
    softmax = with_array(output_layer)  # type: ignore
    model = chain(tok2vec, softmax)
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("softmax", output_layer)
    model.set_ref("output_layer", output_layer)
    return model
