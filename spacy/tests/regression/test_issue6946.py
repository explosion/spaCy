import spacy
from spacy import util
from spacy.tokens import DocBin
from spacy.training.initialize import init_nlp

from ..util import make_tempdir

TRANSF_TEXTCAT_ENSEMBLE_CONFIG = """
[paths]
train = "TRAIN_PLACEHOLDER"
raw = null
init_tok2vec = null
vectors = null

[system]
seed = 0
gpu_allocator = null

[nlp]
lang = "en"
pipeline = ["transformer","textcat"]
tokenizer = {"@tokenizers":"spacy.Tokenizer.v1"}
disabled = []
before_creation = null
after_creation = null
after_pipeline_creation = null
batch_size = 32

[components]

[components.transformer]
factory = "transformer"

[components.transformer.model]
@architectures = "spacy-transformers.TransformerModel.v1"
name = "roberta-base"
tokenizer_config = {"use_fast": true}

[components.transformer.model.get_spans]
@span_getters = "spacy-transformers.strided_spans.v1"
window = 128
stride = 96

[components.textcat]
factory = "textcat_multilabel"
threshold = 0.5

[components.textcat.model]
@architectures = "spacy.TextCatEnsemble.v2"
nO = null

[components.textcat.model.tok2vec]
@architectures = "spacy-transformers.TransformerListener.v1"
grad_factor = 1.0
pooling = {"@layers":"reduce_mean.v1"}
upstream = "*"

[components.textcat.model.linear_model]
@architectures = "spacy.TextCatBOW.v1"
exclusive_classes = false
ngram_size = 1
no_output_layer = false

[corpora]

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths:train}

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths:train}


[training]
train_corpus = "corpora.train"
dev_corpus = "corpora.dev"
seed = ${system.seed}
gpu_allocator = ${system.gpu_allocator}
frozen_components = []
before_to_disk = null

[pretraining]

[initialize]
vectors = ${paths.vectors}
init_tok2vec = ${paths.init_tok2vec}
vocab_data = null
lookups = null
before_init = null
after_init = null

[initialize.components]

[initialize.components.textcat]
labels = ['label1', 'label2']

[initialize.tokenizer]
"""


def test_textcat_ensemble_transform_listener():
    """Test intializing `spacy.TextCatEnsemble.v2`
    using `spacy-transformers.TransformerListener.v1`
    """

    def create_data(out_file):
        nlp = spacy.blank("en")
        doc = nlp.make_doc("Some text")
        doc.cats = {"label1": 0, "label2": 1}

        out_data = DocBin(docs=[doc]).to_bytes()
        with out_file.open("wb") as file_:
            file_.write(out_data)

    with make_tempdir() as tmp_path:
        train_path = tmp_path / "train.spacy"
        create_data(train_path)

        config_str = TRANSF_TEXTCAT_ENSEMBLE_CONFIG.replace(
            "TRAIN_PLACEHOLDER", train_path.as_posix()
        )

        config = util.load_config_from_str(config_str)
        init_nlp(config)
