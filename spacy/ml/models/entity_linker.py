from typing import Optional
from thinc.api import chain, clone, list2ragged, reduce_mean, residual
from thinc.api import Model, Maxout, Linear

from ...util import registry
from ...kb import KnowledgeBase
from ...vocab import Vocab


@registry.architectures.register("spacy.EntityLinker.v1")
def build_nel_encoder(tok2vec: Model, nO: Optional[int] = None) -> Model:
    with Model.define_operators({">>": chain, "**": clone}):
        token_width = tok2vec.get_dim("nO")
        output_layer = Linear(nO=nO, nI=token_width)
        model = (
            tok2vec
            >> list2ragged()
            >> reduce_mean()
            >> residual(Maxout(nO=token_width, nI=token_width, nP=2, dropout=0.0))
            >> output_layer
        )
        model.set_ref("output_layer", output_layer)
        model.set_ref("tok2vec", tok2vec)
    return model


@registry.assets.register("spacy.KBFromFile.v1")
def load_kb(vocab_path: str, kb_path: str) -> KnowledgeBase:
    vocab = Vocab().from_disk(vocab_path)
    kb = KnowledgeBase(entity_vector_length=1)
    kb.initialize(vocab)
    kb.load_bulk(kb_path)
    return kb


@registry.assets.register("spacy.EmptyKB.v1")
def empty_kb(entity_vector_length: int) -> KnowledgeBase:
    kb = KnowledgeBase(entity_vector_length=entity_vector_length)
    return kb
