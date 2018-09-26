import numpy as np
import ujson as json
from keras.utils import to_categorical
import plac
from pathlib import Path

import spacy

from keras_decompositional_attention import build_model


def train(train_loc, dev_loc, shape, settings):
    train_texts1, train_texts2, train_labels = read_snli(train_loc)
    dev_texts1, dev_texts2, dev_labels = read_snli(dev_loc)

    print("Loading spaCy")
    nlp = spacy.load('en-vectors-web-lg')
    assert nlp.path is not None
   
    print("Processing texts...")

    train_x1, train_X2, train_labels = create_dataset(nlp, train_texts1, train_texts2, 100, shape[0])
    dev_x1, dev_X2, dev_labels = create_dataset(nlp, dev_texts1, dev_texts2, 100, shape[0])

    print("Compiling network")
    model = build_model(get_embeddings(nlp.vocab), shape, settings)


    print(settings)
    model.fit(
        [train_X1, train_X2],
        train_labels,
        validation_data=([dev_X1, dev_X2], dev_labels),
        nb_epoch=settings['nr_epoch'],
        batch_size=settings['batch_size'])
    if not (nlp.path / 'similarity').exists():
        (nlp.path / 'similarity').mkdir()
    print("Saving to", nlp.path / 'similarity')
    weights = model.get_weights()
    with (nlp.path / 'similarity' / 'model').open('wb') as file_:
        pickle.dump(weights[1:], file_)
    with (nlp.path / 'similarity' / 'config.json').open('wb') as file_:
        file_.write(model.to_json())


def evaluate(dev_loc):
    dev_texts1, dev_texts2, dev_labels = read_snli(dev_loc)
    nlp = spacy.load('en',
            create_pipeline=create_similarity_pipeline)
    total = 0.
    correct = 0.
    for text1, text2, label in zip(dev_texts1, dev_texts2, dev_labels):
        doc1 = nlp(text1)
        doc2 = nlp(text2)
        sim = doc1.similarity(doc2)
        if sim.argmax() == label.argmax():
            correct += 1
        total += 1
    return correct, total


def demo():
    nlp = spacy.load('en',
            create_pipeline=create_similarity_pipeline)
    doc1 = nlp(u'What were the best crime fiction books in 2016?')
    doc2 = nlp(
        u'What should I read that was published last year? I like crime stories.')
    print(doc1)
    print(doc2)
    print("Similarity", doc1.similarity(doc2))


LABELS = {'entailment': 0, 'contradiction': 1, 'neutral': 2}
def read_snli(path):
    texts1 = []
    texts2 = []
    labels = []
    with open(path, 'r') as file_:
        for line in file_:
            eg = json.loads(line)
            label = eg['gold_label']
            if label == '-':  # per Parikh, ignore - SNLI entries
                continue
            texts1.append(eg['sentence1'])
            texts2.append(eg['sentence2'])
            labels.append(LABELS[label])
    return texts1, texts2, to_categorical(np.asarray(labels, dtype='int32'))

def create_dataset(nlp, texts, hypotheses, num_oov, max_length):
    sents = texts + hypotheses
    
    # the extra +1 is for a zero vector represting NULL for padding
    num_vectors = max(lex.rank for lex in nlp.vocab) + 2 
    
    # create random vectors for OOV tokens
    oov = np.random.normal(size=(num_oov, nlp.vocab.vectors_length))
    oov = oov / oov.sum(axis=1, keepdims=True)
    
    vectors = np.zeros((num_vectors + num_oov, nlp.vocab.vectors_length), dtype='float32')
    vectors[num_vectors:, ] = oov
    for lex in nlp.vocab:
        if lex.has_vector and lex.vector_norm > 0:
            vectors[lex.rank + 1] = lex.vector / lex.vector_norm
            
    sents_as_ids = []
    for sent in sents:
        doc = nlp(sent)
        word_ids = []
        
        for i, token in enumerate(doc):
            # skip odd spaces from tokenizer
            if token.has_vector and token.vector_norm == 0:
                continue
                
            if i > max_length:
                break
                
            if token.has_vector:
                word_ids.append(token.rank + 1)
            else:
                # if we don't have a vector, pick an OOV entry
                word_ids.append(token.rank % num_oov + num_vectors) 
                
        # there must be a simpler way of generating padded arrays from lists...
        word_id_vec = np.zeros((max_length), dtype='int')
        clipped_len = min(max_length, len(word_ids))
        word_id_vec[:clipped_len] = word_ids[:clipped_len]
        sents_as_ids.append(word_id_vec)
        
        
    return vectors, np.array(sents_as_ids[:len(texts)]), np.array(sents_as_ids[len(texts):])


@plac.annotations(
    mode=("Mode to execute", "positional", None, str, ["train", "evaluate", "demo"]),
    train_loc=("Path to training data", "positional", None, Path),
    dev_loc=("Path to development data", "positional", None, Path),
    max_length=("Length to truncate sentences", "option", "L", int),
    nr_hidden=("Number of hidden units", "option", "H", int),
    dropout=("Dropout level", "option", "d", float),
    learn_rate=("Learning rate", "option", "e", float),
    batch_size=("Batch size for neural network training", "option", "b", int),
    nr_epoch=("Number of training epochs", "option", "i", int),
    tree_truncate=("Truncate sentences by tree distance", "flag", "T", bool),
    gru_encode=("Encode sentences with bidirectional GRU", "flag", "E", bool),
    entail_dir=("Direction of entailment", "option", "D", str, ["both", "left", "right"])
)
def main(mode, train_loc, dev_loc,
        tree_truncate = False,
        gru_encode = False,
        max_length = 50,
        nr_hidden = 200,
        dropout = 0.2,
        learn_rate = 0.001,
        batch_size = 1024,
        nr_epoch = 10,
        entail_dir="both"):
    
    shape = (max_length, nr_hidden, 3)
    settings = {
        'lr': learn_rate,
        'dropout': dropout,
        'batch_size': batch_size,
        'nr_epoch': nr_epoch,
        'tree_truncate': tree_truncate,
        'gru_encode': gru_encode
        'entail_dir': entail_dir
    }

    if mode == 'train':
        train(train_loc, dev_loc, shape, settings)
    elif mode == 'evaluate':
        correct, total = evaluate(dev_loc)
        print(correct, '/', total, correct / total)
    else:
        demo()

if __name__ == '__main__':
    plac.call(main)
