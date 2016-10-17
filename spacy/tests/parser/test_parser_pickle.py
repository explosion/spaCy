import pytest

import pickle
import cloudpickle

import io


#@pytest.mark.models
#def test_pickle(EN):
#    file_ = io.BytesIO()
#    cloudpickle.dump(EN.parser, file_)
#
#    file_.seek(0)
#
#    loaded = pickle.load(file_)
#
