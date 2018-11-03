'''Not sure if this is useful -- try training the Tensorizer component.'''
import plac
import spacy
import thinc.extra.datasets
from spacy.util import minibatch, use_gpu
import tqdm


def load_imdb():
    nlp = spacy.blank('en')
    train, dev = thinc.extra.datasets.imdb()
    train_texts, _ = zip(*train)
    dev_texts, _ = zip(*dev)
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    return list(train_texts), list(dev_texts)


def get_sentences(nlp, texts):
    for doc in nlp.pipe(texts):
        for sent in doc.sents:
            yield sent.text


def prefer_gpu():
    used = spacy.util.use_gpu(0)
    if used is None:
        return False
    else:
        return True

def main(vectors_model):
    use_gpu = prefer_gpu()
    print("Using GPU?", use_gpu)
    print("Load data")
    train_texts, dev_texts = load_imdb()
    print("Load vectors")
    nlp = spacy.load(vectors_model)
    print("Start training")
    nlp.add_pipe(nlp.create_pipe('tagger'))
    tensorizer = nlp.create_pipe('tensorizer')
    nlp.add_pipe(tensorizer)
    optimizer = nlp.begin_training()

    for i in range(10):
        losses = {}
        for i, batch in enumerate(minibatch(tqdm.tqdm(train_texts))):
            docs = [nlp.make_doc(text) for text in batch]
            tensorizer.update(docs, None, losses=losses, sgd=optimizer, drop=0.5)
        print(losses)

if __name__ == '__main__':
    plac.call(main)
