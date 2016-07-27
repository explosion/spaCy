import cloudpickle
import io
import os
import pickle
import pytest
import tempfile

try:
    unicode
except NameError:
    unicode = str

# These cause the addition of temp files, that are then not deleted
#@pytest.mark.models
#def test_pickle_english(EN):
#    file_ = io.BytesIO()
#    cloudpickle.dump(EN, file_)
#
#    file_.seek(0)
#
#    loaded = pickle.load(file_)
#    assert loaded is not None
#
#@pytest.mark.models
#def test_cloudpickle_to_file(EN):
#    f = tempfile.NamedTemporaryFile(delete=False)
#    p = cloudpickle.CloudPickler(f)
#    p.dump(EN)
#    f.close()
#    loaded_en = cloudpickle.load(open(f.name, 'rb'))
#    os.unlink(f.name)
#    doc = loaded_en(unicode('test parse'))
#    assert len(doc) == 2
