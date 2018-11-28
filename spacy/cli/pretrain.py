'''This script is experimental.

Try pre-training the CNN component of the text categorizer using a cheap
language modelling-like objective. Specifically, we load pre-trained vectors
(from something like word2vec, GloVe, FastText etc), and use the CNN to
predict the tokens' pre-trained vectors. This isn't as easy as it sounds:
we're not merely doing compression here, because heavy dropout is applied,
including over the input words. This means the model must often (50% of the time)
use the context in order to predict the word.

To evaluate the technique, we're pre-training with the 50k texts from the IMDB
corpus, and then training with only 100 labels. Note that it's a bit dirty to
pre-train with the development data, but also not *so* terrible: we're not using
the development labels, after all --- only the unlabelled text.
'''
from __future__ import print_function, unicode_literals
import plac
import random
import numpy
import time
import ujson as json
from pathlib import Path
import sys
from collections import Counter

import spacy
from spacy.tokens import Doc
from spacy.attrs import ID, HEAD
from spacy.util import minibatch, minibatch_by_words, use_gpu, compounding, ensure_path
from spacy._ml import Tok2Vec, flatten, chain, zero_init, create_default_optimizer
from thinc.v2v import Affine
from thinc.api import wrap


def prefer_gpu():
    used = spacy.util.use_gpu(0)
    if used is None:
        return False
    else:
        import cupy.random
        cupy.random.seed(0)
        return True


def load_texts(path):
    '''Load inputs from a jsonl file.
    
    Each line should be a dict like {"text": "..."}
    '''
    path = ensure_path(path)
    with path.open('r', encoding='utf8') as file_:
        texts = [json.loads(line) for line in file_]
    random.shuffle(texts)
    return texts


def stream_texts():
    for line in sys.stdin:
        yield json.loads(line)


def make_update(model, docs, optimizer, drop=0.):
    """Perform an update over a single batch of documents.

    docs (iterable): A batch of `Doc` objects.
    drop (float): The droput rate.
    optimizer (callable): An optimizer.
    RETURNS loss: A float for the loss.
    """
    predictions, backprop = model.begin_update(docs, drop=drop)
    gradients = get_vectors_loss(model.ops, docs, predictions)
    backprop(gradients, sgd=optimizer)
    # Don't want to return a cupy object here
    # The gradients are modified in-place by the BERT MLM,
    # so we get an accurate loss
    loss = float((gradients**2).mean())
    return loss


def make_docs(nlp, batch):
    docs = []
    for record in batch:
        text = record["text"]
        if "tokens" in record:
            doc = Doc(nlp.vocab, words=record["tokens"])
        else:
            doc = nlp.make_doc(text)
        if "heads" in record:
            heads = record["heads"]
            heads = numpy.asarray(heads, dtype="uint64")
            heads = heads.reshape((len(doc), 1))
            doc = doc.from_array([HEAD], heads)
        if len(doc) >= 1 and len(doc) < 200:
            docs.append(doc)
    return docs


def get_vectors_loss(ops, docs, prediction):
    """Compute a mean-squared error loss between the documents' vectors and
    the prediction.    

    Note that this is ripe for customization! We could compute the vectors
    in some other word, e.g. with an LSTM language model, or use some other
    type of objective.
    """
    # The simplest way to implement this would be to vstack the
    # token.vector values, but that's a bit inefficient, especially on GPU.
    # Instead we fetch the index into the vectors table for each of our tokens,
    # and look them up all at once. This prevents data copying.
    ids = ops.flatten([doc.to_array(ID).ravel() for doc in docs])
    target = docs[0].vocab.vectors.data[ids]
    d_scores = prediction - target
    return d_scores


def create_pretraining_model(nlp, tok2vec):
    '''Define a network for the pretraining. We simply add an output layer onto
    the tok2vec input model. The tok2vec input model needs to be a model that
    takes a batch of Doc objects (as a list), and returns a list of arrays.
    Each array in the output needs to have one row per token in the doc.
    '''
    output_size = nlp.vocab.vectors.data.shape[1]
    output_layer = zero_init(Affine(output_size, drop_factor=0.0))
    # This is annoying, but the parser etc have the flatten step after
    # the tok2vec. To load the weights in cleanly, we need to match
    # the shape of the models' components exactly. So what we cann
    # "tok2vec" has to be the same set of processes as what the components do.
    tok2vec = chain(tok2vec, flatten)
    model = chain(
        tok2vec,
        output_layer
    )
    model = masked_language_model(nlp.vocab, model)
    model.tok2vec = tok2vec
    model.output_layer = output_layer
    model.begin_training([nlp.make_doc('Give it a doc to infer shapes')])
    return model


def masked_language_model(vocab, model, mask_prob=0.15):
    '''Convert a model into a BERT-style masked language model'''
    vocab_words = [lex.text for lex in vocab if lex.prob != 0.0]
    vocab_probs = [lex.prob for lex in vocab if lex.prob != 0.0]
    vocab_words = vocab_words[:10000]
    vocab_probs = vocab_probs[:10000]
    vocab_probs = numpy.exp(numpy.array(vocab_probs, dtype='f'))
    vocab_probs /= vocab_probs.sum()
    
    def mlm_forward(docs, drop=0.):
        mask, docs = apply_mask(docs, vocab_words, vocab_probs,
                                mask_prob=mask_prob)
        mask = model.ops.asarray(mask).reshape((mask.shape[0], 1))
        output, backprop = model.begin_update(docs, drop=drop)

        def mlm_backward(d_output, sgd=None):
            d_output *= 1-mask
            return backprop(d_output, sgd=sgd)

        return output, mlm_backward

    return wrap(mlm_forward, model)


def apply_mask(docs, vocab_texts, vocab_probs, mask_prob=0.15):
    N = sum(len(doc) for doc in docs)
    mask = numpy.random.uniform(0., 1.0, (N,))
    mask = mask >= mask_prob
    i = 0
    masked_docs = []
    for doc in docs:
        words = []
        for token in doc:
            if not mask[i]:
                word = replace_word(token.text, vocab_texts, vocab_probs)
            else:
                word = token.text
            words.append(word)
            i += 1
        spaces = [bool(w.whitespace_) for w in doc]
        # NB: If you change this implementation to instead modify
        # the docs in place, take care that the IDs reflect the original
        # words. Currently we use the original docs to make the vectors
        # for the target, so we don't lose the original tokens. But if
        # you modified the docs in place here, you would.
        masked_docs.append(Doc(doc.vocab, words=words, spaces=spaces))
    return mask, masked_docs


def replace_word(word, vocab_texts, vocab_probs, mask='[MASK]'):
    roll = random.random()
    if roll < 0.8:
        return mask
    elif roll < 0.9:
        index = numpy.random.choice(len(vocab_texts), p=vocab_probs)
        return vocab_texts[index]
    else:
        return word


class ProgressTracker(object):
    def __init__(self, frequency=100000):
        self.loss = 0.0
        self.prev_loss = 0.0
        self.nr_word = 0
        self.words_per_epoch = Counter()
        self.frequency = frequency
        self.last_time = time.time()
        self.last_update = 0

    def update(self, epoch, loss, docs):
        self.loss += loss
        words_in_batch = sum(len(doc) for doc in docs)
        self.words_per_epoch[epoch] += words_in_batch
        self.nr_word += words_in_batch
        words_since_update = self.nr_word - self.last_update
        if words_since_update >= self.frequency:
            wps = words_since_update / (time.time() - self.last_time)
            self.last_update = self.nr_word
            self.last_time = time.time()
            loss_per_word = self.loss - self.prev_loss
            status = (
                epoch,
                self.nr_word,
                "%.5f" % self.loss,
                "%.4f" % loss_per_word,
                int(wps),
            )
            self.prev_loss = float(self.loss)
            return status
        else:
            return None


@plac.annotations(
    texts_loc=("Path to jsonl file with texts to learn from", "positional", None, str),
    vectors_model=("Name or path to vectors model to learn from"),
    output_dir=("Directory to write models each epoch", "positional", None, str),
    width=("Width of CNN layers", "option", "cw", int),
    depth=("Depth of CNN layers", "option", "cd", int),
    embed_rows=("Embedding rows", "option", "er", int),
    use_vectors=("Whether to use the static vectors as input features", "flag", "uv"),
    dropout=("Dropout", "option", "d", float),
    seed=("Seed for random number generators", "option", "s", float),
    nr_iter=("Number of iterations to pretrain", "option", "i", int),
)
def pretrain(texts_loc, vectors_model, output_dir, width=128, depth=4,
        embed_rows=5000, use_vectors=False, dropout=0.2, nr_iter=100, seed=0):
    """
    Pre-train the 'token-to-vector' (tok2vec) layer of pipeline components,
    using an approximate language-modelling objective. Specifically, we load
    pre-trained vectors, and train a component like a CNN, BiLSTM, etc to predict
    vectors which match the pre-trained ones. The weights are saved to a directory
    after each epoch. You can then pass a path to one of these pre-trained weights
    files to the 'spacy train' command.

    This technique may be especially helpful if you have little labelled data.
    However, it's still quite experimental, so your mileage may vary.

    To load the weights back in during 'spacy train', you need to ensure
    all settings are the same between pretraining and training. The API and
    errors around this need some improvement.
    """
    config = dict(locals())
    output_dir = ensure_path(output_dir)
    random.seed(seed)
    numpy.random.seed(seed)
    if not output_dir.exists():
        output_dir.mkdir()
    with (output_dir / 'config.json').open('w') as file_:
        file_.write(json.dumps(config))
    has_gpu = prefer_gpu()
    print("Use GPU?", has_gpu)
    nlp = spacy.load(vectors_model)
    pretrained_vectors = None if not use_vectors else nlp.vocab.vectors.name
    model = create_pretraining_model(nlp,
                Tok2Vec(width, embed_rows,
                    conv_depth=depth,
                    pretrained_vectors=pretrained_vectors,
                    bilstm_depth=0, # Requires PyTorch. Experimental.
                    cnn_maxout_pieces=2, # You can try setting this higher
                    subword_features=True)) # Set to False for character models, e.g. Chinese
    optimizer = create_default_optimizer(model.ops)
    tracker = ProgressTracker()
    print('Epoch', '#Words', 'Loss', 'w/s')
    texts = stream_texts() if texts_loc == '-' else load_texts(texts_loc) 
    for epoch in range(nr_iter):
        for batch in minibatch(texts, size=256):
            docs = make_docs(nlp, batch)
            loss = make_update(model, docs, optimizer, drop=dropout)
            progress = tracker.update(epoch, loss, docs)
            if progress:
                print(*progress)
                if texts_loc == '-' and tracker.words_per_epoch[epoch] >= 10**7:
                    break
        with model.use_params(optimizer.averages):
            with (output_dir / ('model%d.bin' % epoch)).open('wb') as file_:
                file_.write(model.tok2vec.to_bytes())
            with (output_dir / 'log.jsonl').open('a') as file_:
                file_.write(json.dumps({'nr_word': tracker.nr_word,
                    'loss': tracker.loss, 'epoch': epoch}) + '\n')
        if texts_loc != '-':
            texts = load_texts(texts_loc)
