from paddle.trainer.PyDataProvider2 import *
from itertools import izip
import spacy


def get_features(doc):
    return numpy.asarray(
        [t.rank+1 for t in doc
         if t.has_vector and not t.is_punct and not t.is_space],
        dtype='int32')


def read_data(data_dir):
    for subdir, label in (('pos', 1), ('neg', 0)):
        for filename in (data_dir / subdir).iterdir():
            with filename.open() as file_:
                text = file_.read()
                yield text, label


def on_init(settings, **kwargs):
    print("Loading spaCy")
    nlp = spacy.load('en', entity=False)
    vectors = get_vectors(nlp)
    settings.input_types = [
        # The text is a sequence of integer values, and each value is a word id.
        # The whole sequence is the sentences that we want to predict its
        # sentimental.
        integer_value(vectors.shape[0], seq_type=SequenceType),  # text input

        # label positive/negative
        integer_value(2)
    ]
    settings.nlp = nlp
    settings.vectors = vectors
    settings['batch_size'] = 32


@provider(init_hook=on_init)
def process(settings, data_dir):  # settings is not used currently.
    texts, labels = read_data(data_dir)
    for doc, label in izip(nlp.pipe(texts, batch_size=5000, n_threads=3), labels):
        for sent in doc.sents:
            ids = get_features(sent)
            # give data to paddle.
            yield ids, label
