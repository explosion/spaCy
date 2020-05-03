"""Thinc layer to do simpler transition-based parsing, NER, etc."""
from typing import List, Tuple, Dict
from thinc.api import Ops, Model
from thinc.types import Padded, Ints1d, Ints3d, Floats3d


def BILUO(labels: List[str]) -> Model[Padded, Padded]:
    return Model(
        "biluo",
        forward,
        init=init,
        dims={"nO": None},
        attrs={"labels": labels}
    )


def init(model, X=None, Y=None):
    n_labels = len(model.attrs["labels"])
    if n_labels == 0:
        raise ValueError("Error initializing BILUO layer: No labels")
    nO = _get_n_actions(n_labels)
    model.set_dim("nO", nO)


def forward(model: Model[Padded, Padded], Xp: Padded, is_train: bool):
    n_labels = len(model.attrs["labels"])
    n_tokens, n_docs, n_actions = Xp.data.shape
    # At each timestep, we make a validity mask of shape (n_docs, n_actions)
    # to indicate which actions are valid next for each sequence. To construct
    # the mask, we have a state of shape (2, n_actions) and a validity table of
    # shape (2, n_actions+1, n_actions). The first dimension of the state indicates
    # whether it's the last token, the second dimension indicates the previous
    # action, plus a special 'null action' for the first entry.
    valid_transitions = _get_transition_table(model.ops, n_labels)
    state = model.ops.alloc2i(2, n_docs)
    actions = model.ops.alloc2i(Xp.data.shape[0], Xp.data.shape[1])
    Y = model.ops.alloc3f(*Xp.data.shape)
    for t in range(Xp.data.shape[0]):
        mask = valid_transitions[state[0], state[1]]
        Y[t] = Xp.data[t] * mask
        actions[t] = Y[t].argmax(axis=-1)
        # TODO: Remove loop :(
        for i, size in enumerate(Xp.size_at_t[t]):
            state[0, size:] = 1
        state[1] = actions[t]

    def backprop(dY: Padded) -> Padded:
        dX = Padded(model.ops.alloc3f(*dY.data.shape), dY.size_at_t, dY.lengths, dY.indices)
        dX.data[actions] = dY.data
        return dX

    return Padded(Y, Xp.size_at_t, Xp.lengths, Xp.indices)

def _get_n_actions(n_labels: int) -> int:
    # One BEGIN action per label
    # One IN action per label
    # One LAST action per label
    # One UNIT action per label
    # One OUT action
    return n_labels + n_labels + n_labels + n_labels + 1


def _get_transition_table(ops: Ops, n_labels: int, _cache: Dict[int, Floats3d]={}) -> Floats3d:
    n_actions = _get_n_actions(n_labels)
    if n_actions in _cache:
        return _cache[n_actions]
    table = ops.alloc3f(2, n_actions+1, n_actions)
    B_start, B_end = (n_labels, n_labels+n_labels)
    I_start, I_end = (B_end, B_end + n_labels)
    L_start, L_end = (I_end, I_end + n_labels)
    U_start, U_end = (I_end, I_end + n_labels)
    # Using ranges allows us to set specific cells, which is necessary to express
    # that only actions of the same label are valid continuations.
    B_range = ops.xp.arange(B_start, B_end)
    I_range = ops.xp.arange(I_start, I_end)
    L_range = ops.xp.arange(L_start, L_end)
    O_action = U_end + 1
    first_action = O_action + 1
    assert first_action == n_actions
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
    # Regardless of whether this is the last token, if the previous action was
    # U or O or none, U and O are valid.
    table[:, U_start:, U_start:] = 1
    return table
