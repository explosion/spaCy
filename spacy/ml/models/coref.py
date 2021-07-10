from dataclasses import dataclass
import warnings

from thinc.api import Model, Linear, Relu, Dropout
from thinc.api import chain, noop, Embed, add, tuplify
from thinc.types import Floats2d, Floats1d, Ints2d, Ragged
from typing import List, Callable, Tuple, Any
from ...tokens import Doc
from ...util import registry

from .coref_util import get_candidate_mentions, select_non_crossing_spans, topk


@registry.architectures("spacy.Coref.v1")
def build_coref(
    tok2vec: Model[List[Doc], List[Floats2d]],
    get_mentions: Any = get_candidate_mentions,
    hidden: int = 1000,
    dropout: float = 0.3,
    mention_limit: int = 3900,
    #TODO this needs a better name. It limits the max mentions as a ratio of 
    # the token count.
    mention_limit_ratio: float = 0.4,
    max_span_width: int = 20,
    antecedent_limit: int = 50
):
    dim = tok2vec.get_dim("nO") * 3

    span_embedder = build_span_embedder(get_mentions, max_span_width)

    with Model.define_operators({">>": chain, "&": tuplify, "+": add}):

        mention_scorer = (
            Linear(nI=dim, nO=hidden)
            >> Relu(nI=hidden, nO=hidden)
            >> Dropout(dropout)
            >> Linear(nI=hidden, nO=1)
        )
        mention_scorer.initialize()

        #TODO make feature_embed_size a param
        feature_embed_size = 20
        width_scorer = build_width_scorer(max_span_width, hidden, feature_embed_size)

        bilinear = Linear(nI=dim, nO=dim) >> Dropout(dropout)
        bilinear.initialize()

        ms = (build_take_vecs() >> mention_scorer) + width_scorer

        model = (
            (tok2vec & noop())
            >> span_embedder
            >> (ms & noop())
            >> build_coarse_pruner(mention_limit, mention_limit_ratio)
            >> build_ant_scorer(bilinear, Dropout(dropout), antecedent_limit)
        )
    return model


@dataclass
class SpanEmbeddings:
    indices: Ints2d  # Array with 2 columns (for start and end index)
    vectors: Ragged  # Ragged[Floats2d] # One vector per span
    # NB: We assume that the indices refer to a concatenated Floats2d that
    # has one row per token in the *batch* of documents. This makes it unambiguous
    # which row is in which document, because if the lengths are e.g. [10, 5],
    # a span starting at 11 must be starting at token 2 of doc 1. A bug could
    # potentially cause you to have a span which crosses a doc boundary though,
    # which would be bad.
    # The lengths in the Ragged are not the tokens per doc, but the number of
    # mentions per doc.

    def __add__(self, right):
        out = self.vectors.data + right.vectors.data
        return SpanEmbeddings(self.indices, Ragged(out, self.vectors.lengths))

    def __iadd__(self, right):
        self.vectors.data += right.vectors.data
        return self


def build_width_scorer(max_span_width, hidden_size, feature_embed_size=20):
    span_width_prior = (
        Embed(nV=max_span_width, nO=feature_embed_size)
        >> Linear(nI=feature_embed_size, nO=hidden_size)
        >> Relu(nI=hidden_size, nO=hidden_size)
        >> Dropout()
        >> Linear(nI=hidden_size, nO=1)
    )
    span_width_prior.initialize()
    return Model(
            "WidthScorer",
            forward=width_score_forward,
            layers=[span_width_prior])


def width_score_forward(model, embeds: SpanEmbeddings, is_train) -> Tuple[Floats1d, Callable]:
    # calculate widths, subtracting 1 so it's 0-index
    w_ffnn = model.layers[0]
    idxs = embeds.indices
    widths = idxs[:,1] - idxs[:,0] - 1
    wscores, width_b = w_ffnn(widths, is_train)

    lens = embeds.vectors.lengths

    def width_score_backward(d_score: Floats1d) -> SpanEmbeddings:

        dX = width_b(d_score)
        vecs = Ragged(dX, lens)
        return SpanEmbeddings(idxs, vecs)

    return wscores, width_score_backward

# model converting a Doc/Mention to span embeddings
# get_mentions: Callable[Doc, Pairs[int]]
def build_span_embedder(
    get_mentions: Callable,
    max_span_width: int = 20,
) -> Model[Tuple[List[Floats2d], List[Doc]], SpanEmbeddings]:

    with Model.define_operators({">>": chain, "|": concatenate}):
        span_reduce = (extract_spans() >> 
                (reduce_first() | reduce_last() | reduce_mean()))
    model = Model(
        "SpanEmbedding",
        forward=span_embeddings_forward,
        attrs={
            "get_mentions": get_mentions,
            # XXX might be better to make this an implicit parameter in the
            # mention generator
            "max_span_width": max_span_width,
        },
        layers=[span_reduce],
    )
    model.set_ref("span_reducer", span_reduce)
    return model


def span_embeddings_forward(
    model, inputs: Tuple[List[Floats2d], List[Doc]], is_train
) -> Tuple[SpanEmbeddings, Callable]:
    ops = model.ops
    xp = ops.xp

    tokvecs, docs = inputs

    # TODO fix this
    dim = tokvecs[0].shape[1]

    get_mentions = model.attrs["get_mentions"]
    max_span_width = model.attrs["max_span_width"]
    mentions = ops.alloc2i(0, 2)
    total_length = 0
    docmenlens = []  # number of mentions per doc

    for doc in docs:
        starts, ends = get_mentions(doc, max_span_width)
        docmenlens.append(len(starts))
        cments = ops.asarray2i([starts, ends]).transpose()

        mentions = xp.concatenate((mentions, cments + total_length))
        total_length += len(doc)

    # TODO support attention here
    tokvecs = xp.concatenate(tokvecs)
    tokvecs_r = Ragged(tokvecs, docmenlens)
    mentions_r = Ragged(mentions, docmenlens)

    span_reduce = model.get_ref("span_reducer")
    spanvecs, span_reduce_back = span_reduce( (tokvecs_r, mentions_r), is_train)

    embeds = Ragged(spanvecs, docmenlens)

    def backprop_span_embed(dY: SpanEmbeddings) -> Tuple[List[Floats2d], List[Doc]]:

        oweights = []
        offset = 0
        for mlen in dY.vectors.lengths:
            hi = offset + mlen
            vecs = dY.vectors.data[offset:hi]
            out, out_idx = span_reduce_back(vecs)
            oweights.append(out.data)

            offset = hi
        return oweights, docs

    return SpanEmbeddings(mentions, embeds), backprop_span_embed


def build_coarse_pruner(
    mention_limit: int,
    mention_limit_ratio: float,
) -> Model[SpanEmbeddings, SpanEmbeddings]:
    model = Model(
        "CoarsePruner",
        forward=coarse_prune,
        attrs={
            "mention_limit": mention_limit,
            "mention_limit_ratio": mention_limit_ratio,
        },
    )
    return model


def coarse_prune(
    model, inputs: Tuple[Floats1d, SpanEmbeddings], is_train
) -> Tuple[Tuple[Floats1d, SpanEmbeddings], Callable]:
    """Given scores for mention, output the top non-crossing mentions.

    Mentions can contain other mentions, but candidate mentions cannot cross each other.
    """
    rawscores, spanembeds = inputs
    scores = rawscores.flatten()
    mention_limit = model.attrs["mention_limit"]
    mention_limit_ratio = model.attrs["mention_limit_ratio"]
    # XXX: Issue here. Don't need docs to find crossing spans, but might for the limits.
    # In old code the limit can be:
    # - hard number per doc
    # - ratio of tokens in the doc

    offset = 0
    selected = []
    sellens = []
    for menlen in spanembeds.vectors.lengths:
        hi = offset + menlen
        cscores = scores[offset:hi]

        # negate it so highest numbers come first
        tops = (model.ops.xp.argsort(-1 * cscores)).tolist()
        starts = spanembeds.indices[offset:hi, 0].tolist()
        ends = spanembeds.indices[offset:hi:, 1].tolist()

        # calculate the doc length
        doclen = ends[-1] - starts[0]
        # XXX seems to make more sense to use menlen than doclen here?
        #mlimit = min(mention_limit, int(mention_limit_ratio * doclen))
        mlimit = min(mention_limit, int(mention_limit_ratio * menlen))
        # csel is a 1d integer list
        csel = select_non_crossing_spans(tops, starts, ends, mlimit)
        # add the offset so these indices are absolute
        csel = [ii + offset for ii in csel]
        # this should be constant because short choices are padded
        sellens.append(len(csel))
        selected += csel
        offset += menlen

    selected = model.ops.asarray1i(selected)
    top_spans = spanembeds.indices[selected]
    top_vecs = spanembeds.vectors.data[selected]

    out = SpanEmbeddings(top_spans, Ragged(top_vecs, sellens))

    # save some variables so the embeds can be garbage collected
    idxlen = spanembeds.indices.shape[0]
    vecshape = spanembeds.vectors.data.shape
    indices = spanembeds.indices
    veclens = out.vectors.lengths

    def coarse_prune_backprop(
        dY: Tuple[Floats1d, SpanEmbeddings]
    ) -> Tuple[Floats1d, SpanEmbeddings]:

        dYscores, dYembeds = dY

        dXscores = model.ops.alloc1f(idxlen)
        dXscores[selected] = dYscores.flatten()

        dXvecs = model.ops.alloc2f(*vecshape)
        dXvecs[selected] = dYembeds.vectors.data
        rout = Ragged(dXvecs, veclens)
        dXembeds = SpanEmbeddings(indices, rout)

        # inflate for mention scorer
        dXscores = model.ops.xp.expand_dims(dXscores, 1)

        return (dXscores, dXembeds)

    return (scores[selected], out), coarse_prune_backprop


def build_take_vecs() -> Model[SpanEmbeddings, Floats2d]:
    # this just gets vectors out of spanembeddings
    # XXX Might be better to convert SpanEmbeddings to a tuple and use with_getitem
    return Model("TakeVecs", forward=take_vecs_forward)


def take_vecs_forward(model, inputs: SpanEmbeddings, is_train) -> Floats2d:
    idxs = inputs.indices
    lens = inputs.vectors.lengths
    def backprop(dY: Floats2d) -> SpanEmbeddings:
        vecs = Ragged(dY, lens)
        return SpanEmbeddings(idxs, vecs)

    return inputs.vectors.data, backprop


def build_ant_scorer(
    bilinear, dropout, ant_limit=50
) -> Model[Tuple[Floats1d, SpanEmbeddings], List[Floats2d]]:
    return Model(
        "AntScorer",
        forward=ant_scorer_forward,
        layers=[bilinear, dropout],
        attrs={
            "ant_limit": ant_limit,
        },
    )


def ant_scorer_forward(
    model, inputs: Tuple[Floats1d, SpanEmbeddings], is_train
) -> Tuple[Tuple[List[Tuple[Floats2d, Ints2d]], Ints2d], Callable]:
    ops = model.ops
    xp = ops.xp

    ant_limit = model.attrs["ant_limit"]
    # this contains the coarse bilinear in coref-hoi
    # coarse bilinear is a single layer linear network
    # TODO make these proper refs
    bilinear = model.layers[0]
    dropout = model.layers[1]

    # XXX Note on dimensions: This won't work as a ragged because the floats2ds
    # are not all the same dimensions. Each floats2d is a square in the size of
    # the number of antecedents in the document. Actually, that will have the
    # same size if antecedents are padded... Needs checking.

    mscores, sembeds = inputs
    vecs = sembeds.vectors  # ragged

    offset = 0
    backprops = []
    out = []
    for ll in vecs.lengths:
        hi = offset + ll
        # each iteration is one doc

        # first calculate the pairwise product scores
        cvecs = vecs.data[offset:hi]
        pw_prod, prod_back = pairwise_product(bilinear, dropout, cvecs, is_train)

        # now calculate the pairwise mention scores
        ms = mscores[offset:hi].flatten()
        pw_sum, pw_sum_back = pairwise_sum(ops, ms)

        # make a mask so antecedents precede referrents
        ant_range = xp.arange(0, cvecs.shape[0])

        # This will take the log of 0, which causes a warning, but we're doing
        # it on purpose so we can just ignore the warning.
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            mask = xp.log(
                (xp.expand_dims(ant_range, 1) - xp.expand_dims(ant_range, 0)) >= 1
            ).astype('f')

        scores = pw_prod + pw_sum + mask

        top_limit = min(ant_limit, len(scores))
        top_scores, top_scores_idx = topk(xp, scores, top_limit)
        # now add the placeholder
        placeholder = ops.alloc2f(scores.shape[0], 1)
        top_scores = xp.concatenate( (placeholder, top_scores), 1)
        #top_scores = ops.softmax(top_scores, axis=1)

        out.append((top_scores, top_scores_idx))

        # In the full model these scores can be further refined. In the current
        # state of this model we're done here, so this pruning is less important,
        # but it's still helpful for reducing memory usage (since scores can be
        # garbage collected when the loop exits).

        offset += ll
        backprops.append((prod_back, pw_sum_back))

    # save vars for gc
    vecshape = vecs.data.shape
    veclens = vecs.lengths
    scoreshape = mscores.shape
    idxes = sembeds.indices

    def backprop(
        dYs: Tuple[List[Tuple[Floats2d, Ints2d]], Ints2d]
    ) -> Tuple[Floats2d, SpanEmbeddings]:
        dYscores, dYembeds = dYs
        dXembeds = Ragged(ops.alloc2f(*vecshape), veclens)
        dXscores = ops.alloc1f(*scoreshape)

        offset = 0
        for dy, (prod_back, pw_sum_back), ll in zip(dYscores, backprops, veclens):
            dyscore, dyidx = dy
            # remove the placeholder
            dyscore = dyscore[:, 1:]
            # the full score grid is square

            fullscore = ops.alloc2f(ll, ll)
            for ii, (ridx, rscores) in enumerate(zip(dyidx, dyscore)):
                fullscore[ii][ridx] = rscores

            dXembeds.data[offset : offset + ll] = prod_back(fullscore)
            dXscores[offset : offset + ll] = pw_sum_back(fullscore)

            offset += ll
        # make it fit back into the linear
        dXscores = xp.expand_dims(dXscores, 1)
        return (dXscores, SpanEmbeddings(idxes, dXembeds))

    return (out, sembeds.indices), backprop


def pairwise_sum(ops, mention_scores: Floats1d) -> Tuple[Floats2d, Callable]:
    """Find the most likely mention-antecedent pairs."""
    # This doesn't use multiplication because two items with low mention scores
    # don't make a good candidate pair.

    pw_sum = ops.xp.expand_dims(mention_scores, 1) + ops.xp.expand_dims(
        mention_scores, 0
    )

    def backward(d_pwsum: Floats2d) -> Floats1d:
        # For the backward pass, the gradient is distributed over the whole row and
        # column, so pull it all in.
        dim = d_pwsum.shape[0]
        out = ops.alloc1f(dim)
        for ii in range(dim):
            out[ii] = d_pwsum[:, ii].sum() + d_pwsum[ii, :].sum()

        return out

    return pw_sum, backward


def pairwise_product(bilinear, dropout, vecs: Floats2d, is_train):
    # A neat side effect of this is that we don't have to pass the backprops
    # around separately because the closure handles them.
    source, source_b = bilinear(vecs, is_train)
    target, target_b = dropout(vecs.T, is_train)
    pw_prod = source @ target

    def backward(d_prod: Floats2d) -> Floats2d:
        dS = source_b(d_prod @ target.T)
        dT = target_b(source.T @ d_prod)
        dX = dS + dT.T
        return dX

    return pw_prod, backward
