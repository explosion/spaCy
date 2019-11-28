# coding: utf8
from __future__ import unicode_literals, print_function

from pathlib import Path
import plac
import sys
import srsly
from wasabi import Printer
from spacy.morphology import FEATURES


@plac.annotations(
    train_path=("location of JSON-formatted training data", "positional", None, Path),
    tag_map_path=("Location of JSON-formatted tag map", "positional", None, Path),
)
def make_tag_map(
    train_path,
    tag_map_path,
):
    """
    Generate a JSON tag map from tags in JSON-formatted training data.
    """
    msg = Printer()

    # Make sure all files and paths exists if they are needed
    if not train_path.exists():
        msg.fail("Training data not found", train_path, exits=1)

    data = srsly.read_json(train_path)

    tags = set()
    for doc in data:
        for para in doc["paragraphs"]:
            for sent in para["sentences"]:
                for token in sent["tokens"]:
                    tags.add(token["tag"])

    UD_TAGS = [
        "ADJ",
        "ADP",
        "ADV",
        "AUX",
        "CCONJ",
        "DET",
        "INTJ",
        "NOUN",
        "NUM",
        "PART",
        "PRON",
        "PROPN",
        "PUNCT",
        "SCONJ",
        "SYM",
        "VERB",
        "X",
    ]

    VAL_NORM_MAP = {
        "0": "None",
        "1": "One",
        "2": "Two",
        "3": "Three",
    }

    tag_map = {}
    for tag in tags:
        tagparts = tag.split("__")
        pos = tagparts[0]
        posparts = pos.split("_")
        if posparts[0] not in UD_TAGS:
            msg.fail("Can't automatically map the following tag to a UD coarse-grained POS: " + tag, exits=1)
        tag_map[tag] = {"POS": posparts[0]}
        if len(tagparts) > 1:
            for morph in tagparts[1].split("|"):
                morph_feat, morph_val = morph.split("=")
                if morph_val in VAL_NORM_MAP:
                    morph_val = VAL_NORM_MAP[morph_val]
                feature_name = morph_feat + "_" + morph_val.lower()
                if feature_name not in FEATURES:
                    msg.fail("Unsupported morphological feature " + feature_name + ": " + tag, exits=1)
                tag_map[tag][morph_feat] = morph_val

    srsly.write_json(tag_map_path, tag_map)
