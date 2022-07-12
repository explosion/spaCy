from typing import List, Tuple, Callable, cast

from thinc.api import Model, chain, get_width
from thinc.api import PyTorchWrapper, ArgsKwargs
from thinc.types import Floats2d, Ints2d
from thinc.util import torch, xp2torch, torch2xp

from ...tokens import Doc
from ...util import registry


EPSILON = 1e-7


@registry.architectures("spacy.Coref.v1")
def build_wl_coref_model(
    tok2vec: Model[List[Doc], List[Floats2d]],
    distance_embedding_size: int = 20,
    hidden_size: int = 1024,
    depth: int = 1,
    dropout: float = 0.3,
    # pairs to keep per mention after rough scoring
    antecedent_limit: int = 50,
    antecedent_batch_size: int = 512,
    nI=None,
) -> Model[List[Doc], Tuple[Floats2d, Ints2d]]:

    with Model.define_operators({">>": chain}):
        coref_clusterer: Model[List[Floats2d], Tuple[Floats2d, Ints2d]] = Model(
            "coref_clusterer",
            forward=coref_forward,
            init=coref_init,
            dims={"nI": nI},
            attrs={
                "distance_embedding_size": distance_embedding_size,
                "hidden_size": hidden_size,
                "depth": depth,
                "dropout": dropout,
                "antecedent_limit": antecedent_limit,
                "antecedent_batch_size": antecedent_batch_size,
            },
        )

        model = tok2vec >> coref_clusterer
        model.set_ref("coref_clusterer", coref_clusterer)
    return model


def coref_init(model: Model, X=None, Y=None):
    if model.layers:
        return

    if X is not None and model.has_dim("nI") is None:
        model.set_dim("nI", get_width(X))

    hidden_size = model.attrs["hidden_size"]
    depth = model.attrs["depth"]
    dropout = model.attrs["dropout"]
    antecedent_limit = model.attrs["antecedent_limit"]
    antecedent_batch_size = model.attrs["antecedent_batch_size"]
    distance_embedding_size = model.attrs["distance_embedding_size"]

    model._layers = [
        PyTorchWrapper(
            CorefClusterer(
                model.get_dim("nI"),
                distance_embedding_size,
                hidden_size,
                depth,
                dropout,
                antecedent_limit,
                antecedent_batch_size,
            ),
            convert_inputs=convert_coref_clusterer_inputs,
            convert_outputs=convert_coref_clusterer_outputs,
        )
        # TODO maybe we need mixed precision and grad scaling?
    ]


def coref_forward(model: Model, X, is_train: bool):
    return model.layers[0](X, is_train)

def convert_coref_clusterer_inputs(model: Model, X: List[Floats2d], is_train: bool):
    # The input here is List[Floats2d], one for each doc
    # just use the first
    # TODO real batching
    X = X[0]
    word_features = xp2torch(X, requires_grad=is_train)

    def backprop(args: ArgsKwargs) -> List[Floats2d]:
        # convert to xp and wrap in list
        gradients = cast(Floats2d, torch2xp(args.args[0]))
        return [gradients]

    return ArgsKwargs(args=(word_features,), kwargs={}), backprop


def convert_coref_clusterer_outputs(
    model: Model, inputs_outputs, is_train: bool
) -> Tuple[Tuple[Floats2d, Ints2d], Callable]:
    _, outputs = inputs_outputs
    scores, indices = outputs

    def convert_for_torch_backward(dY: Floats2d) -> ArgsKwargs:
        dY_t = xp2torch(dY[0])
        return ArgsKwargs(
            args=([scores],),
            kwargs={"grad_tensors": [dY_t]},
        )

    scores_xp = cast(Floats2d, torch2xp(scores))
    indices_xp = cast(Ints2d, torch2xp(indices))
    return (scores_xp, indices_xp), convert_for_torch_backward


class CorefClusterer(torch.nn.Module):
    """
    Combines all coref modules together to find coreferent token pairs.
    Submodules (in the order of their usage in the pipeline):
        - rough_scorer (RoughScorer) that prunes candidate pairs
        - pw (DistancePairwiseEncoder) that computes pairwise features
        - a_scorer (AnaphoricityScorer) produces the final scores
    """

    def __init__(
        self,
        dim: int,
        dist_emb_size: int,
        hidden_size: int,
        n_layers: int,
        dropout: float,
        roughk: int,
        batch_size: int,
    ):
        super().__init__()
        """
        dim: Size of the input features.
        dist_emb_size: Size of the distance embeddings.
        hidden_size: Size of the coreference candidate embeddings.
        n_layers: Numbers of layers in the AnaphoricityScorer.
        dropout: Dropout probability to apply across all modules.
        roughk: Number of candidates the RoughScorer returns.
        batch_size: Internal batch-size for the more expensive scorer.
        """
        self.dropout = torch.nn.Dropout(dropout)
        self.batch_size = batch_size
        self.pw = DistancePairwiseEncoder(dist_emb_size, dropout)

        pair_emb = dim * 3 + self.pw.shape
        self.a_scorer = AnaphoricityScorer(pair_emb, hidden_size, n_layers, dropout)
        self.lstm = torch.nn.LSTM(
            input_size=dim,
            hidden_size=dim,
            batch_first=True,
        )

        self.rough_scorer = RoughScorer(dim, dropout, roughk)

    def forward(self, word_features: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        1. LSTM encodes the incoming word_features.
        2. The RoughScorer scores and prunes the candidates.
        3. The DistancePairwiseEncoder embeds the distances between pairs.
        4. The AnaphoricityScorer scores all pairs in mini-batches.

        word_features: torch.Tensor containing word encodings

        returns:
            coref_scores: n_words x roughk floats.
            top_indices: n_words x roughk integers.
        """
        self.lstm.flatten_parameters()  # XXX without this there's a warning
        word_features = torch.unsqueeze(word_features, dim=0)
        words, _ = self.lstm(word_features)
        words = words.squeeze()
        # words: n_words x dim
        words = self.dropout(words)
        # Obtain bilinear scores and leave only top-k antecedents for each word
        # top_rough_scores: (n_words x roughk)
        # top_indices: (n_words x roughk)
        top_rough_scores, top_indices = self.rough_scorer(words)
        # Get pairwise features
        # (n_words x roughk x n_pw_features)
        pw = self.pw(top_indices)
        batch_size = self.batch_size
        a_scores_lst: List[torch.Tensor] = []

        for i in range(0, len(words), batch_size):
            pw_batch = pw[i : i + batch_size]
            words_batch = words[i : i + batch_size]
            top_indices_batch = top_indices[i : i + batch_size]
            top_rough_scores_batch = top_rough_scores[i : i + batch_size]

            # a_scores_batch    [batch_size, n_ants]
            a_scores_batch = self.a_scorer(
                all_mentions=words,
                mentions_batch=words_batch,
                pw_batch=pw_batch,
                top_indices_batch=top_indices_batch,
                top_rough_scores_batch=top_rough_scores_batch,
            )
            a_scores_lst.append(a_scores_batch)

        coref_scores = torch.cat(a_scores_lst, dim=0)
        return coref_scores, top_indices


# Note this function is kept here to keep a torch dep out of coref_util.
def add_dummy(tensor: torch.Tensor, eps: bool = False):
    """Prepends zeros (or a very small value if eps is True)
    to the first (not zeroth) dimension of tensor.
    """
    kwargs = dict(device=tensor.device, dtype=tensor.dtype)
    shape: List[int] = list(tensor.shape)
    shape[1] = 1
    if not eps:
        dummy = torch.zeros(shape, **kwargs)  # type: ignore
    else:
        dummy = torch.full(shape, EPSILON, **kwargs)  # type: ignore
    output = torch.cat((dummy, tensor), dim=1)
    return output


class AnaphoricityScorer(torch.nn.Module):
    """Calculates anaphoricity scores by passing the inputs into a FFNN"""

    def __init__(self, in_features: int, hidden_size, depth, dropout):
        super().__init__()
        hidden_size = hidden_size
        if not depth:
            hidden_size = in_features
        layers = []
        for i in range(depth):
            layers.extend(
                [
                    torch.nn.Linear(hidden_size if i else in_features, hidden_size),
                    torch.nn.LeakyReLU(),
                    torch.nn.Dropout(dropout),
                ]
            )
        self.hidden = torch.nn.Sequential(*layers)
        self.out = torch.nn.Linear(hidden_size, out_features=1)

    def forward(
        self,
        *,  # type: ignore  # pylint: disable=arguments-differ  #35566 in pytorch
        all_mentions: torch.Tensor,
        mentions_batch: torch.Tensor,
        pw_batch: torch.Tensor,
        top_indices_batch: torch.Tensor,
        top_rough_scores_batch: torch.Tensor,
    ) -> torch.Tensor:
        """Builds a pairwise matrix, scores the pairs and returns the scores.

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
            all_mentions, mentions_batch, pw_batch, top_indices_batch
        )

        # [batch_size, n_ants]
        scores = top_rough_scores_batch + self._ffnn(pair_matrix)
        scores = add_dummy(scores, eps=True)

        return scores

    def _ffnn(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: tensor of shape (batch_size x roughk x n_features
        returns: tensor of shape (batch_size x antecedent_limit)
        """
        x = self.out(self.hidden(x))
        return x.squeeze(2)

    @staticmethod
    def _get_pair_matrix(
        all_mentions: torch.Tensor,
        mentions_batch: torch.Tensor,
        pw_batch: torch.Tensor,
        top_indices_batch: torch.Tensor,
    ) -> torch.Tensor:
        """
        Builds the matrix used as input for AnaphoricityScorer.

        all_mentions: (n_mentions x mention_emb),
            all the valid mentions of the document,
            can be on a different device
        mentions_batch: (batch_size x mention_emb),
            the mentions of the current batch.
        pw_batch: (batch_size x roughk x pw_emb),
            pairwise distance features of the current batch.
        top_indices_batch: (batch_size x n_ants),
            indices of antecedents of each mention

        Returns:
            out: pairwise features (batch_size x n_ants x pair_emb)
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
    Cheaper module that gives a rough estimate of the anaphoricity of two
    candidates, only top scoring candidates are considered on later
    steps to reduce computational cost.
    """

    def __init__(self, features: int, dropout: float, antecedent_limit: int):
        super().__init__()
        self.dropout = torch.nn.Dropout(dropout)
        self.bilinear = torch.nn.Linear(features, features)
        self.k = antecedent_limit

    def forward(
        self,  # type: ignore
        mentions: torch.Tensor,
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
        top_scores, indices = torch.topk(
            rough_scores, k=min(self.k, len(rough_scores)), dim=1, sorted=False
        )

        return top_scores, indices


class DistancePairwiseEncoder(torch.nn.Module):
    def __init__(self, distance_embedding_size, dropout):
        """
        Takes the top_indices indicating, which is a ranked
        list for each word and its most likely corresponding
        anaphora candidates. For each of these pairs it looks
        up a distance embedding from a table, where the distance
        corresponds to the log-distance.

        distance_embedding_size: int,
            Dimensionality of the distance-embeddings table.
        dropout: float,
            Dropout probability.
        """
        super().__init__()
        emb_size = distance_embedding_size
        self.distance_emb = torch.nn.Embedding(9, emb_size)
        self.dropout = torch.nn.Dropout(dropout)
        self.shape = emb_size

    def forward(self, top_indices: torch.Tensor) -> torch.Tensor:
        word_ids = torch.arange(0, top_indices.size(0))
        distance = (word_ids.unsqueeze(1) - word_ids[top_indices]).clamp_min_(min=1)
        log_distance = distance.to(torch.float).log2().floor_()
        log_distance = log_distance.clamp_max_(max=6).to(torch.long)
        distance = torch.where(distance < 5, distance - 1, log_distance + 2)
        distance = distance.to(top_indices.device)
        distance = self.distance_emb(distance)
        return self.dropout(distance)
