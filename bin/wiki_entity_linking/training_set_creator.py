# coding: utf-8
from __future__ import unicode_literals

import logging
import random
import re
import bz2
import json

from functools import partial

from spacy.gold import GoldParse
from bin.wiki_entity_linking import kb_creator

"""
Process Wikipedia interlinks to generate a training dataset for the EL algorithm.
Gold-standard entities are stored in one file in standoff format (by character offset).
"""

ENTITY_FILE = "gold_entities.csv"
logger = logging.getLogger(__name__)


def create_training_examples_and_descriptions(wikipedia_input,
                                              entity_def_input,
                                              description_output,
                                              training_output,
                                              parse_descriptions,
                                              limit=None):
    wp_to_id = kb_creator.get_entity_to_id(entity_def_input)
    _process_wikipedia_texts(wikipedia_input,
                             wp_to_id,
                             description_output,
                             training_output,
                             parse_descriptions,
                             limit)


def _process_wikipedia_texts(wikipedia_input,
                             wp_to_id,
                             output,
                             training_output,
                             parse_descriptions,
                             limit=None):
    """
    Read the XML wikipedia data to parse out training data:
    raw text data + positive instances
    """
    title_regex = re.compile(r"(?<=<title>).*(?=</title>)")
    id_regex = re.compile(r"(?<=<id>)\d*(?=</id>)")

    read_ids = set()

    with output.open("a", encoding="utf8") as descr_file, training_output.open("w", encoding="utf8") as entity_file:
        if parse_descriptions:
            _write_training_description(descr_file, "WD_id", "description")
        with bz2.open(wikipedia_input, mode="rb") as file:
            article_count = 0
            article_text = ""
            article_title = None
            article_id = None
            reading_text = False
            reading_revision = False

            logger.info("Processed {} articles".format(article_count))

            for line in file:
                clean_line = line.strip().decode("utf-8")

                if clean_line == "<revision>":
                    reading_revision = True
                elif clean_line == "</revision>":
                    reading_revision = False

                # Start reading new page
                if clean_line == "<page>":
                    article_text = ""
                    article_title = None
                    article_id = None
                # finished reading this page
                elif clean_line == "</page>":
                    if article_id:
                        clean_text, entities = _process_wp_text(
                            article_title,
                            article_text,
                            wp_to_id
                        )
                        if clean_text is not None and entities is not None:
                            _write_training_entities(entity_file,
                                                     article_id,
                                                     clean_text,
                                                     entities)

                            if article_title in wp_to_id and parse_descriptions:
                                description = " ".join(clean_text[:1000].split(" ")[:-1])
                                _write_training_description(
                                    descr_file,
                                    wp_to_id[article_title],
                                    description
                                )
                            article_count += 1
                            if article_count % 10000 == 0:
                                logger.info("Processed {} articles".format(article_count))
                            if limit and article_count >= limit:
                                break
                    article_text = ""
                    article_title = None
                    article_id = None
                    reading_text = False
                    reading_revision = False

                # start reading text within a page
                if "<text" in clean_line:
                    reading_text = True

                if reading_text:
                    article_text += " " + clean_line

                # stop reading text within a page (we assume a new page doesn't start on the same line)
                if "</text" in clean_line:
                    reading_text = False

                # read the ID of this article (outside the revision portion of the document)
                if not reading_revision:
                    ids = id_regex.search(clean_line)
                    if ids:
                        article_id = ids[0]
                        if article_id in read_ids:
                            logger.info(
                                "Found duplicate article ID", article_id, clean_line
                            )  # This should never happen ...
                        read_ids.add(article_id)

                # read the title of this article (outside the revision portion of the document)
                if not reading_revision:
                    titles = title_regex.search(clean_line)
                    if titles:
                        article_title = titles[0].strip()
    logger.info("Finished. Processed {} articles".format(article_count))


text_regex = re.compile(r"(?<=<text xml:space=\"preserve\">).*(?=</text)")
info_regex = re.compile(r"{[^{]*?}")
htlm_regex = re.compile(r"&lt;!--[^-]*--&gt;")
category_regex = re.compile(r"\[\[Category:[^\[]*]]")
file_regex = re.compile(r"\[\[File:[^[\]]+]]")
ref_regex = re.compile(r"&lt;ref.*?&gt;")  # non-greedy
ref_2_regex = re.compile(r"&lt;/ref.*?&gt;")  # non-greedy


def _process_wp_text(article_title, article_text, wp_to_id):
    # ignore meta Wikipedia pages
    if (
        article_title.startswith("Wikipedia:") or
        article_title.startswith("Kategori:")
    ):
        return None, None

    # remove the text tags
    text_search = text_regex.search(article_text)
    if text_search is None:
        return None, None
    text = text_search.group(0)

    # stop processing if this is a redirect page
    if text.startswith("#REDIRECT"):
        return None, None

    # get the raw text without markup etc, keeping only interwiki links
    clean_text, entities = _remove_links(_get_clean_wp_text(text), wp_to_id)
    return clean_text, entities


def _get_clean_wp_text(article_text):
    clean_text = article_text.strip()

    # remove bolding & italic markup
    clean_text = clean_text.replace("'''", "")
    clean_text = clean_text.replace("''", "")

    # remove nested {{info}} statements by removing the inner/smallest ones first and iterating
    try_again = True
    previous_length = len(clean_text)
    while try_again:
        clean_text = info_regex.sub(
            "", clean_text
        )  # non-greedy match excluding a nested {
        if len(clean_text) < previous_length:
            try_again = True
        else:
            try_again = False
        previous_length = len(clean_text)

    # remove HTML comments
    clean_text = htlm_regex.sub("", clean_text)

    # remove Category and File statements
    clean_text = category_regex.sub("", clean_text)
    clean_text = file_regex.sub("", clean_text)

    # remove multiple =
    while "==" in clean_text:
        clean_text = clean_text.replace("==", "=")

    clean_text = clean_text.replace(". =", ".")
    clean_text = clean_text.replace(" = ", ". ")
    clean_text = clean_text.replace("= ", ".")
    clean_text = clean_text.replace(" =", "")

    # remove refs (non-greedy match)
    clean_text = ref_regex.sub("", clean_text)
    clean_text = ref_2_regex.sub("", clean_text)

    # remove additional wikiformatting
    clean_text = re.sub(r"&lt;blockquote&gt;", "", clean_text)
    clean_text = re.sub(r"&lt;/blockquote&gt;", "", clean_text)

    # change special characters back to normal ones
    clean_text = clean_text.replace(r"&lt;", "<")
    clean_text = clean_text.replace(r"&gt;", ">")
    clean_text = clean_text.replace(r"&quot;", '"')
    clean_text = clean_text.replace(r"&amp;nbsp;", " ")
    clean_text = clean_text.replace(r"&amp;", "&")

    # remove multiple spaces
    while "  " in clean_text:
        clean_text = clean_text.replace("  ", " ")

    return clean_text.strip()


def _remove_links(clean_text, wp_to_id):
    # read the text char by char to get the right offsets for the interwiki links
    entities = []
    final_text = ""
    open_read = 0
    reading_text = True
    reading_entity = False
    reading_mention = False
    reading_special_case = False
    entity_buffer = ""
    mention_buffer = ""
    for index, letter in enumerate(clean_text):
        if letter == "[":
            open_read += 1
        elif letter == "]":
            open_read -= 1
        elif letter == "|":
            if reading_text:
                final_text += letter
            # switch from reading entity to mention in the [[entity|mention]] pattern
            elif reading_entity:
                reading_text = False
                reading_entity = False
                reading_mention = True
            else:
                reading_special_case = True
        else:
            if reading_entity:
                entity_buffer += letter
            elif reading_mention:
                mention_buffer += letter
            elif reading_text:
                final_text += letter
            else:
                raise ValueError("Not sure at point", clean_text[index - 2: index + 2])

        if open_read > 2:
            reading_special_case = True

        if open_read == 2 and reading_text:
            reading_text = False
            reading_entity = True
            reading_mention = False

        # we just finished reading an entity
        if open_read == 0 and not reading_text:
            if "#" in entity_buffer or entity_buffer.startswith(":"):
                reading_special_case = True
            # Ignore cases with nested structures like File: handles etc
            if not reading_special_case:
                if not mention_buffer:
                    mention_buffer = entity_buffer
                start = len(final_text)
                end = start + len(mention_buffer)
                qid = wp_to_id.get(entity_buffer, None)
                if qid:
                    entities.append((mention_buffer, qid, start, end))
                final_text += mention_buffer

            entity_buffer = ""
            mention_buffer = ""

            reading_text = True
            reading_entity = False
            reading_mention = False
            reading_special_case = False
    return final_text, entities


def _write_training_description(outputfile, qid, description):
    if description is not None:
        line = str(qid) + "|" + description + "\n"
        outputfile.write(line)


def _write_training_entities(outputfile, article_id, clean_text, entities):
    entities_data = [{"alias": ent[0], "entity": ent[1], "start": ent[2], "end": ent[3]} for ent in entities]
    line = json.dumps(
        {
            "article_id": article_id,
            "clean_text": clean_text,
            "entities": entities_data
        },
        ensure_ascii=False) + "\n"
    outputfile.write(line)


def read_training(nlp, entity_file_path, dev, limit, kb):
    """ This method provides training examples that correspond to the entity annotations found by the nlp object.
     For training,, it will include negative training examples by using the candidate generator,
     and it will only keep positive training examples that can be found by using the candidate generator.
     For testing, it will include all positive examples only."""

    from tqdm import tqdm
    data = []
    num_entities = 0
    get_gold_parse = partial(_get_gold_parse, dev=dev, kb=kb)

    logger.info("Reading {} data with limit {}".format('dev' if dev else 'train', limit))
    with entity_file_path.open("r", encoding="utf8") as file:
        with tqdm(total=limit, leave=False) as pbar:
            for i, line in enumerate(file):
                example = json.loads(line)
                article_id = example["article_id"]
                clean_text = example["clean_text"]
                entities = example["entities"]

                if dev != is_dev(article_id) or len(clean_text) >= 30000:
                    continue

                doc = nlp(clean_text)
                gold = get_gold_parse(doc, entities)
                if gold and len(gold.links) > 0:
                    data.append((doc, gold))
                    num_entities += len(gold.links)
                    pbar.update(len(gold.links))
                if limit and num_entities >= limit:
                    break
    logger.info("Read {} entities in {} articles".format(num_entities, len(data)))
    return data


def _get_gold_parse(doc, entities, dev, kb):
    gold_entities = {}
    tagged_ent_positions = set(
        [(ent.start_char, ent.end_char) for ent in doc.ents]
    )

    for entity in entities:
        entity_id = entity["entity"]
        alias = entity["alias"]
        start = entity["start"]
        end = entity["end"]

        candidates = kb.get_candidates(alias)
        candidate_ids = [
            c.entity_ for c in candidates
        ]

        should_add_ent = (
            dev or
            (
                (start, end) in tagged_ent_positions and
                entity_id in candidate_ids and
                len(candidates) > 1
            )
        )

        if should_add_ent:
            value_by_id = {entity_id: 1.0}
            if not dev:
                random.shuffle(candidate_ids)
                value_by_id.update({
                    kb_id: 0.0
                    for kb_id in candidate_ids
                    if kb_id != entity_id
                })
            gold_entities[(start, end)] = value_by_id

    return GoldParse(doc, links=gold_entities)


def is_dev(article_id):
    return article_id.endswith("3")
