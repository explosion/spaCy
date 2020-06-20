import pytest
from collections import namedtuple
from thinc.api import NumpyOps
from spacy.ml._biluo import BILUO, _get_transition_table


@pytest.fixture(
    params=[
        ["PER", "ORG", "LOC", "MISC"],
        ["GPE", "PERSON", "NUMBER", "CURRENCY", "EVENT"],
    ]
)
def labels(request):
    return request.param


@pytest.fixture
def ops():
    return NumpyOps()


def _get_actions(labels):
    action_names = (
        [f"B{label}" for label in labels]
        + [f"I{label}" for label in labels]
        + [f"L{label}" for label in labels]
        + [f"U{label}" for label in labels]
        + ["O"]
    )
    A = namedtuple("actions", action_names)
    return A(**{name: i for i, name in enumerate(action_names)})


def test_init_biluo_layer(labels):
    model = BILUO()
    model.set_dim("nO", model.attrs["get_num_actions"](len(labels)))
    model.initialize()
    assert model.get_dim("nO") == len(labels) * 4 + 1


def test_transition_table(ops):
    labels = ["per", "loc", "org"]
    table = _get_transition_table(len(labels))
    a = _get_actions(labels)
    assert table.shape == (2, len(a), len(a))
    # Not last token, prev action was B
    assert table[0, a.Bper, a.Bper] == 0
    assert table[0, a.Bper, a.Bloc] == 0
    assert table[0, a.Bper, a.Borg] == 0
    assert table[0, a.Bper, a.Iper] == 1
    assert table[0, a.Bper, a.Iloc] == 0
    assert table[0, a.Bper, a.Iorg] == 0
    assert table[0, a.Bper, a.Lper] == 1
    assert table[0, a.Bper, a.Lloc] == 0
    assert table[0, a.Bper, a.Lorg] == 0
    assert table[0, a.Bper, a.Uper] == 0
    assert table[0, a.Bper, a.Uloc] == 0
    assert table[0, a.Bper, a.Uorg] == 0
    assert table[0, a.Bper, a.O] == 0

    assert table[0, a.Bloc, a.Bper] == 0
    assert table[0, a.Bloc, a.Bloc] == 0
    assert table[0, a.Bloc, a.Borg] == 0
    assert table[0, a.Bloc, a.Iper] == 0
    assert table[0, a.Bloc, a.Iloc] == 1
    assert table[0, a.Bloc, a.Iorg] == 0
    assert table[0, a.Bloc, a.Lper] == 0
    assert table[0, a.Bloc, a.Lloc] == 1
    assert table[0, a.Bloc, a.Lorg] == 0
    assert table[0, a.Bloc, a.Uper] == 0
    assert table[0, a.Bloc, a.Uloc] == 0
    assert table[0, a.Bloc, a.Uorg] == 0
    assert table[0, a.Bloc, a.O] == 0

    assert table[0, a.Borg, a.Bper] == 0
    assert table[0, a.Borg, a.Bloc] == 0
    assert table[0, a.Borg, a.Borg] == 0
    assert table[0, a.Borg, a.Iper] == 0
    assert table[0, a.Borg, a.Iloc] == 0
    assert table[0, a.Borg, a.Iorg] == 1
    assert table[0, a.Borg, a.Lper] == 0
    assert table[0, a.Borg, a.Lloc] == 0
    assert table[0, a.Borg, a.Lorg] == 1
    assert table[0, a.Borg, a.Uper] == 0
    assert table[0, a.Borg, a.Uloc] == 0
    assert table[0, a.Borg, a.Uorg] == 0
    assert table[0, a.Borg, a.O] == 0

    # Not last token, prev action was I
    assert table[0, a.Iper, a.Bper] == 0
    assert table[0, a.Iper, a.Bloc] == 0
    assert table[0, a.Iper, a.Borg] == 0
    assert table[0, a.Iper, a.Iper] == 1
    assert table[0, a.Iper, a.Iloc] == 0
    assert table[0, a.Iper, a.Iorg] == 0
    assert table[0, a.Iper, a.Lper] == 1
    assert table[0, a.Iper, a.Lloc] == 0
    assert table[0, a.Iper, a.Lorg] == 0
    assert table[0, a.Iper, a.Uper] == 0
    assert table[0, a.Iper, a.Uloc] == 0
    assert table[0, a.Iper, a.Uorg] == 0
    assert table[0, a.Iper, a.O] == 0

    assert table[0, a.Iloc, a.Bper] == 0
    assert table[0, a.Iloc, a.Bloc] == 0
    assert table[0, a.Iloc, a.Borg] == 0
    assert table[0, a.Iloc, a.Iper] == 0
    assert table[0, a.Iloc, a.Iloc] == 1
    assert table[0, a.Iloc, a.Iorg] == 0
    assert table[0, a.Iloc, a.Lper] == 0
    assert table[0, a.Iloc, a.Lloc] == 1
    assert table[0, a.Iloc, a.Lorg] == 0
    assert table[0, a.Iloc, a.Uper] == 0
    assert table[0, a.Iloc, a.Uloc] == 0
    assert table[0, a.Iloc, a.Uorg] == 0
    assert table[0, a.Iloc, a.O] == 0

    assert table[0, a.Iorg, a.Bper] == 0
    assert table[0, a.Iorg, a.Bloc] == 0
    assert table[0, a.Iorg, a.Borg] == 0
    assert table[0, a.Iorg, a.Iper] == 0
    assert table[0, a.Iorg, a.Iloc] == 0
    assert table[0, a.Iorg, a.Iorg] == 1
    assert table[0, a.Iorg, a.Lper] == 0
    assert table[0, a.Iorg, a.Lloc] == 0
    assert table[0, a.Iorg, a.Lorg] == 1
    assert table[0, a.Iorg, a.Uper] == 0
    assert table[0, a.Iorg, a.Uloc] == 0
    assert table[0, a.Iorg, a.Uorg] == 0
    assert table[0, a.Iorg, a.O] == 0

    # Not last token, prev action was L
    assert table[0, a.Lper, a.Bper] == 1
    assert table[0, a.Lper, a.Bloc] == 1
    assert table[0, a.Lper, a.Borg] == 1
    assert table[0, a.Lper, a.Iper] == 0
    assert table[0, a.Lper, a.Iloc] == 0
    assert table[0, a.Lper, a.Iorg] == 0
    assert table[0, a.Lper, a.Lper] == 0
    assert table[0, a.Lper, a.Lloc] == 0
    assert table[0, a.Lper, a.Lorg] == 0
    assert table[0, a.Lper, a.Uper] == 1
    assert table[0, a.Lper, a.Uloc] == 1
    assert table[0, a.Lper, a.Uorg] == 1
    assert table[0, a.Lper, a.O] == 1

    assert table[0, a.Lloc, a.Bper] == 1
    assert table[0, a.Lloc, a.Bloc] == 1
    assert table[0, a.Lloc, a.Borg] == 1
    assert table[0, a.Lloc, a.Iper] == 0
    assert table[0, a.Lloc, a.Iloc] == 0
    assert table[0, a.Lloc, a.Iorg] == 0
    assert table[0, a.Lloc, a.Lper] == 0
    assert table[0, a.Lloc, a.Lloc] == 0
    assert table[0, a.Lloc, a.Lorg] == 0
    assert table[0, a.Lloc, a.Uper] == 1
    assert table[0, a.Lloc, a.Uloc] == 1
    assert table[0, a.Lloc, a.Uorg] == 1
    assert table[0, a.Lloc, a.O] == 1

    assert table[0, a.Lorg, a.Bper] == 1
    assert table[0, a.Lorg, a.Bloc] == 1
    assert table[0, a.Lorg, a.Borg] == 1
    assert table[0, a.Lorg, a.Iper] == 0
    assert table[0, a.Lorg, a.Iloc] == 0
    assert table[0, a.Lorg, a.Iorg] == 0
    assert table[0, a.Lorg, a.Lper] == 0
    assert table[0, a.Lorg, a.Lloc] == 0
    assert table[0, a.Lorg, a.Lorg] == 0
    assert table[0, a.Lorg, a.Uper] == 1
    assert table[0, a.Lorg, a.Uloc] == 1
    assert table[0, a.Lorg, a.Uorg] == 1
    assert table[0, a.Lorg, a.O] == 1

    # Not last token, prev action was U
    assert table[0, a.Uper, a.Bper] == 1
    assert table[0, a.Uper, a.Bloc] == 1
    assert table[0, a.Uper, a.Borg] == 1
    assert table[0, a.Uper, a.Iper] == 0
    assert table[0, a.Uper, a.Iloc] == 0
    assert table[0, a.Uper, a.Iorg] == 0
    assert table[0, a.Uper, a.Lper] == 0
    assert table[0, a.Uper, a.Lloc] == 0
    assert table[0, a.Uper, a.Lorg] == 0
    assert table[0, a.Uper, a.Uper] == 1
    assert table[0, a.Uper, a.Uloc] == 1
    assert table[0, a.Uper, a.Uorg] == 1
    assert table[0, a.Uper, a.O] == 1

    assert table[0, a.Uloc, a.Bper] == 1
    assert table[0, a.Uloc, a.Bloc] == 1
    assert table[0, a.Uloc, a.Borg] == 1
    assert table[0, a.Uloc, a.Iper] == 0
    assert table[0, a.Uloc, a.Iloc] == 0
    assert table[0, a.Uloc, a.Iorg] == 0
    assert table[0, a.Uloc, a.Lper] == 0
    assert table[0, a.Uloc, a.Lloc] == 0
    assert table[0, a.Uloc, a.Lorg] == 0
    assert table[0, a.Uloc, a.Uper] == 1
    assert table[0, a.Uloc, a.Uloc] == 1
    assert table[0, a.Uloc, a.Uorg] == 1
    assert table[0, a.Uloc, a.O] == 1

    assert table[0, a.Uorg, a.Bper] == 1
    assert table[0, a.Uorg, a.Bloc] == 1
    assert table[0, a.Uorg, a.Borg] == 1
    assert table[0, a.Uorg, a.Iper] == 0
    assert table[0, a.Uorg, a.Iloc] == 0
    assert table[0, a.Uorg, a.Iorg] == 0
    assert table[0, a.Uorg, a.Lper] == 0
    assert table[0, a.Uorg, a.Lloc] == 0
    assert table[0, a.Uorg, a.Lorg] == 0
    assert table[0, a.Uorg, a.Uper] == 1
    assert table[0, a.Uorg, a.Uloc] == 1
    assert table[0, a.Uorg, a.Uorg] == 1
    assert table[0, a.Uorg, a.O] == 1

    # Not last token, prev action was O
    assert table[0, a.O, a.Bper] == 1
    assert table[0, a.O, a.Bloc] == 1
    assert table[0, a.O, a.Borg] == 1
    assert table[0, a.O, a.Iper] == 0
    assert table[0, a.O, a.Iloc] == 0
    assert table[0, a.O, a.Iorg] == 0
    assert table[0, a.O, a.Lper] == 0
    assert table[0, a.O, a.Lloc] == 0
    assert table[0, a.O, a.Lorg] == 0
    assert table[0, a.O, a.Uper] == 1
    assert table[0, a.O, a.Uloc] == 1
    assert table[0, a.O, a.Uorg] == 1
    assert table[0, a.O, a.O] == 1

    # Last token, prev action was B
    assert table[1, a.Bper, a.Bper] == 0
    assert table[1, a.Bper, a.Bloc] == 0
    assert table[1, a.Bper, a.Borg] == 0
    assert table[1, a.Bper, a.Iper] == 0
    assert table[1, a.Bper, a.Iloc] == 0
    assert table[1, a.Bper, a.Iorg] == 0
    assert table[1, a.Bper, a.Lper] == 1
    assert table[1, a.Bper, a.Lloc] == 0
    assert table[1, a.Bper, a.Lorg] == 0
    assert table[1, a.Bper, a.Uper] == 0
    assert table[1, a.Bper, a.Uloc] == 0
    assert table[1, a.Bper, a.Uorg] == 0
    assert table[1, a.Bper, a.O] == 0

    assert table[1, a.Bloc, a.Bper] == 0
    assert table[1, a.Bloc, a.Bloc] == 0
    assert table[0, a.Bloc, a.Borg] == 0
    assert table[1, a.Bloc, a.Iper] == 0
    assert table[1, a.Bloc, a.Iloc] == 0
    assert table[1, a.Bloc, a.Iorg] == 0
    assert table[1, a.Bloc, a.Lper] == 0
    assert table[1, a.Bloc, a.Lloc] == 1
    assert table[1, a.Bloc, a.Lorg] == 0
    assert table[1, a.Bloc, a.Uper] == 0
    assert table[1, a.Bloc, a.Uloc] == 0
    assert table[1, a.Bloc, a.Uorg] == 0
    assert table[1, a.Bloc, a.O] == 0

    assert table[1, a.Borg, a.Bper] == 0
    assert table[1, a.Borg, a.Bloc] == 0
    assert table[1, a.Borg, a.Borg] == 0
    assert table[1, a.Borg, a.Iper] == 0
    assert table[1, a.Borg, a.Iloc] == 0
    assert table[1, a.Borg, a.Iorg] == 0
    assert table[1, a.Borg, a.Lper] == 0
    assert table[1, a.Borg, a.Lloc] == 0
    assert table[1, a.Borg, a.Lorg] == 1
    assert table[1, a.Borg, a.Uper] == 0
    assert table[1, a.Borg, a.Uloc] == 0
    assert table[1, a.Borg, a.Uorg] == 0
    assert table[1, a.Borg, a.O] == 0

    # Last token, prev action was I
    assert table[1, a.Iper, a.Bper] == 0
    assert table[1, a.Iper, a.Bloc] == 0
    assert table[1, a.Iper, a.Borg] == 0
    assert table[1, a.Iper, a.Iper] == 0
    assert table[1, a.Iper, a.Iloc] == 0
    assert table[1, a.Iper, a.Iorg] == 0
    assert table[1, a.Iper, a.Lper] == 1
    assert table[1, a.Iper, a.Lloc] == 0
    assert table[1, a.Iper, a.Lorg] == 0
    assert table[1, a.Iper, a.Uper] == 0
    assert table[1, a.Iper, a.Uloc] == 0
    assert table[1, a.Iper, a.Uorg] == 0
    assert table[1, a.Iper, a.O] == 0

    assert table[1, a.Iloc, a.Bper] == 0
    assert table[1, a.Iloc, a.Bloc] == 0
    assert table[1, a.Iloc, a.Borg] == 0
    assert table[1, a.Iloc, a.Iper] == 0
    assert table[1, a.Iloc, a.Iloc] == 0
    assert table[1, a.Iloc, a.Iorg] == 0
    assert table[1, a.Iloc, a.Lper] == 0
    assert table[1, a.Iloc, a.Lloc] == 1
    assert table[1, a.Iloc, a.Lorg] == 0
    assert table[1, a.Iloc, a.Uper] == 0
    assert table[1, a.Iloc, a.Uloc] == 0
    assert table[1, a.Iloc, a.Uorg] == 0
    assert table[1, a.Iloc, a.O] == 0

    assert table[1, a.Iorg, a.Bper] == 0
    assert table[1, a.Iorg, a.Bloc] == 0
    assert table[1, a.Iorg, a.Borg] == 0
    assert table[1, a.Iorg, a.Iper] == 0
    assert table[1, a.Iorg, a.Iloc] == 0
    assert table[1, a.Iorg, a.Iorg] == 0
    assert table[1, a.Iorg, a.Lper] == 0
    assert table[1, a.Iorg, a.Lloc] == 0
    assert table[1, a.Iorg, a.Lorg] == 1
    assert table[1, a.Iorg, a.Uper] == 0
    assert table[1, a.Iorg, a.Uloc] == 0
    assert table[1, a.Iorg, a.Uorg] == 0
    assert table[1, a.Iorg, a.O] == 0

    # Last token, prev action was L
    assert table[1, a.Lper, a.Bper] == 0
    assert table[1, a.Lper, a.Bloc] == 0
    assert table[1, a.Lper, a.Borg] == 0
    assert table[1, a.Lper, a.Iper] == 0
    assert table[1, a.Lper, a.Iloc] == 0
    assert table[1, a.Lper, a.Iorg] == 0
    assert table[1, a.Lper, a.Lper] == 0
    assert table[1, a.Lper, a.Lloc] == 0
    assert table[1, a.Lper, a.Lorg] == 0
    assert table[1, a.Lper, a.Uper] == 1
    assert table[1, a.Lper, a.Uloc] == 1
    assert table[1, a.Lper, a.Uorg] == 1
    assert table[1, a.Lper, a.O] == 1

    assert table[1, a.Lloc, a.Bper] == 0
    assert table[1, a.Lloc, a.Bloc] == 0
    assert table[1, a.Lloc, a.Borg] == 0
    assert table[1, a.Lloc, a.Iper] == 0
    assert table[1, a.Lloc, a.Iloc] == 0
    assert table[1, a.Lloc, a.Iorg] == 0
    assert table[1, a.Lloc, a.Lper] == 0
    assert table[1, a.Lloc, a.Lloc] == 0
    assert table[1, a.Lloc, a.Lorg] == 0
    assert table[1, a.Lloc, a.Uper] == 1
    assert table[1, a.Lloc, a.Uloc] == 1
    assert table[1, a.Lloc, a.Uorg] == 1
    assert table[1, a.Lloc, a.O] == 1

    assert table[1, a.Lorg, a.Bper] == 0
    assert table[1, a.Lorg, a.Bloc] == 0
    assert table[1, a.Lorg, a.Borg] == 0
    assert table[1, a.Lorg, a.Iper] == 0
    assert table[1, a.Lorg, a.Iloc] == 0
    assert table[1, a.Lorg, a.Iorg] == 0
    assert table[1, a.Lorg, a.Lper] == 0
    assert table[1, a.Lorg, a.Lloc] == 0
    assert table[1, a.Lorg, a.Lorg] == 0
    assert table[1, a.Lorg, a.Uper] == 1
    assert table[1, a.Lorg, a.Uloc] == 1
    assert table[1, a.Lorg, a.Uorg] == 1
    assert table[1, a.Lorg, a.O] == 1

    # Last token, prev action was U
    assert table[1, a.Uper, a.Bper] == 0
    assert table[1, a.Uper, a.Bloc] == 0
    assert table[1, a.Uper, a.Borg] == 0
    assert table[1, a.Uper, a.Iper] == 0
    assert table[1, a.Uper, a.Iloc] == 0
    assert table[1, a.Uper, a.Iorg] == 0
    assert table[1, a.Uper, a.Lper] == 0
    assert table[1, a.Uper, a.Lloc] == 0
    assert table[1, a.Uper, a.Lorg] == 0
    assert table[1, a.Uper, a.Uper] == 1
    assert table[1, a.Uper, a.Uloc] == 1
    assert table[1, a.Uper, a.Uorg] == 1
    assert table[1, a.Uper, a.O] == 1

    assert table[1, a.Uloc, a.Bper] == 0
    assert table[1, a.Uloc, a.Bloc] == 0
    assert table[1, a.Uloc, a.Borg] == 0
    assert table[1, a.Uloc, a.Iper] == 0
    assert table[1, a.Uloc, a.Iloc] == 0
    assert table[1, a.Uloc, a.Iorg] == 0
    assert table[1, a.Uloc, a.Lper] == 0
    assert table[1, a.Uloc, a.Lloc] == 0
    assert table[1, a.Uloc, a.Lorg] == 0
    assert table[1, a.Uloc, a.Uper] == 1
    assert table[1, a.Uloc, a.Uloc] == 1
    assert table[1, a.Uloc, a.Uorg] == 1
    assert table[1, a.Uloc, a.O] == 1

    assert table[1, a.Uorg, a.Bper] == 0
    assert table[1, a.Uorg, a.Bloc] == 0
    assert table[1, a.Uorg, a.Borg] == 0
    assert table[1, a.Uorg, a.Iper] == 0
    assert table[1, a.Uorg, a.Iloc] == 0
    assert table[1, a.Uorg, a.Iorg] == 0
    assert table[1, a.Uorg, a.Lper] == 0
    assert table[1, a.Uorg, a.Lloc] == 0
    assert table[1, a.Uorg, a.Lorg] == 0
    assert table[1, a.Uorg, a.Uper] == 1
    assert table[1, a.Uorg, a.Uloc] == 1
    assert table[1, a.Uorg, a.Uorg] == 1
    assert table[1, a.Uorg, a.O] == 1

    # Last token, prev action was O
    assert table[1, a.O, a.Bper] == 0
    assert table[1, a.O, a.Bloc] == 0
    assert table[1, a.O, a.Borg] == 0
    assert table[1, a.O, a.Iper] == 0
    assert table[1, a.O, a.Iloc] == 0
    assert table[1, a.O, a.Iorg] == 0
    assert table[1, a.O, a.Lper] == 0
    assert table[1, a.O, a.Lloc] == 0
    assert table[1, a.O, a.Lorg] == 0
    assert table[1, a.O, a.Uper] == 1
    assert table[1, a.O, a.Uloc] == 1
    assert table[1, a.O, a.Uorg] == 1
    assert table[1, a.O, a.O] == 1
