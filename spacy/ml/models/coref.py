from dataclasses import dataclass
import warnings

from thinc.api import Model, Linear, Relu, Dropout
from thinc.api import chain, noop, Embed, add, tuplify, concatenate
from thinc.api import reduce_first, reduce_last, reduce_mean
from thinc.api import PyTorchWrapper, ArgsKwargs
from thinc.types import Floats2d, Floats1d, Ints1d, Ints2d, Ragged
from typing import List, Callable, Tuple, Any
from ...tokens import Doc
from ...util import registry
from ..extract_spans import extract_spans

import torch
from thinc.util import xp2torch, torch2xp

from .coref_util import add_dummy, get_sentence_ids

@registry.architectures("spacy.Coref.v1")
def build_wl_coref_model(
    tok2vec: Model[List[Doc], List[Floats2d]],
    embedding_size: int = 20,
    hidden_size: int = 1024,
    n_hidden_layers: int = 1, # TODO rename to "depth"?
    dropout: float = 0.3,
    # pairs to keep per mention after rough scoring
    # TODO change to meaningful name
    rough_k: int = 50,
    # TODO is this not a training loop setting?
    a_scoring_batch_size: int = 512,
    # span predictor embeddings
    sp_embedding_size: int = 64,
    ):
    # TODO fix this
    try:
        dim = tok2vec.get_dim("nO")
    except ValueError:
        # happens with transformer listener
        dim = 768
    
    with Model.define_operators({">>": chain}):
        # TODO chain tok2vec with these models
        # TODO fix device - should be automatic
        device = "cuda:0"
        coref_scorer = PyTorchWrapper(
            CorefScorer(
                device,
                dim,
                embedding_size,
                hidden_size,
                n_hidden_layers,
                dropout,
                rough_k,
                a_scoring_batch_size
            ),
            convert_inputs=convert_coref_scorer_inputs,
            convert_outputs=convert_coref_scorer_outputs
        )

        coref_model = tok2vec >> coref_scorer
    # TODO combine models so output is uniform (just one forward pass)
    # It may be reasonable to have an option to disable span prediction,
    # and just return words as spans.
    return coref_model

@registry.architectures("spacy.SpanPredictor.v1")
def build_span_predictor(
    tok2vec: Model[List[Doc], List[Floats2d]],
    hidden_size: int = 1024,
    dist_emb_size: int = 64,
    ):
    # TODO fix this
    try:
        dim = tok2vec.get_dim("nO")
    except ValueError:
        # happens with transformer listener
        dim = 768

    with Model.define_operators({">>": chain, "&": tuplify}):
        # TODO fix device - should be automatic
        device = "cuda:0"
        span_predictor = PyTorchWrapper(
            SpanPredictor(dim, hidden_size, dist_emb_size, device),
            convert_inputs=convert_span_predictor_inputs
        )
        # TODO use proper parameter for prefix
        head_info = build_get_head_metadata("coref_head_clusters")
        model = (tok2vec & head_info) >> span_predictor

    return model


def convert_coref_scorer_inputs(
    model: Model,
    X: List[Floats2d],
    is_train: bool
):
    # The input here is List[Floats2d], one for each doc
    # just use the first
    # TODO real batching
    X = X[0]


    word_features = xp2torch(X, requires_grad=is_train)
    def backprop(args: ArgsKwargs) -> List[Floats2d]:
        # convert to xp and wrap in list
        gradients = torch2xp(args.args[0])
        return [gradients]
    return ArgsKwargs(args=(word_features, ), kwargs={}), backprop


def convert_coref_scorer_outputs(
    model: Model,
    inputs_outputs,
    is_train: bool
):
    _, outputs = inputs_outputs
    scores, indices = outputs

    def convert_for_torch_backward(dY: Floats2d) -> ArgsKwargs:
        dY_t = xp2torch(dY[0])
        return ArgsKwargs(
            args=([scores],),
            kwargs={"grad_tensors": [dY_t]},
        )

    scores_xp = torch2xp(scores)
    indices_xp = torch2xp(indices)
    return (scores_xp, indices_xp), convert_for_torch_backward

def convert_span_predictor_inputs(
    model: Model,
    X: Tuple[Ints1d, Floats2d, Ints1d],
    is_train: bool
):
    tok2vec, (sent_ids, head_ids) = X
    # Normally we shoudl use the input is_train, but for these two it's not relevant
    sent_ids = xp2torch(sent_ids[0], requires_grad=False)
    head_ids = xp2torch(head_ids[0], requires_grad=False)

    word_features = xp2torch(tok2vec[0], requires_grad=is_train)

    argskwargs = ArgsKwargs(args=(sent_ids, word_features, head_ids), kwargs={})
    # TODO actually support backprop
    return argskwargs, lambda dX: []

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

def build_get_head_metadata(prefix):
    # TODO this name is awful, fix it
    model = Model("HeadDataProvider", attrs={"prefix": prefix}, forward=head_data_forward)
    return model

def head_data_forward(model, docs, is_train):
    """A layer to generate the extra data needed for the span predictor.
    """
    sent_ids = []
    head_ids = []
    prefix = model.attrs["prefix"]

    for doc in docs:
        sids = model.ops.asarray2i(get_sentence_ids(doc))
        sent_ids.append(sids)
        heads = []
        for key, sg in doc.spans.items():
            if not key.startswith(prefix):
                continue
            for span in sg:
                # TODO warn if spans are more than one token
                heads.append(span[0].i)
        heads = model.ops.asarray2i(heads)
        head_ids.append(heads)
    
    # each of these is a list with one entry per doc
    # backprop is just a placeholder
    # TODO it would probably be better to have a list of tuples than two lists of arrays
    return (sent_ids, head_ids), lambda x: []


class CorefScorer(torch.nn.Module):
    """Combines all coref modules together to find coreferent spans.

    Attributes:
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
        dim: int, # tok2vec size
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
            epochs_trained (int): the number of epochs finished
                (useful for warm start)
        """
        # device, dist_emb_size, hidden_size, n_layers, dropout_rate
        self.pw = DistancePairwiseEncoder(dist_emb_size, dropout_rate).to(device)
        #TODO clean this up
        bert_emb = dim
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
        self.lstm.flatten_parameters() # XXX without this there's a warning
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
        scores = add_dummy(scores, eps=True)

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


class SpanPredictor(torch.nn.Module):
    def __init__(self, input_size: int, hidden_size: int, dist_emb_size: int, device):
        super().__init__()
        # input size = single token size
        # 64 = probably distance emb size
        # TODO check that dist_emb_size use is correct
        self.ffnn = torch.nn.Sequential(
            torch.nn.Linear(input_size * 2 + dist_emb_size, hidden_size),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            #TODO seems weird the 256 isn't a parameter???
            torch.nn.Linear(hidden_size, 256),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            # this use of dist_emb_size looks wrong but it was 64...?
            torch.nn.Linear(256, dist_emb_size),
        )
        self.device = device
        self.conv = torch.nn.Sequential(
            torch.nn.Conv1d(64, 4, 3, 1, 1),
            torch.nn.Conv1d(4, 2, 3, 1, 1)
        )
        self.emb = torch.nn.Embedding(128, dist_emb_size) # [-63, 63] + too_far

    def forward(self,  # type: ignore  # pylint: disable=arguments-differ  #35566 in pytorch
                sent_id,
                words: torch.Tensor,
                heads_ids: torch.Tensor) -> torch.Tensor:
        """
        Calculates span start/end scores of words for each span head in
        heads_ids

        Args:
            doc (Doc): the document data
            words (torch.Tensor): contextual embeddings for each word in the
                document, [n_words, emb_size]
            heads_ids (torch.Tensor): word indices of span heads

        Returns:
            torch.Tensor: span start/end scores, [n_heads, n_words, 2]
        """
        # Obtain distance embedding indices, [n_heads, n_words]
        relative_positions = (heads_ids.unsqueeze(1) - torch.arange(words.shape[0], device=words.device).unsqueeze(0))
        # make all valid distances positive
        emb_ids = relative_positions + 63
        # "too_far"
        emb_ids[(emb_ids < 0) + (emb_ids > 126)] = 127
        # Obtain "same sentence" boolean mask, [n_heads, n_words]
        sent_id = torch.tensor(sent_id, device=words.device)
        heads_ids = heads_ids.long()
        same_sent = (sent_id[heads_ids].unsqueeze(1) == sent_id.unsqueeze(0))

        # To save memory, only pass candidates from one sentence for each head
        # pair_matrix contains concatenated span_head_emb + candidate_emb + distance_emb
        # for each candidate among the words in the same sentence as span_head
        # [n_heads, input_size * 2 + distance_emb_size]
        rows, cols = same_sent.nonzero(as_tuple=True)
        pair_matrix = torch.cat((
            words[heads_ids[rows]],
            words[cols],
            self.emb(emb_ids[rows, cols]),
        ), dim=1)

        lengths = same_sent.sum(dim=1)
        padding_mask = torch.arange(0, lengths.max().item(), device=words.device).unsqueeze(0)
        padding_mask = (padding_mask < lengths.unsqueeze(1))  # [n_heads, max_sent_len]

        # [n_heads, max_sent_len, input_size * 2 + distance_emb_size]
        # This is necessary to allow the convolution layer to look at several
        # word scores
        padded_pairs = torch.zeros(*padding_mask.shape, pair_matrix.shape[-1], device=words.device)
        padded_pairs[padding_mask] = pair_matrix

        res = self.ffnn(padded_pairs) # [n_heads, n_candidates, last_layer_output]
        res = self.conv(res.permute(0, 2, 1)).permute(0, 2, 1) # [n_heads, n_candidates, 2]

        scores = torch.full((heads_ids.shape[0], words.shape[0], 2), float('-inf'), device=words.device)
        scores[rows, cols] = res[padding_mask]

        # Make sure that start <= head <= end during inference
        if not self.training:
            valid_starts = torch.log((relative_positions >= 0).to(torch.float))
            valid_ends = torch.log((relative_positions <= 0).to(torch.float))
            valid_positions = torch.stack((valid_starts, valid_ends), dim=2)
            return scores + valid_positions
        return scores
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
