"""Thinc layer to do simpler transition-based parsing, NER, etc."""
from typing import List, Tuple, Dict, Optional
from thinc.api import Ops, Model, with_array, softmax_activation, padded2list
from thinc.types import Padded, Ints1d, Ints3d, Floats2d, Floats3d

from ..tokens import Doc


def BILUO() -> Model[Padded, Padded]:
    return Model(
        "biluo",
        forward,
        init=init,
        dims={"nO": None},
        attrs={"get_num_actions": get_num_actions}
    )


def init(model, X: Optional[Padded]=None, Y: Optional[Padded]=None):
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
    n_labels = (model.get_dim("nO") - 1) // 4
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
    for t in range(Xp.data.shape[0]):
        is_last = (Xp.lengths < (t+2)).astype("i")
        mask = valid_transitions[is_last, prev_actions]
        # Don't train the out-of-bounds sequences.
        mask[Xp.size_at_t[t]:] = 0
        # Valid actions get 0*10e8, invalid get -1*10e8
        Y[t] = Xp.data[t] + ((mask-1) * 10e8)
        prev_actions = Y[t].argmax(axis=-1)

    def backprop_biluo(dY: Padded) -> Padded:
        # Masking the gradient seems to do poorly here. But why?
        return dY

    return Padded(Y, Xp.size_at_t, Xp.lengths, Xp.indices), backprop_biluo


def get_num_actions(n_labels: int) -> int:
    # One BEGIN action per label
    # One IN action per label
    # One LAST action per label
    # One UNIT action per label
    # One OUT action
    return n_labels + n_labels + n_labels + n_labels + 1


def _get_transition_table(
    ops: Ops, n_labels: int, _cache: Dict[int, Floats3d] = {}
) -> Floats3d:
    n_actions = get_num_actions(n_labels)
    if n_actions in _cache:
        return ops.asarray(_cache[n_actions])
    table = ops.alloc3f(2, n_actions, n_actions)
    B_start, B_end = (0, n_labels)
    I_start, I_end = (B_end, B_end + n_labels)
    L_start, L_end = (I_end, I_end + n_labels)
    U_start, U_end = (L_end, L_end + n_labels)
    # Using ranges allows us to set specific cells, which is necessary to express
    # that only actions of the same label are valid continuations.
    B_range = ops.xp.arange(B_start, B_end)
    I_range = ops.xp.arange(I_start, I_end)
    L_range = ops.xp.arange(L_start, L_end)
    O_action = U_end
    # If this is the last token and the previous action was B or I, only L
    # of that label is valid
    table[1, B_range, L_range] = 1
    table[1, I_range, L_range] = 1
    # If this isn't the last token and the previous action was B or I, only I or
    # L of that label are valid.
    table[0, B_range, I_range] = 1
    table[0, B_range, L_range] = 1
    table[0, I_range, I_range] = 1
    table[0, I_range, L_range] = 1
    # If this isn't the last token and the previous was L, U or O, B is valid
    table[0, L_start:, :B_end] = 1
    # Regardless of whether this is the last token, if the previous action was
    # {L, U, O}, U and O are valid.
    table[:, L_start:, U_start:] = 1
    _cache[n_actions] = table
    return table
