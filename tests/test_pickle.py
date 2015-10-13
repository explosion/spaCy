import pytest
import io
import cloudpickle
import pickle


@pytest.mark.models
def test_pickle_english(EN):
    file_ = io.BytesIO()
    cloudpickle.dump(EN, file_)

    file_.seek(0)

    loaded = pickle.load(file_)

