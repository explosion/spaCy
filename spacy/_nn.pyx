"""Feed-forward neural network, using Thenao."""

import os
import sys
import time

import numpy

import theano
import theano.tensor as T
import plac

from spacy.gold import read_json_file
from spacy.gold import GoldParse
from spacy.en.pos import POS_TEMPLATES, POS_TAGS, setup_model_dir


def build_model(n_classes, n_vocab, n_hidden, n_word_embed, n_tag_embed):
    # allocate symbolic variables for the data
    words = T.vector('words')
    tags = T.vector('tags') 
    
    word_e = _init_embedding(n_words, n_word_embed)
    tag_e = _init_embedding(n_tags, n_tag_embed)
    label_e = _init_embedding(n_labels, n_label_embed)
    maxent_W, maxent_b = _init_maxent_weights(n_hidden, n_classes)
    hidden_W, hidden_b = _init_hidden_weights(28*28, n_hidden, T.tanh) 
    params = [hidden_W, hidden_b, maxent_W, maxent_b, word_e, tag_e, label_e]

    x = T.concatenate([
          T.flatten(word_e[word_indices], outdim=1),
          T.flatten(tag_e[tag_indices], outdim=1)])

    p_y_given_x = feed_layer(
                    T.nnet.softmax,
                    maxent_W,
                    maxent_b,
                      feed_layer(
                        T.tanh,
                        hidden_W,
                        hidden_b,
                        x))[0]

    guess = T.argmax(p_y_given_x)

    cost = (
        -T.log(p_y_given_x[y])
        + L1(L1_reg, maxent_W, hidden_W, word_e, tag_e)
        + L2(L2_reg, maxent_W, hidden_W, wod_e, tag_e)
    )

    train_model = theano.function(
        inputs=[words, tags, y],
        outputs=guess,
        updates=[update(learning_rate, param, cost) for param in params]
    )

    evaluate_model = theano.function(
        inputs=[x, y],
        outputs=T.neq(y, T.argmax(p_y_given_x[0])),
    )
    return train_model, evaluate_model


def _init_embedding(vocab_size, n_dim):
    embedding = 0.2 * numpy.random.uniform(-1.0, 1.0, (vocab_size+1, n_dim))
    return theano.shared(embedding).astype(theano.config.floatX)


def _init_maxent_weights(n_hidden, n_out):
    weights = numpy.zeros((n_hidden, 10), dtype=theano.config.floatX)
    bias =  numpy.zeros((10,), dtype=theano.config.floatX)
    return (
        theano.shared(name='W', borrow=True, value=weights),
        theano.shared(name='b', borrow=True, value=bias)
    )


def _init_hidden_weights(n_in, n_out, activation=T.tanh):
    rng = numpy.random.RandomState(1234)
    weights = numpy.asarray(
        rng.uniform(
            low=-numpy.sqrt(6. / (n_in + n_out)),
            high=numpy.sqrt(6. / (n_in + n_out)),
            size=(n_in, n_out)
        ),
        dtype=theano.config.floatX
    )

    bias = numpy.zeros((n_out,), dtype=theano.config.floatX)
    return (
        theano.shared(value=weights, name='W', borrow=True),
        theano.shared(value=bias, name='b', borrow=True)
    )

           
def feed_layer(activation, weights, bias, input):
    return activation(T.dot(input, weights) + bias)


def L1(L1_reg, w1, w2):
    return L1_reg * (abs(w1).sum() + abs(w2).sum())


def L2(L2_reg, w1, w2):
    return L2_reg * ((w1 ** 2).sum() + (w2 ** 2).sum())


def update(eta, param, cost):
    return (param, param - (eta * T.grad(cost, param)))


def main(train_loc, eval_loc, model_dir):
    learning_rate = 0.01
    L1_reg = 0.00
    L2_reg = 0.0001

    print "... reading the data"
    gold_train = list(read_json_file(train_loc))
    print '... building the model'
    pos_model_dir = path.join(model_dir, 'pos')
    if path.exists(pos_model_dir):
        shutil.rmtree(pos_model_dir)
    os.mkdir(pos_model_dir)

    setup_model_dir(sorted(POS_TAGS.keys()), POS_TAGS, POS_TEMPLATES, pos_model_dir)

    train_model, evaluate_model = build_model(n_hidden, len(POS_TAGS), learning_rate,
                                              L1_reg, L2_reg)

    print '... training'
    for epoch in range(1, n_epochs+1):
        for raw_text, sents in gold_tuples:
            for (ids, words, tags, ner, heads, deps), _ in sents:
                tokens = nlp.tokenizer.tokens_from_list(words)
                for t in tokens:
                    guess = train_model([t.orth], [t.tag])
                    loss += guess != t.tag
        print loss
        # compute zero-one loss on validation set
        #error = numpy.mean([evaluate_model(x, y) for x, y in dev_examples])
        #print('epoch %i, validation error %f %%' % (epoch, error * 100))


if __name__ == '__main__':
    plac.call(main)
