from typing import Optional, Callable, Iterable
from thinc.api import chain, clone, list2ragged, reduce_mean, residual
from thinc.api import Model, Maxout, Linear

from ...util import registry
from ...kb import KnowledgeBase, Candidate, get_candidates
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


@registry.misc.register("spacy.KBFromFile.v1")
def load_kb(kb_path: str) -> Callable[[Vocab], KnowledgeBase]:
    def kb_from_file(vocab):
        kb = KnowledgeBase(vocab, entity_vector_length=1)
        kb.from_disk(kb_path)
        return kb

    return kb_from_file


@registry.misc.register("spacy.EmptyKB.v1")
def empty_kb(entity_vector_length: int) -> Callable[[Vocab], KnowledgeBase]:
    def empty_kb_factory(vocab):
        return KnowledgeBase(vocab=vocab, entity_vector_length=entity_vector_length)

    return empty_kb_factory


@registry.misc.register("spacy.CandidateGenerator.v1")
def create_candidates() -> Callable[[KnowledgeBase, "Span"], Iterable[Candidate]]:
    return get_candidates
