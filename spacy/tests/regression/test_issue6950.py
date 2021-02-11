from spacy.lang.en import English
from spacy.training import Example
from spacy.util import load_config_from_str
import pickle


CONFIG = """
[nlp]
lang = "en"
pipeline = ["tok2vec", "tagger"]

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v1"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = ${components.tok2vec.model.encode:width}
attrs = ["NORM","PREFIX","SUFFIX","SHAPE"]
rows = [5000,2500,2500,2500]
include_static_vectors = false

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v1"
width = 96
depth = 4
window_size = 1
maxout_pieces = 3

[components.ner]
factory = "ner"

[components.tagger]
factory = "tagger"

[components.tagger.model]
@architectures = "spacy.Tagger.v1"
nO = null

[components.tagger.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.encode:width}
upstream = "*"
"""


def test_issue6950():
    """Test that the nlp object with initialized tok2vec with listeners pickles
    correctly (and doesn't have lambdas).
    """
    nlp = English.from_config(load_config_from_str(CONFIG))
    nlp.initialize(lambda: [Example.from_dict(nlp.make_doc("hello"), {"tags": ["V"]})])
    pickle.dumps(nlp)
    nlp("hello")
    pickle.dumps(nlp)
