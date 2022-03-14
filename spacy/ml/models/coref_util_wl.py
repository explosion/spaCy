""" Contains functions not directly linked to coreference resolution """

from typing import List, Set, Dict, Tuple
from thinc.types import Ints1d
from dataclasses import dataclass
from ...tokens import Doc

import torch

EPSILON = 1e-7

class GraphNode:
    def __init__(self, node_id: int):
        self.id = node_id
        self.links: Set[GraphNode] = set()
        self.visited = False

    def link(self, another: "GraphNode"):
        self.links.add(another)
        another.links.add(self)

    def __repr__(self) -> str:
        return str(self.id)


def add_dummy(tensor: torch.Tensor, eps: bool = False):
    """ Prepends zeros (or a very small value if eps is True)
    to the first (not zeroth) dimension of tensor.
    """
    kwargs = dict(device=tensor.device, dtype=tensor.dtype)
    shape: List[int] = list(tensor.shape)
    shape[1] = 1
    if not eps:
        dummy = torch.zeros(shape, **kwargs)          # type: ignore
    else:
        dummy = torch.full(shape, EPSILON, **kwargs)  # type: ignore
    output = torch.cat((dummy, tensor), dim=1)
    return output

def make_head_only_clusters(examples):
    """Replace coref clusters with head-only clusters.

    This destructively modifies the docs.
    """

    #TODO what if all clusters are eliminated?
    for eg in examples:
        final = [] # save out clusters here
        for key, sg in eg.reference.spans.items():
            if not key.startswith("coref_clusters_"):
                continue

            heads = [span.root.i for span in sg]
            heads = list(set(heads))
            head_spans = [eg.reference[hh:hh+1] for hh in heads]
            if len(heads) > 1:
                final.append(head_spans)

        # now delete the existing clusters
        keys = list(eg.reference.spans.keys())
        for key in keys:
            if not key.startswith("coref_clusters_"):
                continue

            del eg.reference.spans[key]

        # now add the new spangroups
        for ii, spans in enumerate(final):
            #TODO support alternate keys
            eg.reference.spans[f"coref_clusters_{ii}"] = spans

# TODO replace with spaCy config
@dataclass
class CorefConfig:  # pylint: disable=too-many-instance-attributes, too-few-public-methods
    """ Contains values needed to set up the coreference model. """
    section: str

    data_dir: str

    train_data: str
    dev_data: str
    test_data: str

    device: str

    bert_model: str
    bert_window_size: int

    embedding_size: int
    sp_embedding_size: int
    a_scoring_batch_size: int
    hidden_size: int
    n_hidden_layers: int

    max_span_len: int

    rough_k: int

    bert_finetune: bool
    bert_mini_finetune: bool
    dropout_rate: float
    learning_rate: float
    bert_learning_rate: float
    train_epochs: int
    bce_loss_weight: float

    tokenizer_kwargs: Dict[str, dict]
    conll_log_dir: str


def get_sent_ids(doc):
    sid = 0
    sids = []
    for sent in doc.sents:
        for tok in sent:
            sids.append(sid)
        sid += 1
    return sids

def get_cluster_ids(doc):
    """Get the cluster ids of head tokens."""

    out = [0] * len(doc)
    head_spangroups = [doc.spans[sk] for sk in doc.spans if sk.startswith("coref_word_clusters")]
    for ii, group in enumerate(head_spangroups, start=1):
        for span in group:
            out[span[0].i] = ii

    return out

def get_head2span(doc):
    out = []
    for sk in doc.spans:
        if not sk.startswith("coref_clusters"):
            continue

        if len(doc.spans[sk]) == 1:
            print("===== UNARY MENTION ====")

        for span in doc.spans[sk]:
            out.append( (span.root.i, span.start, span.end) )
    return out


def doc2tensors(
    xp,
    doc: Doc
) -> Tuple[Ints1d, Ints1d, Ints1d, Ints1d, Ints1d]:
    sent_ids = get_sent_ids(doc)
    cluster_ids = get_cluster_ids(doc)
    head2span = get_head2span(doc)


    if not head2span:
        heads, starts, ends = [], [], []
    else:
        heads, starts, ends = zip(*head2span)
    sent_ids = xp.asarray(sent_ids)
    cluster_ids = xp.asarray(cluster_ids)
    heads = xp.asarray(heads)
    starts = xp.asarray(starts)
    ends = xp.asarray(ends) - 1
    return sent_ids, cluster_ids, heads, starts, ends
