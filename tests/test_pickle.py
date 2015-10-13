import pytest
import StringIO
import cloudpickle
import pickle


@pytest.mark.models
def test_pickle_english(EN):
    file_ = StringIO.StringIO()
    cloudpickle.dump(EN, file_)

    file_.seek(0)

    loaded = pickle.load(file_)

