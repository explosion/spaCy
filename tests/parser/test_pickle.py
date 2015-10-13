import pytest

import pickle
import cloudpickle
import StringIO


@pytest.mark.models
def test_pickle(EN):
    file_ = StringIO.StringIO()
    cloudpickle.dump(EN.parser, file_)

    file_.seek(0)

    loaded = pickle.load(file_)

