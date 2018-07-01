'''This example shows how to add a multi-task objective that is trained
alongside the entity recognizer. This is an alternative to adding features
to the model.

The multi-task idea is to train an auxiliary model to predict some attribute,
with weights shared between the auxiliary model and the main model. In this
example, we're predicting the position of the word in the document.

The model that predicts the position of the word encourages the convolutional
layers to include the position information in their representation. The
information is then available to the main model, as a feature.

The overall idea is that we might know something about what sort of features
we'd like the CNN to extract. The multi-task objectives can encourage the
extraction of this type of feature. The multi-task objective is only used
during training. We discard the auxiliary model before run-time.

The specific example here is not necessarily a good idea --- but it shows
how an arbitrary objective function for some word can be used.

Developed and tested for spaCy 2.0.6
'''
import random
import plac
import spacy
import os.path
from spacy.gold import read_json_file, GoldParse

random.seed(0)

PWD = os.path.dirname(__file__)

TRAIN_DATA = list(read_json_file(os.path.join(PWD, 'training-data.json')))



def get_position_label(i, words, tags, heads, labels, ents):
    '''Return labels indicating the position of the word in the document.
    '''
    if len(words) < 20:
        return 'short-doc'
    elif i == 0:
        return 'first-word'
    elif i < 10:
        return 'early-word'
    elif i < 20:
        return 'mid-word'
    elif i == len(words)-1:
        return 'last-word'
    else:
        return 'late-word'


def main(n_iter=10):
    nlp = spacy.blank('en')
    ner = nlp.create_pipe('ner')
    ner.add_multitask_objective(get_position_label)
    nlp.add_pipe(ner)

    print("Create data", len(TRAIN_DATA))
    optimizer = nlp.begin_training(get_gold_tuples=lambda: TRAIN_DATA)
    for itn in range(n_iter):
        random.shuffle(TRAIN_DATA)
        losses = {}
        for text, annot_brackets in TRAIN_DATA:
            annotations, _ = annot_brackets
            doc = nlp.make_doc(text)
            gold = GoldParse.from_annot_tuples(doc, annotations[0])
            nlp.update(
                [doc],  # batch of texts
                [gold],  # batch of annotations
                drop=0.2,  # dropout - make it harder to memorise data
                sgd=optimizer,  # callable to update weights
                losses=losses)
        print(losses.get('nn_labeller', 0.0), losses['ner'])

    # test the trained model
    for text, _ in TRAIN_DATA:
        doc = nlp(text)
        print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
        print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])


if __name__ == '__main__':
    plac.call(main)
