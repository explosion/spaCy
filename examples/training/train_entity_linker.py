#!/usr/bin/env python
# coding: utf8

"""Example of training spaCy's entity linker, starting off with an
existing model and a pre-defined knowledge base.

For more details, see the documentation:
* Training: https://spacy.io/usage/training
* Entity Linking: https://spacy.io/usage/linguistic-features#entity-linking

Compatible with: spaCy v2.2.3
Last tested with: v2.2.3
"""
from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path

from spacy.symbols import PERSON
from spacy.vocab import Vocab

import spacy
from spacy.kb import KnowledgeBase
from spacy.pipeline import EntityRuler
from spacy.tokens import Span
from spacy.util import minibatch, compounding


def sample_train_data():
    train_data = []

    # Q2146908 (Russ Cochran): American golfer
    # Q7381115 (Russ Cochran): publisher

    text_1 = "Russ Cochran his reprints include EC Comics."
    dict_1 = {(0, 12): {"Q7381115": 1.0, "Q2146908": 0.0}}
    train_data.append((text_1, {"links": dict_1}))

    text_2 = "Russ Cochran has been publishing comic art."
    dict_2 = {(0, 12): {"Q7381115": 1.0, "Q2146908": 0.0}}
    train_data.append((text_2, {"links": dict_2}))

    text_3 = "Russ Cochran captured his first major title with his son as caddie."
    dict_3 = {(0, 12): {"Q7381115": 0.0, "Q2146908": 1.0}}
    train_data.append((text_3, {"links": dict_3}))

    text_4 = "Russ Cochran was a member of University of Kentucky's golf team."
    dict_4 = {(0, 12): {"Q7381115": 0.0, "Q2146908": 1.0}}
    train_data.append((text_4, {"links": dict_4}))

    return train_data


# training data
TRAIN_DATA = sample_train_data()


@plac.annotations(
    kb_path=("Path to the knowledge base", "positional", None, Path),
    vocab_path=("Path to the vocab for the kb", "positional", None, Path),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
)
def main(kb_path, vocab_path=None, output_dir=None, n_iter=50):
    """Create a blank model with the specified vocab, set up the pipeline and train the entity linker.
    The `vocab` should be the one used during creation of the KB."""
    vocab = Vocab().from_disk(vocab_path)
    # create blank Language class with correct vocab
    nlp = spacy.blank("en", vocab=vocab)
    nlp.vocab.vectors.name = "spacy_pretrained_vectors"
    print("Created blank 'en' model with vocab from '%s'" % vocab_path)

    # Add a sentencizer component. Alternatively, add a dependency parser for higher accuracy.
    nlp.add_pipe(nlp.create_pipe('sentencizer'))

    # Add a custom component to recognize "Russ Cochran" as an entity for the example training data.
    # Note that in a realistic application, an actual NER algorithm should be used instead.
    ruler = EntityRuler(nlp)
    patterns = [{"label": "PERSON", "pattern": [{"LOWER": "russ"}, {"LOWER": "cochran"}]}]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)

    # Create the Entity Linker component and add it to the pipeline.
    if "entity_linker" not in nlp.pipe_names:
        # use only the predicted EL score and not the prior probability (for demo purposes)
        cfg = {"incl_prior": False}
        entity_linker = nlp.create_pipe("entity_linker", cfg)
        kb = KnowledgeBase(vocab=nlp.vocab)
        kb.load_bulk(kb_path)
        print("Loaded Knowledge Base from '%s'" % kb_path)
        entity_linker.set_kb(kb)
        nlp.add_pipe(entity_linker, last=True)

    # Convert the texts to docs to make sure we have doc.ents set for the training examples.
    # Also ensure that the annotated examples correspond to known identifiers in the knowlege base.
    kb_ids = nlp.get_pipe("entity_linker").kb.get_entity_strings()
    TRAIN_DOCS = []
    for text, annotation in TRAIN_DATA:
        with nlp.disable_pipes("entity_linker"):
            doc = nlp(text)
        annotation_clean = annotation
        for offset, kb_id_dict in annotation["links"].items():
            new_dict = {}
            for kb_id, value in kb_id_dict.items():
                if kb_id in kb_ids:
                    new_dict[kb_id] = value
                else:
                    print(
                        "Removed", kb_id, "from training because it is not in the KB."
                    )
            annotation_clean["links"][offset] = new_dict
        TRAIN_DOCS.append((doc, annotation_clean))

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "entity_linker"]
    with nlp.disable_pipes(*other_pipes):  # only train entity linker
        # reset and initialize the weights randomly
        optimizer = nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DOCS)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DOCS, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.2,  # dropout - make it harder to memorise data
                    losses=losses,
                    sgd=optimizer,
                )
            print(itn, "Losses", losses)

    # test the trained model
    _apply_model(nlp)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print()
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        _apply_model(nlp2)


def _apply_model(nlp):
    for text, annotation in TRAIN_DATA:
        # apply the entity linker which will now make predictions for the 'Russ Cochran' entities
        doc = nlp(text)
        print()
        print("Entities", [(ent.text, ent.label_, ent.kb_id_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_kb_id_) for t in doc])


if __name__ == "__main__":
    plac.call(main)

    # Expected output (can be shuffled):

    # Entities[('Russ Cochran', 'PERSON', 'Q7381115')]
    # Tokens[('Russ', 'PERSON', 'Q7381115'), ('Cochran', 'PERSON', 'Q7381115'), ("his", '', ''), ('reprints', '', ''), ('include', '', ''), ('The', '', ''), ('Complete', '', ''), ('EC', '', ''), ('Library', '', ''), ('.', '', '')]

    # Entities[('Russ Cochran', 'PERSON', 'Q7381115')]
    # Tokens[('Russ', 'PERSON', 'Q7381115'), ('Cochran', 'PERSON', 'Q7381115'), ('has', '', ''), ('been', '', ''), ('publishing', '', ''), ('comic', '', ''), ('art', '', ''), ('.', '', '')]

    # Entities[('Russ Cochran', 'PERSON', 'Q2146908')]
    # Tokens[('Russ', 'PERSON', 'Q2146908'), ('Cochran', 'PERSON', 'Q2146908'), ('captured', '', ''), ('his', '', ''), ('first', '', ''), ('major', '', ''), ('title', '', ''), ('with', '', ''), ('his', '', ''), ('son', '', ''), ('as', '', ''), ('caddie', '', ''), ('.', '', '')]

    # Entities[('Russ Cochran', 'PERSON', 'Q2146908')]
    # Tokens[('Russ', 'PERSON', 'Q2146908'), ('Cochran', 'PERSON', 'Q2146908'), ('was', '', ''), ('a', '', ''), ('member', '', ''), ('of', '', ''), ('University', '', ''), ('of', '', ''), ('Kentucky', '', ''), ("'s", '', ''), ('golf', '', ''), ('team', '', ''), ('.', '', '')]
