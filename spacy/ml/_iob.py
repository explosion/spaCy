"""Thinc layer to do simpler transition-based parsing, NER, etc."""
from typing import Dict, Optional
from thinc.api import Ops, Model
from thinc.types import Padded, Floats3d


def IOB() -> Model[Padded, Padded]:
    return Model(
        "biluo",
        forward,
        init=init,
        dims={"nO": None},
        attrs={"get_num_actions": get_num_actions},
    )


def init(model, X: Optional[Padded] = None, Y: Optional[Padded] = None):
    if X is not None and Y is not None:
        if X.data.shape != Y.data.shape:
            # TODO: Fix error
            raise ValueError("Mismatched shapes (TODO: Fix message)")
        model.set_dim("nO", X.data.shape[2])
    elif X is not None:
        model.set_dim("nO", X.data.shape[2])
    elif Y is not None:
        model.set_dim("nO", Y.data.shape[2])
    elif model.get_dim("nO") is None:
        raise ValueError("Dimension unset for BILUO: nO")


def forward(model: Model[Padded, Padded], Xp: Padded, is_train: bool):
    n_labels = (model.get_dim("nO") - 1) // 2
    n_tokens, n_docs, n_actions = Xp.data.shape
    # At each timestep, we make a validity mask of shape (n_docs, n_actions)
    # to indicate which actions are valid next for each sequence. To construct
    # the mask, we have a state of shape (2, n_actions) and a validity table of
    # shape (2, n_actions+1, n_actions). The first dimension of the state indicates
    # whether it's the last token, the second dimension indicates the previous
    # action, plus a special 'null action' for the first entry.
    valid_transitions = _get_transition_table(model.ops, n_labels)
    prev_actions = model.ops.alloc1i(n_docs)
    # Initialize as though prev action was O
    prev_actions.fill(n_actions - 1)
    Y = model.ops.alloc3f(*Xp.data.shape)
    masks = model.ops.alloc3f(*Y.shape)
    for t in range(Xp.data.shape[0]):
        masks[t] = valid_transitions[prev_actions]
        # Don't train the out-of-bounds sequences.
        masks[t, Xp.size_at_t[t] :] = 0
        # Valid actions get 0*10e8, invalid get -1*10e8
        Y[t] = Xp.data[t] + ((masks[t] - 1) * 10e8)
        prev_actions = Y[t].argmax(axis=-1)

    def backprop_biluo(dY: Padded) -> Padded:
        # Masking the gradient seems to do poorly here. But why?
        # dY.data *= masks
        return dY

    return Padded(Y, Xp.size_at_t, Xp.lengths, Xp.indices), backprop_biluo


def get_num_actions(n_labels: int) -> int:
    # One BEGIN action per label
    # One IN action per label
    # One LAST action per label
    # One UNIT action per label
    # One OUT action
    return n_labels * 2 + 1


def _get_transition_table(
    ops: Ops, n_labels: int, _cache: Dict[int, Floats3d] = {}
) -> Floats3d:
    n_actions = get_num_actions(n_labels)
    if n_actions in _cache:
        return ops.asarray(_cache[n_actions])
    table = ops.alloc2f(n_actions, n_actions)
    B_start, B_end = (0, n_labels)
    I_start, I_end = (B_end, B_end + n_labels)
    O_action = I_end
    B_range = ops.xp.arange(B_start, B_end)
    I_range = ops.xp.arange(I_start, I_end)
    # B and O are always valid
    table[:, B_start:B_end] = 1
    table[:, O_action] = 1
    # I can only follow a matching B
    table[B_range, I_range] = 1

    _cache[n_actions] = table
    return table
