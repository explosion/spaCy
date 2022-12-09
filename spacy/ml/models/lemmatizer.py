from typing import Optional, List
from thinc.api import glorot_uniform_init, with_array, Softmax_v2, Model
from thinc.api import Relu, Dropout, Sigmoid, concatenate, chain
from thinc.types import Floats2d, Union

from ...util import registry
from ...tokens import Doc


@registry.architectures("spacy.Lemmatizer.v1")
def build_lemmatizer_model(
    tok2vec: Model[List[Doc], List[Floats2d]],
    nO: Optional[int] = None,
    normalize=False,
    lowercasing=True,
) -> Model[List[Doc], Union[List[Floats2d]]]:
    """Build a model for the edit-tree lemmatizer, using a provided token-to-vector component.
    A linear layer with softmax activation is added to predict scores
    given the token vectors (this part corresponds to the *Tagger* architecture).

    Additionally, if *lowercasing==True*, a single sigmoid output is learned for each
    token input: this is used in the context of the lemmatizer to determine when to convert inputs
    to lowercase before processing them with the edit trees. A single normalized linear layer
    is placed between the token-to-vector component and the sigmoid output neuron, as this has
    been found to produce slightly better results than a direct connection. A possible intuition
    explaining this is that it reduces the interference between the two learning goals,
    which are linked but nonetheless distinct.

    tok2vec (Model[List[Doc], List[Floats2d]]): The token-to-vector subnetwork.
    nO (int or None): The number of tags to output in the main model. Inferred from the data if None.
    lowercasing: if *True*, the additional sigmoid appendage is created.
    """
    with Model.define_operators({">>": chain, "|": concatenate}):
        t2v_width = tok2vec.get_dim("nO") if tok2vec.has_dim("nO") else None
        softmax = Softmax_v2(
            nO, t2v_width, init_W=glorot_uniform_init, normalize_outputs=normalize
        )
        model = tok2vec >> with_array(softmax)
        if lowercasing:
            lowercasing_output = Sigmoid(1)
            sigmoid_appendage = Relu(50) >> Dropout(0.2) >> lowercasing_output
            model |= tok2vec >> with_array(sigmoid_appendage)
            model.set_ref("lowercasing_output", lowercasing_output)
        return model
