from typing import Optional, List
from thinc.api import chain, clone, concatenate, with_array, with_padded
from thinc.api import Model, noop, list2ragged, ragged2list
from thinc.api import FeatureExtractor, HashEmbed
from thinc.api import expand_window, residual, Maxout, Mish
from thinc.types import Floats2d

from ...tokens import Doc
from ... import util
from ...util import registry
from ...ml import _character_embed
from ..staticvectors import StaticVectors
from ...pipeline.tok2vec import Tok2VecListener
from ...attrs import ID, ORTH, NORM, PREFIX, SUFFIX, SHAPE


@registry.architectures.register("spacy.Tok2VecListener.v1")
def tok2vec_listener_v1(width, upstream="*"):
    tok2vec = Tok2VecListener(upstream_name=upstream, width=width)
    return tok2vec


@registry.architectures.register("spacy.Tok2Vec.v1")
def Tok2Vec(
    embed: Model[List[Doc], List[Floats2d]],
    encode: Model[List[Floats2d], List[Floats2d]],
) -> Model[List[Doc], List[Floats2d]]:

    receptive_field = encode.attrs.get("receptive_field", 0)
    tok2vec = chain(embed, with_array(encode, pad=receptive_field))
    tok2vec.set_dim("nO", encode.get_dim("nO"))
    tok2vec.set_ref("embed", embed)
    tok2vec.set_ref("encode", encode)
    return tok2vec


@registry.architectures.register("spacy.MultiHashEmbed.v1")
def MultiHashEmbed(
    width: int, rows: int, also_embed_subwords: bool, also_use_static_vectors: bool
):
    cols = [NORM, PREFIX, SUFFIX, SHAPE, ORTH]

    seed = 7

    def make_hash_embed(feature):
        nonlocal seed
        seed += 1
        return HashEmbed(
            width,
            rows if feature == NORM else rows // 2,
            column=cols.index(feature),
            seed=seed,
            dropout=0.0,
        )

    if also_embed_subwords:
        embeddings = [
            make_hash_embed(NORM),
            make_hash_embed(PREFIX),
            make_hash_embed(SUFFIX),
            make_hash_embed(SHAPE),
        ]
    else:
        embeddings = [make_hash_embed(NORM)]

    if also_use_static_vectors:
        model = chain(
            concatenate(
                chain(
                    FeatureExtractor(cols),
                    list2ragged(),
                    with_array(concatenate(*embeddings)),
                ),
                StaticVectors(width, dropout=0.0),
            ),
            with_array(Maxout(width, nP=3, dropout=0.0, normalize=True)),
            ragged2list(),
        )
    else:
        model = chain(
            chain(
                FeatureExtractor(cols),
                list2ragged(),
                with_array(concatenate(*embeddings)),
            ),
            with_array(Maxout(width, nP=3, dropout=0.0, normalize=True)),
            ragged2list(),
        )
    return model


@registry.architectures.register("spacy.CharacterEmbed.v1")
def CharacterEmbed(columns, width, rows, nM, nC, features, dropout):
    norm = HashEmbed(
        nO=width, nV=rows, column=columns.index("NORM"), dropout=dropout, seed=5
    )
    chr_embed = _character_embed.CharacterEmbed(nM=nM, nC=nC)
    with Model.define_operators({">>": chain, "|": concatenate}):
        embed_layer = chr_embed | features >> with_array(norm)
    embed_layer.set_dim("nO", nM * nC + width)
    return embed_layer


@registry.architectures.register("spacy.MaxoutWindowEncoder.v1")
def MaxoutWindowEncoder(width: int, window_size: int, maxout_pieces: int, depth: int):
    cnn = chain(
        expand_window(window_size=window_size),
        Maxout(
            nO=width,
            nI=width * ((window_size * 2) + 1),
            nP=maxout_pieces,
            dropout=0.0,
            normalize=True,
        ),
    )
    model = clone(residual(cnn), depth)
    model.set_dim("nO", width)
    model.attrs["receptive_field"] = window_size * depth
    return model


@registry.architectures.register("spacy.MishWindowEncoder.v1")
def MishWindowEncoder(width, window_size, depth):
    cnn = chain(
        expand_window(window_size=window_size),
        Mish(nO=width, nI=width * ((window_size * 2) + 1)),
        LayerNorm(width),
    )
    model = clone(residual(cnn), depth)
    model.set_dim("nO", width)
    return model


@registry.architectures.register("spacy.TorchBiLSTMEncoder.v1")
def BiLSTMEncoder(width, depth, dropout):
    if depth == 0:
        return noop()
    return with_padded(PyTorchLSTM(width, width, bi=True, depth=depth, dropout=dropout))
