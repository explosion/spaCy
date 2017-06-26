from __future__ import unicode_literals, print_function

import random

from spacy.lang.en import English
from spacy.gold import GoldParse, biluo_tags_from_offsets


def reformat_train_data(tokenizer, examples):
    """Reformat data to match JSON format"""
    output = []
    for i, (text, entity_offsets) in enumerate(examples):
        doc = tokenizer(text)
        ner_tags = biluo_tags_from_offsets(tokenizer(text), entity_offsets)
        words = [w.text for w in doc]
        tags = ['-'] * len(doc)
        heads = [0] * len(doc)
        deps = [''] * len(doc)
        sentence = (range(len(doc)), words, tags, heads, deps, ner_tags)
        output.append((text, [(sentence, [])]))
    return output


def main(model_dir=None):
    train_data = [
        (
            'Who is Shaka Khan?',
            [(len('Who is '), len('Who is Shaka Khan'), 'PERSON')]
        ),
        (
            'I like London and Berlin.',
            [(len('I like '), len('I like London'), 'LOC'),
            (len('I like London and '), len('I like London and Berlin'), 'LOC')]
        )
    ]
    nlp = English(pipeline=['tensorizer', 'ner'])
    get_data = lambda: reformat_train_data(nlp.tokenizer, train_data)
    optimizer = nlp.begin_training(get_data)
    for itn in range(100):
        random.shuffle(train_data)
        losses = {}
        for raw_text, entity_offsets in train_data:
            doc = nlp.make_doc(raw_text)
            gold = GoldParse(doc, entities=entity_offsets)
            nlp.update(
                [doc], # Batch of Doc objects
                [gold], # Batch of GoldParse objects
                drop=0.5, # Dropout -- make it harder to memorise data
                sgd=optimizer, # Callable to update weights
                losses=losses)
        print(losses)
    print("Save to", model_dir)
    nlp.to_disk(model_dir)
    print("Load from", model_dir)
    nlp = spacy.lang.en.English(pipeline=['tensorizer', 'ner'])
    nlp.from_disk(model_dir)
    for raw_text, _ in train_data:
        doc = nlp(raw_text)
        for word in doc:
            print(word.text, word.ent_type_, word.ent_iob_)

if __name__ == '__main__':
    import plac
    plac.call(main)
    # Who "" 2
    # is "" 2
    # Shaka "" PERSON 3
    # Khan "" PERSON 1
    # ? "" 2
