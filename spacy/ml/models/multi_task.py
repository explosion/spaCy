from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Iterable, List, Optional, Tuple, cast

import numpy
from thinc.api import (
    CosineDistance,
    L2Distance,
    LayerNorm,
    Linear,
    Maxout,
    Model,
    MultiSoftmax,
    Softmax,
    chain,
    list2array,
    to_categorical,
    zero_init,
)
from thinc.loss import Loss
from thinc.types import Floats2d, Ints1d

from ...attrs import ID, ORTH
from ...errors import Errors
from ...util import OOV_RANK, registry
from ...vectors import Mode as VectorsMode

if TYPE_CHECKING:
    # This lets us add type hints for mypy etc. without causing circular imports
    from ...tokens.doc import Doc  # noqa: F401
    from ...vocab import Vocab  # noqa: F401


def create_pretrain_vectors(
    maxout_pieces: int, hidden_size: int, loss: str
) -> Callable[["Vocab", Model], Model]:
    def create_vectors_objective(vocab: "Vocab", tok2vec: Model) -> Model:
        if vocab.vectors.shape[1] == 0:
            raise ValueError(Errors.E875)
        model = build_cloze_multi_task_model(
            vocab, tok2vec, hidden_size=hidden_size, maxout_pieces=maxout_pieces
        )
        model.attrs["loss"] = create_vectors_loss()
        return model

    def create_vectors_loss() -> Callable:
        distance: Loss
        if loss == "cosine":
            distance = CosineDistance(normalize=True, ignore_zeros=True)
            return partial(get_vectors_loss, distance=distance)
        elif loss == "L2":
            distance = L2Distance(normalize=True)
            return partial(get_vectors_loss, distance=distance)
        else:
            raise ValueError(Errors.E906.format(found=loss, supported="'cosine', 'L2'"))

    return create_vectors_objective


def create_pretrain_characters(
    maxout_pieces: int, hidden_size: int, n_characters: int
) -> Callable[["Vocab", Model], Model]:
    def create_characters_objective(vocab: "Vocab", tok2vec: Model) -> Model:
        model = build_cloze_characters_multi_task_model(
            vocab,
            tok2vec,
            hidden_size=hidden_size,
            maxout_pieces=maxout_pieces,
            nr_char=n_characters,
        )
        model.attrs["loss"] = partial(get_characters_loss, nr_char=n_characters)
        return model

    return create_characters_objective


def get_vectors_loss(ops, docs, prediction, distance):
    """Compute a loss based on a distance between the documents' vectors and
    the prediction.
    """
    vocab = docs[0].vocab
    if vocab.vectors.mode == VectorsMode.default:
        # The simplest way to implement this would be to vstack the
        # token.vector values, but that's a bit inefficient, especially on GPU.
        # Instead we fetch the index into the vectors table for each of our
        # tokens, and look them up all at once. This prevents data copying.
        ids = ops.flatten([doc.to_array(ID).ravel() for doc in docs])
        target = docs[0].vocab.vectors.data[ids]
        target[ids == OOV_RANK] = 0
        d_target, loss = distance(prediction, target)
    elif vocab.vectors.mode == VectorsMode.floret:
        keys = ops.flatten([cast(Ints1d, doc.to_array(ORTH)) for doc in docs])
        target = vocab.vectors.get_batch(keys)
        target = ops.as_contig(target)
        d_target, loss = distance(prediction, target)
    else:
        raise ValueError(Errors.E850.format(mode=vocab.vectors.mode))
    return loss, d_target


def get_characters_loss(ops, docs, prediction, nr_char):
    """Compute a loss based on a number of characters predicted from the docs."""
    target_ids = numpy.vstack([doc.to_utf8_array(nr_char=nr_char) for doc in docs])
    target_ids = target_ids.reshape((-1,))
    target = ops.asarray(to_categorical(target_ids, n_classes=256), dtype="f")
    target = target.reshape((-1, 256 * nr_char))
    diff = prediction - target
    loss = (diff**2).sum()
    d_target = diff / float(prediction.shape[0])
    return loss, d_target


def build_multi_task_model(
    tok2vec: Model,
    maxout_pieces: int,
    token_vector_width: int,
    nO: Optional[int] = None,
) -> Model:
    softmax = Softmax(nO=nO, nI=token_vector_width * 2)
    model = chain(
        tok2vec,
        Maxout(
            nO=token_vector_width * 2,
            nI=token_vector_width,
            nP=maxout_pieces,
            dropout=0.0,
        ),
        LayerNorm(token_vector_width * 2),
        softmax,
    )
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("output_layer", softmax)
    return model


def build_cloze_multi_task_model(
    vocab: "Vocab", tok2vec: Model, maxout_pieces: int, hidden_size: int
) -> Model:
    nO = vocab.vectors.shape[1]
    output_layer = chain(
        cast(Model[List["Floats2d"], Floats2d], list2array()),
        Maxout(
            nO=hidden_size,
            nI=tok2vec.get_dim("nO"),
            nP=maxout_pieces,
            normalize=True,
            dropout=0.0,
        ),
        Linear(nO=nO, nI=hidden_size, init_W=zero_init),
    )
    model = chain(tok2vec, output_layer)
    model = build_masked_language_model(vocab, model)
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("output_layer", output_layer)
    return model


def build_cloze_characters_multi_task_model(
    vocab: "Vocab", tok2vec: Model, maxout_pieces: int, hidden_size: int, nr_char: int
) -> Model:
    output_layer = chain(
        cast(Model[List["Floats2d"], Floats2d], list2array()),
        Maxout(nO=hidden_size, nP=maxout_pieces),
        LayerNorm(nI=hidden_size),
        MultiSoftmax([256] * nr_char, nI=hidden_size),  # type: ignore[arg-type]
    )
    model = build_masked_language_model(vocab, chain(tok2vec, output_layer))
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("output_layer", output_layer)
    return model


def build_masked_language_model(
    vocab: "Vocab", wrapped_model: Model, mask_prob: float = 0.15
) -> Model:
    """Convert a model into a BERT-style masked language model"""
    random_words = _RandomWords(vocab)

    def mlm_forward(model, docs, is_train):
        mask, docs = _apply_mask(docs, random_words, mask_prob=mask_prob)
        mask = model.ops.asarray(mask).reshape((mask.shape[0], 1))
        output, backprop = model.layers[0](docs, is_train)

        def mlm_backward(d_output):
            d_output *= 1 - mask
            return backprop(d_output)

        return output, mlm_backward

    def mlm_initialize(model: Model, X=None, Y=None):
        wrapped = model.layers[0]
        wrapped.initialize(X=X, Y=Y)
        for dim in wrapped.dim_names:
            if wrapped.has_dim(dim):
                model.set_dim(dim, wrapped.get_dim(dim))

    mlm_model: Model = Model(
        "masked-language-model",
        mlm_forward,
        layers=[wrapped_model],
        init=mlm_initialize,
        refs={"wrapped": wrapped_model},
        dims={dim: None for dim in wrapped_model.dim_names},
    )
    mlm_model.set_ref("wrapped", wrapped_model)
    return mlm_model


class _RandomWords:
    def __init__(self, vocab: "Vocab") -> None:
        # Extract lexeme representations
        self.words = [lex.text for lex in vocab if lex.prob != 0.0]
        self.words = self.words[:10000]

        # Compute normalized lexeme probabilities
        probs = [lex.prob for lex in vocab if lex.prob != 0.0]
        probs = probs[:10000]
        probs: numpy.ndarray = numpy.exp(numpy.array(probs, dtype="f"))
        probs /= probs.sum()
        self.probs = probs

        # Initialize cache
        self._cache: List[int] = []

    def next(self) -> str:
        if not self._cache:
            self._cache.extend(
                numpy.random.choice(len(self.words), 10000, p=self.probs)
            )
        index = self._cache.pop()
        return self.words[index]


def _apply_mask(
    docs: Iterable["Doc"], random_words: _RandomWords, mask_prob: float = 0.15
) -> Tuple[numpy.ndarray, List["Doc"]]:
    # This needs to be here to avoid circular imports
    from ...tokens.doc import Doc  # noqa: F811

    N = sum(len(doc) for doc in docs)
    mask = numpy.random.uniform(0.0, 1.0, (N,))
    mask = mask >= mask_prob
    i = 0
    masked_docs = []
    for doc in docs:
        words = []
        for token in doc:
            if not mask[i]:
                word = _replace_word(token.text, random_words)
            else:
                word = token.text
            words.append(word)
            i += 1
        spaces = [bool(w.whitespace_) for w in doc]
        # NB: If you change this implementation to instead modify
        # the docs in place, take care that the IDs reflect the original
        # words. Currently we use the original docs to make the vectors
        # for the target, so we don't lose the original tokens. But if
        # you modified the docs in place here, you would.
        masked_docs.append(Doc(doc.vocab, words=words, spaces=spaces))
    return mask, masked_docs


def _replace_word(word: str, random_words: _RandomWords, mask: str = "[MASK]") -> str:
    roll = numpy.random.random()
    if roll < 0.8:
        return mask
    elif roll < 0.9:
        return random_words.next()
    else:
        return word
