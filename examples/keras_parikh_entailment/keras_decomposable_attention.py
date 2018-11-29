# Semantic entailment/similarity with decomposable attention (using spaCy and Keras)
# Practical state-of-the-art textual entailment with spaCy and Keras

import numpy as np
from keras import layers, Model, models, optimizers
from keras import backend as K

def build_model(vectors, shape, settings):
    max_length, nr_hidden, nr_class = shape

    input1 = layers.Input(shape=(max_length,), dtype='int32', name='words1')
    input2 = layers.Input(shape=(max_length,), dtype='int32', name='words2')
    
    # embeddings (projected)
    embed = create_embedding(vectors, max_length, nr_hidden)
   
    a = embed(input1)
    b = embed(input2)
    
    # step 1: attend
    F = create_feedforward(nr_hidden)
    att_weights = layers.dot([F(a), F(b)], axes=-1)
    
    G = create_feedforward(nr_hidden)
    
    if settings['entail_dir'] == 'both':
        norm_weights_a = layers.Lambda(normalizer(1))(att_weights)
        norm_weights_b = layers.Lambda(normalizer(2))(att_weights)
        alpha = layers.dot([norm_weights_a, a], axes=1)
        beta  = layers.dot([norm_weights_b, b], axes=1)

        # step 2: compare
        comp1 = layers.concatenate([a, beta])
        comp2 = layers.concatenate([b, alpha])
        v1 = layers.TimeDistributed(G)(comp1)
        v2 = layers.TimeDistributed(G)(comp2)

        # step 3: aggregate
        v1_sum = layers.Lambda(sum_word)(v1)
        v2_sum = layers.Lambda(sum_word)(v2)
        concat = layers.concatenate([v1_sum, v2_sum])

    elif settings['entail_dir'] == 'left':
        norm_weights_a = layers.Lambda(normalizer(1))(att_weights)
        alpha = layers.dot([norm_weights_a, a], axes=1)
        comp2 = layers.concatenate([b, alpha])
        v2 = layers.TimeDistributed(G)(comp2)
        v2_sum = layers.Lambda(sum_word)(v2)
        concat = v2_sum

    else:
        norm_weights_b = layers.Lambda(normalizer(2))(att_weights)
        beta  = layers.dot([norm_weights_b, b], axes=1)
        comp1 = layers.concatenate([a, beta])
        v1 = layers.TimeDistributed(G)(comp1)
        v1_sum = layers.Lambda(sum_word)(v1)
        concat = v1_sum
    
    H = create_feedforward(nr_hidden)
    out = H(concat)
    out = layers.Dense(nr_class, activation='softmax')(out)
    
    model = Model([input1, input2], out)
    
    model.compile(
        optimizer=optimizers.Adam(lr=settings['lr']),
        loss='categorical_crossentropy',
        metrics=['accuracy'])
    
    return model


def create_embedding(vectors, max_length, projected_dim):
    return models.Sequential([
        layers.Embedding(
            vectors.shape[0],
            vectors.shape[1],
            input_length=max_length,
            weights=[vectors],
            trainable=False),
        
        layers.TimeDistributed(
            layers.Dense(projected_dim,
                         activation=None,
                         use_bias=False))
    ])

def create_feedforward(num_units=200, activation='relu', dropout_rate=0.2):
    return models.Sequential([
        layers.Dense(num_units, activation=activation),
        layers.Dropout(dropout_rate),
        layers.Dense(num_units, activation=activation),
        layers.Dropout(dropout_rate)
    ])


def normalizer(axis):
    def _normalize(att_weights):
        exp_weights = K.exp(att_weights)
        sum_weights = K.sum(exp_weights, axis=axis, keepdims=True)
        return exp_weights/sum_weights
    return _normalize

def sum_word(x):
    return K.sum(x, axis=1)


def test_build_model():
    vectors = np.ndarray((100, 8), dtype='float32')
    shape = (10, 16, 3)
    settings = {'lr': 0.001, 'dropout': 0.2, 'gru_encode':True, 'entail_dir':'both'}
    model = build_model(vectors, shape, settings)


def test_fit_model():

    def _generate_X(nr_example, length, nr_vector):
        X1 = np.ndarray((nr_example, length), dtype='int32')
        X1 *= X1 < nr_vector
        X1 *= 0 <= X1
        X2 = np.ndarray((nr_example, length), dtype='int32')
        X2 *= X2 < nr_vector
        X2 *= 0 <= X2
        return [X1, X2]

    def _generate_Y(nr_example, nr_class):
        ys = np.zeros((nr_example, nr_class), dtype='int32')
        for i in range(nr_example):
            ys[i, i % nr_class] = 1
        return ys

    vectors = np.ndarray((100, 8), dtype='float32')
    shape = (10, 16, 3)
    settings = {'lr': 0.001, 'dropout': 0.2, 'gru_encode':True, 'entail_dir':'both'}
    model = build_model(vectors, shape, settings)

    train_X = _generate_X(20, shape[0], vectors.shape[0])
    train_Y = _generate_Y(20, shape[2])
    dev_X = _generate_X(15, shape[0], vectors.shape[0])
    dev_Y = _generate_Y(15, shape[2])

    model.fit(train_X, train_Y, validation_data=(dev_X, dev_Y), epochs=5, batch_size=4)


__all__ = [build_model]
