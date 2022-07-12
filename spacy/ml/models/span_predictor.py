from typing import List, Tuple, cast

from thinc.api import Model, chain, tuplify, get_width
from thinc.api import PyTorchWrapper, ArgsKwargs
from thinc.types import Floats2d, Ints1d
from thinc.util import torch, xp2torch, torch2xp

from ...tokens import Doc
from ...util import registry
from .coref_util import get_sentence_ids


@registry.architectures("spacy.SpanPredictor.v1")
def build_span_predictor(
    tok2vec: Model[List[Doc], List[Floats2d]],
    hidden_size: int = 1024,
    distance_embedding_size: int = 64,
    conv_channels: int = 4,
    window_size: int = 1,
    max_distance: int = 128,
    prefix: str = "coref_head_clusters",
):
    # TODO add model return types

    nI = None

    with Model.define_operators({">>": chain, "&": tuplify}):
        span_predictor: Model[List[Floats2d], List[Floats2d]] = Model(
            "span_predictor",
            forward=span_predictor_forward,
            init=span_predictor_init,
            dims={"nI": nI},
            attrs={
                "distance_embedding_size": distance_embedding_size,
                "hidden_size": hidden_size,
                "conv_channels": conv_channels,
                "window_size": window_size,
                "max_distance": max_distance,
            },
        )
        head_info = build_get_head_metadata(prefix)
        model = (tok2vec & head_info) >> span_predictor
        model.set_ref("span_predictor", span_predictor)

    return model


def span_predictor_init(model: Model, X=None, Y=None):
    if model.layers:
        return

    if X is not None and model.has_dim("nI") is None:
        model.set_dim("nI", get_width(X))

    hidden_size = model.attrs["hidden_size"]
    distance_embedding_size = model.attrs["distance_embedding_size"]
    conv_channels = model.attrs["conv_channels"]
    window_size = model.attrs["window_size"]
    max_distance = model.attrs["max_distance"]

    model._layers = [
        PyTorchWrapper(
            SpanPredictor(
                model.get_dim("nI"),
                hidden_size,
                distance_embedding_size,
                conv_channels,
                window_size,
                max_distance,
            ),
            convert_inputs=convert_span_predictor_inputs,
        )
        # TODO maybe we need mixed precision and grad scaling?
    ]


def span_predictor_forward(model: Model, X, is_train: bool):
    return model.layers[0](X, is_train)


def convert_span_predictor_inputs(
    model: Model,
    X: Tuple[List[Floats2d], Tuple[List[Ints1d], List[Ints1d]]],
    is_train: bool,
):
    tok2vec, (sent_ids, head_ids) = X
    # Normally we should use the input is_train, but for these two it's not relevant
    # TODO fix the type here, or remove it
    def backprop(args: ArgsKwargs) -> Tuple[List[Floats2d], None]:
        gradients = cast(Floats2d, torch2xp(args.args[1]))
        # The sent_ids and head_ids are None because no gradients
        return ([gradients], None)

    word_features = xp2torch(tok2vec[0], requires_grad=is_train)
    sent_ids_tensor = xp2torch(sent_ids[0], requires_grad=False)
    if not head_ids[0].size:
        head_ids_tensor = torch.empty(size=(0,))
    else:
        head_ids_tensor = xp2torch(head_ids[0], requires_grad=False)

    argskwargs = ArgsKwargs(
        args=(sent_ids_tensor, word_features, head_ids_tensor), kwargs={}
    )
    return argskwargs, backprop


def build_get_head_metadata(prefix):
    model = Model(
        "HeadDataProvider", attrs={"prefix": prefix}, forward=head_data_forward
    )
    return model


def head_data_forward(model, docs, is_train):
    """A layer to generate the extra data needed for the span predictor."""
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


# TODO this should maybe have a different name from the component
class SpanPredictor(torch.nn.Module):
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        dist_emb_size: int,
        conv_channels: int,
        window_size: int,
        max_distance: int,
    ):
        super().__init__()
        if max_distance % 2 != 0:
            raise ValueError("max_distance has to be an even number")
        # input size = single token size
        # 64 = probably distance emb size
        self.ffnn = torch.nn.Sequential(
            torch.nn.Linear(input_size * 2 + dist_emb_size, hidden_size),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            # TODO seems weird the 256 isn't a parameter???
            torch.nn.Linear(hidden_size, 256),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            # this use of dist_emb_size looks wrong but it was 64...?
            torch.nn.Linear(256, dist_emb_size),
        )
        kernel_size = window_size * 2 + 1
        self.conv = torch.nn.Sequential(
            torch.nn.Conv1d(dist_emb_size, conv_channels, kernel_size, 1, 1),
            torch.nn.Conv1d(conv_channels, 2, kernel_size, 1, 1),
        )
        self.max_distance = max_distance
        # handle distances between +-(max_distance - 2 / 2)
        self.emb = torch.nn.Embedding(max_distance, dist_emb_size)

    def forward(
        self,
        sent_id,
        words: torch.Tensor,
        heads_ids: torch.Tensor,
    ) -> torch.Tensor:
        """
        Calculates span start/end scores of words for each span
        for each head.

        sent_id: Sentence id of each word.
        words: features for each word in the document.
        heads_ids: word indices of span heads

        Returns:
            torch.Tensor: span start/end scores, (n_heads x n_words x 2)
        """
        # If we don't receive heads, return empty
        device = heads_ids.device
        if heads_ids.nelement() == 0:
            return torch.empty(size=(0,))
        # Obtain distance embedding indices, [n_heads, n_words]
        relative_positions = heads_ids.unsqueeze(1) - torch.arange(
            words.shape[0], device=device
        ).unsqueeze(0)
        md = self.max_distance
        # make all valid distances positive
        emb_ids = relative_positions + (md - 2) // 2
        # "too_far"
        emb_ids[(emb_ids < 0) + (emb_ids > md - 2)] = md - 1
        # Obtain "same sentence" boolean mask: (n_heads x n_words)
        heads_ids = heads_ids.long()
        same_sent = sent_id[heads_ids].unsqueeze(1) == sent_id.unsqueeze(0)
        # To save memory, only pass candidates from one sentence for each head
        # pair_matrix contains concatenated span_head_emb + candidate_emb + distance_emb
        # for each candidate among the words in the same sentence as span_head
        # (n_heads x input_size * 2 x distance_emb_size)
        rows, cols = same_sent.nonzero(as_tuple=True)
        pair_matrix = torch.cat(
            (
                words[heads_ids[rows]],
                words[cols],
                self.emb(emb_ids[rows, cols]),
            ),
            dim=1,
        )
        lengths = same_sent.sum(dim=1)
        padding_mask = torch.arange(0, lengths.max().item(), device=device).unsqueeze(0)
        # (n_heads x max_sent_len)
        padding_mask = padding_mask < lengths.unsqueeze(1)
        # (n_heads x max_sent_len x input_size * 2 + distance_emb_size)
        # This is necessary to allow the convolution layer to look at several
        # word scores
        padded_pairs = torch.zeros(
            *padding_mask.shape, pair_matrix.shape[-1], device=device
        )
        padded_pairs[padding_mask] = pair_matrix
        res = self.ffnn(padded_pairs)  # (n_heads x n_candidates x last_layer_output)
        res = self.conv(res.permute(0, 2, 1)).permute(
            0, 2, 1
        )  # (n_heads x n_candidates, 2)

        scores = torch.full(
            (heads_ids.shape[0], words.shape[0], 2), float("-inf"), device=device
        )
        scores[rows, cols] = res[padding_mask]
        # Make sure that start <= head <= end during inference
        if not self.training:
            valid_starts = torch.log((relative_positions >= 0).to(torch.float))
            valid_ends = torch.log((relative_positions <= 0).to(torch.float))
            valid_positions = torch.stack((valid_starts, valid_ends), dim=2)
            return scores + valid_positions
        return scores
