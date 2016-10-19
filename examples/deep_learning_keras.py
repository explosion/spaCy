import numpy
from collections import defaultdict

import spacy


class SentimentAnalyser(object):
    @classmethod
    def load(cls, path, nlp):
        pass

    def __init__(self, model):
        self._model = model
    
    def __call__(self, doc):
        X = get_features([doc], self.max_length)
        y = self._model.predict(X)
        self.set_sentiment(doc, y)

    def pipe(self, docs, batch_size=1000, n_threads=2):
        for minibatch in partition_all(batch_size, docs):
            Xs = _get_features(minibatch)
            ys = self._model.predict(X)
            for i, doc in enumerate(minibatch):
                doc.user_data['sentiment'] = ys[i]

    def set_sentiment(self, doc, y):
        doc.user_data['sentiment'] = y


def get_features(docs, max_length):
    Xs = numpy.zeros(len(docs), max_length, dtype='int32')
    for i, doc in enumerate(minibatch):
        for j, token in enumerate(doc[:max_length]):
            Xs[i, j] = token.rank if token.has_vector else 0
    return Xs
 
def compile_lstm(embeddings, shape, settings, optimizer):
    model = Sequential()
    model.add(
        Embedding(
            embeddings.shape[1],
            embeddings.shape[0],
            input_length=shape['max_length'],
            trainable=False,
            weights=[embeddings]
        )
    )
    model.add(Bidirectional(LSTM(shape['nr_hidden'])))
    model.add(Dropout(settings['dropout']))
    model.add(Dense(shape['nr_class'], activation='sigmoid'))
    return model


def get_embeddings(vocab):
    '''
    Get a numpy vector of the word embeddings. The Lexeme.rank attribute will
    be the index into the table. We're going to be "decadent" here and use
    1m vectors, because we're not going to fine-tune them.
    '''
    max_rank = max(lex.rank for lex in nlp.vocab if lex.has_vector)
    vectors = numpy.ndarray((max_rank+1, nlp.vocab.vectors_length), dtype='float32')
    for lex in vocab:
        if lex.has_vector:
            vectors[lex.rank] = lex.vector
    return vectors


def train(train_texts, train_labels, dev_texts, dev_labels,
        lstm_shape, lstm_settings, lstm_optimizer, batch_size=100, nb_epoch=5):
    nlp = spacy.load('en', parser=False, tagger=False, entity=False) 
    model = _compile_model(
                _get_embeddings(
                    nlp.vocab),
                lstm_shape,
                lstm_settings,
                lstm_optimizer)
    model.fit(
        _get_features(
            nlp.pipe(
                train_texts)),
        train_ys,
        _get_features(
            nlp.pipe(
                dev_texts)),
        dev_ys,
        nb_epoch=nb_epoch,
        batch_size=batch_size)
    model.save(model_dir)


def demonstrate_runtime(model_dir, texts):
    '''Demonstrate runtime usage of the custom sentiment model with spaCy.
    
    Here we return a dictionary mapping entities to the average sentiment of the
    documents they occurred in.
    '''
    def create_pipeline(nlp):
        '''
        This could be a lambda, but named functions are easier to read in Python.
        '''
        return [nlp.tagger, nlp.entity, SentimentAnalyser.load(model_dir, nlp)]
    
    nlp = spacy.load('en', create_pipeline=create_pipeline)
    entity_sentiments = defaultdict(float)
    entity_freqs = defaultdict(int)
    for doc in nlp.pipe(texts, batch_size=1000, n_threads=4):
        sentiment = doc.user_data['sentiment']
        for ent in doc.ents:
            entity_sentiments[ent.text] += sentiment
            entity_freqs[ent.text] += 1
    # Compute estimate of P(sentiment | entity)
    for entity, sentiment in entity_freqs.items():
        entity_sentiments[entity] /= entity_freqs[entity]
    return entity_sentiments


def read_data(data_dir, limit=0):
    examples = []
    for subdir, label in (('pos', 1), ('neg', 0)):
        for filename in (data_dir / subdir).iterdir():
            with filename.open() as file_:
                text = filename.read()
            examples.append((text, label))
    random.shuffle(examples)
    if limit >= 1:
        examples = examples[:limit]
    return zip(*examples) # Unzips into two lists


@plac.annotations(
    language=("The language to train", "positional", None, str, ['en','de', 'zh']),
    train_loc=("Location of training file or directory"),
    dev_loc=("Location of development file or directory"),
    model_dir=("Location of output model directory",),
    is_runtime=("Demonstrate run-time usage", "flag", "r", bool),
    nr_hidden=("Number of hidden units", "flag", "H", int),
    max_length=("Maximum sentence length", "flag", "L", int),
    dropout=("Dropout", "flag", "d", float),
    nr_epoch=("Number of training epochs", "flag", "i", int),
    batch_size=("Size of minibatches for training LSTM", "flag", "b", int),
    nr_examples=("Limit to N examples", "flag", "n", int)
)
def main(model_dir, train_dir, dev_dir,
         is_runtime=False,
         nr_hidden=64, max_length=100, # Shape
         dropout=0.5,                  # General NN config
         nb_epoch=5, batch_size=100, nr_examples=-1):  # Training params
    if is_runtime:
        dev_texts, dev_labels = read_dev(dev_dir)
        demonstrate_runtime(model_dir, dev_texts)
    else:
        train_texts, train_labels = read_data(train_dir, limit=nr_examples)
        dev_texts, dev_labels = read_dev(dev_dir)
        lstm = train(train_texts, train_labels, dev_texts, dev_labels,
                     {'nr_hidden': nr_hidden, 'max_length': max_length},
                     {'dropout': 0.5},
                     {},
                     nb_epoch=nb_epoch, batch_size=batch_size)


if __name__ == '__main__':
    plac.call(main)
