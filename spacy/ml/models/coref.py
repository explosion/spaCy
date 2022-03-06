from dataclasses import dataclass
import warnings

from thinc.api import Model, Linear, Relu, Dropout
from thinc.api import chain, noop, Embed, add, tuplify, concatenate
from thinc.api import reduce_first, reduce_last, reduce_mean
from thinc.types import Floats2d, Floats1d, Ints2d, Ragged
from typing import List, Callable, Tuple, Any
from ...tokens import Doc
from ...util import registry
from ..extract_spans import extract_spans

from .coref_util import get_candidate_mentions, select_non_crossing_spans, topk


@registry.architectures("spacy.Coref.v1")
def build_coref(
    tok2vec: Model[List[Doc], List[Floats2d]],
    get_mentions: Any = get_candidate_mentions,
    hidden: int = 1000,
    dropout: float = 0.3,
    mention_limit: int = 3900,
    # TODO this needs a better name. It limits the max mentions as a ratio of
    # the token count.
    mention_limit_ratio: float = 0.4,
    max_span_width: int = 20,
    antecedent_limit: int = 50,
):
    dim = tok2vec.get_dim("nO") * 3

    span_embedder = build_span_embedder(get_mentions, max_span_width)

    with Model.define_operators({">>": chain, "&": tuplify, "+": add}):

        mention_scorer = (
            Linear(nI=dim, nO=hidden)
            >> Relu(nI=hidden, nO=hidden)
            >> Dropout(dropout)
            >> Linear(nI=hidden, nO=hidden)
            >> Relu(nI=hidden, nO=hidden)
            >> Dropout(dropout)
            >> Linear(nI=hidden, nO=1)
        )
        mention_scorer.initialize()

        # TODO make feature_embed_size a param
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
    model = Model("WidthScorer", forward=width_score_forward, layers=[span_width_prior])
    model.set_ref("width_prior", span_width_prior)
    return model


def width_score_forward(
    model, embeds: SpanEmbeddings, is_train
) -> Tuple[Floats1d, Callable]:
    # calculate widths, subtracting 1 so it's 0-index
    w_ffnn = model.get_ref("width_prior")
    idxs = embeds.indices
    widths = idxs[:, 1] - idxs[:, 0] - 1
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
        span_reduce = extract_spans() >> (
            reduce_first() | reduce_last() | reduce_mean()
        )
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
    docmenlens = []  # number of mentions per doc

    for doc in docs:
        starts, ends = get_mentions(doc, max_span_width)
        docmenlens.append(len(starts))
        cments = ops.asarray2i([starts, ends]).transpose()

        mentions = xp.concatenate((mentions, cments))

    # TODO support attention here
    tokvecs = xp.concatenate(tokvecs)
    doclens = [len(doc) for doc in docs]
    tokvecs_r = Ragged(tokvecs, doclens)
    mentions_r = Ragged(mentions, docmenlens)

    span_reduce = model.get_ref("span_reducer")
    spanvecs, span_reduce_back = span_reduce((tokvecs_r, mentions_r), is_train)

    embeds = Ragged(spanvecs, docmenlens)

    def backprop_span_embed(dY: SpanEmbeddings) -> Tuple[List[Floats2d], List[Doc]]:
        grad, idxes = span_reduce_back(dY.vectors.data)

        oweights = []
        offset = 0
        for doclen in doclens:
            hi = offset + doclen
            oweights.append(grad.data[offset:hi])
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
        # This is relatively slow but can't be skipped.
        tops = (model.ops.xp.argsort(-1 * cscores)).tolist()
        starts = spanembeds.indices[offset:hi, 0].tolist()
        ends = spanembeds.indices[offset:hi:, 1].tolist()

        # calculate the doc length
        doclen = ends[-1] - starts[0]
        # XXX seems to make more sense to use menlen than doclen here?
        # coref-hoi uses doclen (number of words). 
        mlimit = min(mention_limit, int(mention_limit_ratio * doclen))
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
    model = Model(
        "AntScorer",
        forward=ant_scorer_forward,
        layers=[bilinear, dropout],
        attrs={
            "ant_limit": ant_limit,
        },
    )
    model.set_ref("bilinear", bilinear)
    model.set_ref("dropout", dropout)
    return model


def ant_scorer_forward(
    model, inputs: Tuple[Floats1d, SpanEmbeddings], is_train
) -> Tuple[Tuple[List[Tuple[Floats2d, Ints2d]], Ints2d], Callable]:
    ops = model.ops
    xp = ops.xp

    ant_limit = model.attrs["ant_limit"]
    # this contains the coarse bilinear in coref-hoi
    # coarse bilinear is a single layer linear network
    # TODO make these proper refs
    bilinear = model.get_ref("bilinear")
    dropout = model.get_ref("dropout")

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
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            mask = xp.log(
                (xp.expand_dims(ant_range, 1) - xp.expand_dims(ant_range, 0)) >= 1
            ).astype("f")

        scores = pw_prod + pw_sum + mask

        top_limit = min(ant_limit, len(scores))
        top_scores, top_scores_idx = topk(xp, scores, top_limit)
        # now add the placeholder
        placeholder = ops.alloc2f(scores.shape[0], 1)
        top_scores = xp.concatenate((placeholder, top_scores), 1)

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
            hi = offset + ll
            dyscore, dyidx = dy
            # remove the placeholder
            dyscore = dyscore[:, 1:]
            # the full score grid is square

            fullscore = ops.alloc2f(ll, ll)
            for ii, (ridx, rscores) in enumerate(zip(dyidx, dyscore)):
                fullscore[ii][ridx] = rscores

            dXembeds.data[offset:hi] = prod_back(fullscore)
            dXscores[offset:hi] = pw_sum_back(fullscore)

            offset = hi
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

        out = d_pwsum.sum(axis=0) + d_pwsum.sum(axis=1)

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


# XXX here down is wl-coref
from typing import List, Tuple

import torch

# TODO rename this to coref_util
import .coref_util_wl as utils

# TODO rename to plain coref
@registry.architectures("spacy.WLCoref.v1")
def build_wl_coref_model(
        #TODO add other hyperparams
    tok2vec: Model[List[Doc], List[Floats2d]],
    ):
    
    # TODO change to use passed in values for config
    config = utils._load_config("/dev/null")
    with Model.define_operators({">>": chain}):

        coref_scorer, span_predictor = configure_pytorch_modules(config)
        # TODO chain tok2vec with these models
        coref_scorer = PyTorchWrapper(
            CorefScorer(
                config.device,
                config.embedding_size,
                config.hidden_size,
                config.n_hidden_layers,
                config.dropout_rate,
                config.rough_k,
                config.a_scoring_batch_size
            ),
            convert_inputs=convert_coref_scorer_inputs,
            convert_outputs=convert_coref_scorer_outputs
        )
        span_predictor = PyTorchWrapper(
            SpanPredictor(
                1024,
                config.sp_embedding_size,
                config.device
            ),
            convert_inputs=convert_span_predictor_inputs
        )
    # TODO combine models so output is uniform (just one forward pass)
    # It may be reasonable to have an option to disable span prediction,
    # and just return words as spans.
    return coref_scorer

def convert_coref_scorer_inputs(
    model: Model,
    X: Floats2d,
    is_train: bool
):
    word_features = xp2torch(X, requires_grad=False)
    return ArgsKwargs(args=(word_features, ), kwargs={}), lambda dX: []


def convert_coref_scorer_outputs(
    model: Model,
    inputs_outputs,
    is_train: bool
):
    _, outputs = inputs_outputs
    scores, indices = outputs

    def convert_for_torch_backward(dY: Floats2d) -> ArgsKwargs:
        dY_t = xp2torch(dY)
        return ArgsKwargs(
            args=([scores],),
            kwargs={"grad_tensors": [dY_t]},
        )

    scores_xp = torch2xp(scores)
    indices_xp = torch2xp(indices)
    return (scores_xp, indices_xp), convert_for_torch_backward

# TODO This probably belongs in the component, not the model.
def predict_span_clusters(span_predictor: Model,
                          sent_ids: Ints1d,
                          words: Floats2d,
                          clusters: List[Ints1d]):
    """
    Predicts span clusters based on the word clusters.

    Args:
        doc (Doc): the document data
        words (torch.Tensor): [n_words, emb_size] matrix containing
            embeddings for each of the words in the text
        clusters (List[List[int]]): a list of clusters where each cluster
            is a list of word indices

    Returns:
        List[List[Span]]: span clusters
    """
    if not clusters:
        return []

    xp = span_predictor.ops.xp
    heads_ids = xp.asarray(sorted(i for cluster in clusters for i in cluster))
    scores = span_predictor.predict((sent_ids, words, heads_ids))
    starts = scores[:, :, 0].argmax(axis=1).tolist()
    ends = (scores[:, :, 1].argmax(axis=1) + 1).tolist()

    head2span = {
        head: (start, end)
        for head, start, end in zip(heads_ids.tolist(), starts, ends)
    }

    return [[head2span[head] for head in cluster]
            for cluster in clusters]

# TODO add docstring for this, maybe move to utils.
# This might belong in the component.
def _clusterize(
        model,
        scores: Floats2d,
        top_indices: Ints2d
):
    xp = model.ops.xp
    antecedents = scores.argmax(axis=1) - 1
    not_dummy = antecedents >= 0
    coref_span_heads = xp.arange(0, len(scores))[not_dummy]
    antecedents = top_indices[coref_span_heads, antecedents[not_dummy]]
    n_words = scores.shape[0]
    nodes = [GraphNode(i) for i in range(n_words)]
    for i, j in zip(coref_span_heads.tolist(), antecedents.tolist()):
        nodes[i].link(nodes[j])
        assert nodes[i] is not nodes[j]

    clusters = []
    for node in nodes:
        if len(node.links) > 0 and not node.visited:
            cluster = []
            stack = [node]
            while stack:
                current_node = stack.pop()
                current_node.visited = True
                cluster.append(current_node.id)
                stack.extend(link for link in current_node.links if not link.visited)
            assert len(cluster) > 1
            clusters.append(sorted(cluster))
    return sorted(clusters)


class CorefScorer(torch.nn.Module):
    """Combines all coref modules together to find coreferent spans.

    Attributes:
        config (coref.config.Config): the model's configuration,
            see config.toml for the details
        epochs_trained (int): number of epochs the model has been trained for

    Submodules (in the order of their usage in the pipeline):
        rough_scorer (RoughScorer)
        pw (PairwiseEncoder)
        a_scorer (AnaphoricityScorer)
        sp (SpanPredictor)
    """
    def __init__(
        self,
        device: str,
        dist_emb_size: int,
        hidden_size: int,
        n_layers: int,
        dropout_rate: float,
        roughk: int,
        batch_size: int
    ):
        super().__init__()
        """
        A newly created model is set to evaluation mode.

        Args:
            config_path (str): the path to the toml file with the configuration
            section (str): the selected section of the config file
            epochs_trained (int): the number of epochs finished
                (useful for warm start)
        """
        # device, dist_emb_size, hidden_size, n_layers, dropout_rate
        self.pw = DistancePairwiseEncoder(dist_emb_size, dropout_rate).to(device)
        bert_emb = 1024
        pair_emb = bert_emb * 3 + self.pw.shape
        self.a_scorer = AnaphoricityScorer(
            pair_emb,
            hidden_size,
            n_layers,
            dropout_rate
        ).to(device)
        self.lstm = torch.nn.LSTM(
            input_size=bert_emb,
            hidden_size=bert_emb,
            batch_first=True,
        )
        self.dropout = torch.nn.Dropout(dropout_rate)
        self.rough_scorer = RoughScorer(
            bert_emb,
            dropout_rate,
            roughk
        ).to(device)
        self.batch_size = batch_size

    def forward(
        self,
        word_features: torch.Tensor
) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        This is a massive method, but it made sense to me to not split it into
        several ones to let one see the data flow.

        Args:
            word_features: torch.Tensor containing word encodings
        Returns:
            coreference scores and top indices
        """
        # words           [n_words, span_emb]
        # cluster_ids     [n_words]
        word_features = torch.unsqueeze(word_features, dim=0)
        words, _ = self.lstm(word_features)
        words = words.squeeze()
        words = self.dropout(words)
        # Obtain bilinear scores and leave only top-k antecedents for each word
        # top_rough_scores  [n_words, n_ants]
        # top_indices       [n_words, n_ants]
        top_rough_scores, top_indices = self.rough_scorer(words)
        # Get pairwise features [n_words, n_ants, n_pw_features]
        pw = self.pw(top_indices)
        batch_size = self.batch_size
        a_scores_lst: List[torch.Tensor] = []

        for i in range(0, len(words), batch_size):
            pw_batch = pw[i:i + batch_size]
            words_batch = words[i:i + batch_size]
            top_indices_batch = top_indices[i:i + batch_size]
            top_rough_scores_batch = top_rough_scores[i:i + batch_size]

            # a_scores_batch    [batch_size, n_ants]
            a_scores_batch = self.a_scorer(
                all_mentions=words, mentions_batch=words_batch,
                pw_batch=pw_batch, top_indices_batch=top_indices_batch,
                top_rough_scores_batch=top_rough_scores_batch
            )
            a_scores_lst.append(a_scores_batch)

        coref_scores = torch.cat(a_scores_lst, dim=0)
        return coref_scores, top_indices


class AnaphoricityScorer(torch.nn.Module):
    """ Calculates anaphoricity scores by passing the inputs into a FFNN """
    def __init__(self,
                 in_features: int,
                 hidden_size,
                 n_hidden_layers,
                 dropout_rate):
        super().__init__()
        hidden_size = hidden_size
        if not n_hidden_layers:
            hidden_size = in_features
        layers = []
        for i in range(n_hidden_layers):
            layers.extend([torch.nn.Linear(hidden_size if i else in_features,
                                           hidden_size),
                           torch.nn.LeakyReLU(),
                           torch.nn.Dropout(dropout_rate)])
        self.hidden = torch.nn.Sequential(*layers)
        self.out = torch.nn.Linear(hidden_size, out_features=1)

    def forward(self, *,  # type: ignore  # pylint: disable=arguments-differ  #35566 in pytorch
                all_mentions: torch.Tensor,
                mentions_batch: torch.Tensor,
                pw_batch: torch.Tensor,
                top_indices_batch: torch.Tensor,
                top_rough_scores_batch: torch.Tensor,
                ) -> torch.Tensor:
        """ Builds a pairwise matrix, scores the pairs and returns the scores.

        Args:
            all_mentions (torch.Tensor): [n_mentions, mention_emb]
            mentions_batch (torch.Tensor): [batch_size, mention_emb]
            pw_batch (torch.Tensor): [batch_size, n_ants, pw_emb]
            top_indices_batch (torch.Tensor): [batch_size, n_ants]
            top_rough_scores_batch (torch.Tensor): [batch_size, n_ants]

        Returns:
            torch.Tensor [batch_size, n_ants + 1]
                anaphoricity scores for the pairs + a dummy column
        """
        # [batch_size, n_ants, pair_emb]
        pair_matrix = self._get_pair_matrix(
            all_mentions, mentions_batch, pw_batch, top_indices_batch)

        # [batch_size, n_ants]
        scores = top_rough_scores_batch + self._ffnn(pair_matrix)
        scores = utils.add_dummy(scores, eps=True)

        return scores

    def _ffnn(self, x: torch.Tensor) -> torch.Tensor:
        """
        Calculates anaphoricity scores.

        Args:
            x: tensor of shape [batch_size, n_ants, n_features]

        Returns:
            tensor of shape [batch_size, n_ants]
        """
        x = self.out(self.hidden(x))
        return x.squeeze(2)

    @staticmethod
    def _get_pair_matrix(all_mentions: torch.Tensor,
                         mentions_batch: torch.Tensor,
                         pw_batch: torch.Tensor,
                         top_indices_batch: torch.Tensor,
                         ) -> torch.Tensor:
        """
        Builds the matrix used as input for AnaphoricityScorer.

        Args:
            all_mentions (torch.Tensor): [n_mentions, mention_emb],
                all the valid mentions of the document,
                can be on a different device
            mentions_batch (torch.Tensor): [batch_size, mention_emb],
                the mentions of the current batch,
                is expected to be on the current device
            pw_batch (torch.Tensor): [batch_size, n_ants, pw_emb],
                pairwise features of the current batch,
                is expected to be on the current device
            top_indices_batch (torch.Tensor): [batch_size, n_ants],
                indices of antecedents of each mention

        Returns:
            torch.Tensor: [batch_size, n_ants, pair_emb]
        """
        emb_size = mentions_batch.shape[1]
        n_ants = pw_batch.shape[1]

        a_mentions = mentions_batch.unsqueeze(1).expand(-1, n_ants, emb_size)
        b_mentions = all_mentions[top_indices_batch]
        similarity = a_mentions * b_mentions

        out = torch.cat((a_mentions, b_mentions, similarity, pw_batch), dim=2)
        return out



class RoughScorer(torch.nn.Module):
    """
    Is needed to give a roughly estimate of the anaphoricity of two candidates,
    only top scoring candidates are considered on later steps to reduce
    computational complexity.
    """
    def __init__(
            self,
            features: int, 
            dropout_rate: float, 
            rough_k: float
    ):
        super().__init__()
        self.dropout = torch.nn.Dropout(dropout_rate)
        self.bilinear = torch.nn.Linear(features, features)

        self.k = rough_k

    def forward(
        self,  # type: ignore  # pylint: disable=arguments-differ  #35566 in pytorch
        mentions: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns rough anaphoricity scores for candidates, which consist of
        the bilinear output of the current model summed with mention scores.
        """
        # [n_mentions, n_mentions]
        pair_mask = torch.arange(mentions.shape[0])
        pair_mask = pair_mask.unsqueeze(1) - pair_mask.unsqueeze(0)
        pair_mask = torch.log((pair_mask > 0).to(torch.float))
        pair_mask = pair_mask.to(mentions.device)
        bilinear_scores = self.dropout(self.bilinear(mentions)).mm(mentions.T)
        rough_scores = pair_mask + bilinear_scores

        return self._prune(rough_scores)

    def _prune(self,
               rough_scores: torch.Tensor
               ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Selects top-k rough antecedent scores for each mention.

        Args:
            rough_scores: tensor of shape [n_mentions, n_mentions], containing
                rough antecedent scores of each mention-antecedent pair.

        Returns:
            FloatTensor of shape [n_mentions, k], top rough scores
            LongTensor of shape [n_mentions, k], top indices
        """
        top_scores, indices = torch.topk(rough_scores,
                                         k=min(self.k, len(rough_scores)),
                                         dim=1, sorted=False)
        return top_scores, indices


class DistancePairwiseEncoder(torch.nn.Module):

    def __init__(self, embedding_size, dropout_rate):
        super().__init__()
        emb_size = embedding_size
        self.distance_emb = torch.nn.Embedding(9, emb_size)
        self.dropout = torch.nn.Dropout(dropout_rate)
        self.shape = emb_size

    @property
    def device(self) -> torch.device:
        """ A workaround to get current device (which is assumed to be the
        device of the first parameter of one of the submodules) """
        return next(self.distance_emb.parameters()).device


    def forward(self,  # type: ignore  # pylint: disable=arguments-differ  #35566 in pytorch
                top_indices: torch.Tensor
        ) -> torch.Tensor:
        word_ids = torch.arange(0, top_indices.size(0), device=self.device)
        distance = (word_ids.unsqueeze(1) - word_ids[top_indices]
                    ).clamp_min_(min=1)
        log_distance = distance.to(torch.float).log2().floor_()
        log_distance = log_distance.clamp_max_(max=6).to(torch.long)
        distance = torch.where(distance < 5, distance - 1, log_distance + 2)
        distance = self.distance_emb(distance)
        return self.dropout(distance)
