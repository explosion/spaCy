# coding: utf-8
from __future__ import unicode_literals

import re
import bz2
import logging
import random
import json

from spacy.gold import GoldParse
from bin.wiki_entity_linking import wiki_io as io
from bin.wiki_entity_linking.wiki_namespaces import (
    WP_META_NAMESPACE,
    WP_FILE_NAMESPACE,
    WP_CATEGORY_NAMESPACE,
)

"""
Process a Wikipedia dump to calculate entity frequencies and prior probabilities in combination with certain mentions.
Write these results to file for downstream KB and training data generation.

Process Wikipedia interlinks to generate a training dataset for the EL algorithm.
"""

ENTITY_FILE = "gold_entities.csv"

map_alias_to_link = dict()

logger = logging.getLogger(__name__)

title_regex = re.compile(r"(?<=<title>).*(?=</title>)")
id_regex = re.compile(r"(?<=<id>)\d*(?=</id>)")
text_regex = re.compile(r"(?<=<text xml:space=\"preserve\">).*(?=</text)")
info_regex = re.compile(r"{[^{]*?}")
html_regex = re.compile(r"&lt;!--[^-]*--&gt;")
ref_regex = re.compile(r"&lt;ref.*?&gt;")  # non-greedy
ref_2_regex = re.compile(r"&lt;/ref.*?&gt;")  # non-greedy

# find the links
link_regex = re.compile(r"\[\[[^\[\]]*\]\]")

# match on interwiki links, e.g. `en:` or `:fr:`
ns_regex = r":?" + "[a-z][a-z]" + ":"
# match on Namespace: optionally preceded by a :
for ns in WP_META_NAMESPACE:
    ns_regex += "|" + ":?" + ns + ":"
ns_regex = re.compile(ns_regex, re.IGNORECASE)

files = r""
for f in WP_FILE_NAMESPACE:
    files += "\[\[" + f + ":[^[\]]+]]" + "|"
files = files[0 : len(files) - 1]
file_regex = re.compile(files)

cats = r""
for c in WP_CATEGORY_NAMESPACE:
    cats += "\[\[" + c + ":[^\[]*]]" + "|"
cats = cats[0 : len(cats) - 1]
category_regex = re.compile(cats)


def read_prior_probs(wikipedia_input, prior_prob_output, limit=None):
    """
    Read the XML wikipedia data and parse out intra-wiki links to estimate prior probabilities.
    The full file takes about 2-3h to parse 1100M lines.
    It works relatively fast because it runs line by line, irrelevant of which article the intrawiki is from,
    though dev test articles are excluded in order not to get an artificially strong baseline.
    """
    cnt = 0
    read_id = False
    current_article_id = None
    with bz2.open(wikipedia_input, mode="rb") as file:
        line = file.readline()
        while line and (not limit or cnt < limit):
            if cnt % 25000000 == 0 and cnt > 0:
                logger.info("processed {} lines of Wikipedia XML dump".format(cnt))
            clean_line = line.strip().decode("utf-8")

            # we attempt at reading the article's ID (but not the revision or contributor ID)
            if "<revision>" in clean_line or "<contributor>" in clean_line:
                read_id = False
            if "<page>" in clean_line:
                read_id = True

            if read_id:
                ids = id_regex.search(clean_line)
                if ids:
                    current_article_id = ids[0]

            # only processing prior probabilities from true training (non-dev) articles
            if not is_dev(current_article_id):
                aliases, entities, normalizations = get_wp_links(clean_line)
                for alias, entity, norm in zip(aliases, entities, normalizations):
                    _store_alias(
                        alias, entity, normalize_alias=norm, normalize_entity=True
                    )

            line = file.readline()
            cnt += 1
        logger.info("processed {} lines of Wikipedia XML dump".format(cnt))
    logger.info("Finished. processed {} lines of Wikipedia XML dump".format(cnt))

    # write all aliases and their entities and count occurrences to file
    with prior_prob_output.open("w", encoding="utf8") as outputfile:
        outputfile.write("alias" + "|" + "count" + "|" + "entity" + "\n")
        for alias, alias_dict in sorted(map_alias_to_link.items(), key=lambda x: x[0]):
            s_dict = sorted(alias_dict.items(), key=lambda x: x[1], reverse=True)
            for entity, count in s_dict:
                outputfile.write(alias + "|" + str(count) + "|" + entity + "\n")


def _store_alias(alias, entity, normalize_alias=False, normalize_entity=True):
    alias = alias.strip()
    entity = entity.strip()

    # remove everything after # as this is not part of the title but refers to a specific paragraph
    if normalize_entity:
        # wikipedia titles are always capitalized
        entity = _capitalize_first(entity.split("#")[0])
    if normalize_alias:
        alias = alias.split("#")[0]

    if alias and entity:
        alias_dict = map_alias_to_link.get(alias, dict())
        entity_count = alias_dict.get(entity, 0)
        alias_dict[entity] = entity_count + 1
        map_alias_to_link[alias] = alias_dict


def get_wp_links(text):
    aliases = []
    entities = []
    normalizations = []

    matches = link_regex.findall(text)
    for match in matches:
        match = match[2:][:-2].replace("_", " ").strip()

        if ns_regex.match(match):
            pass  # ignore the entity if it points to a "meta" page

        # this is a simple [[link]], with the alias the same as the mention
        elif "|" not in match:
            aliases.append(match)
            entities.append(match)
            normalizations.append(True)

        # in wiki format, the link is written as [[entity|alias]]
        else:
            splits = match.split("|")
            entity = splits[0].strip()
            alias = splits[1].strip()
            # specific wiki format  [[alias (specification)|]]
            if len(alias) == 0 and "(" in entity:
                alias = entity.split("(")[0]
                aliases.append(alias)
                entities.append(entity)
                normalizations.append(False)
            else:
                aliases.append(alias)
                entities.append(entity)
                normalizations.append(False)

    return aliases, entities, normalizations


def _capitalize_first(text):
    if not text:
        return None
    result = text[0].capitalize()
    if len(result) > 0:
        result += text[1:]
    return result


def create_training_and_desc(
    wp_input, def_input, desc_output, training_output, parse_desc, limit=None
):
    wp_to_id = io.read_title_to_id(def_input)
    _process_wikipedia_texts(
        wp_input, wp_to_id, desc_output, training_output, parse_desc, limit
    )


def _process_wikipedia_texts(
    wikipedia_input, wp_to_id, output, training_output, parse_descriptions, limit=None
):
    """
    Read the XML wikipedia data to parse out training data:
    raw text data + positive instances
    """

    read_ids = set()

    with output.open("a", encoding="utf8") as descr_file, training_output.open(
        "w", encoding="utf8"
    ) as entity_file:
        if parse_descriptions:
            _write_training_description(descr_file, "WD_id", "description")
        with bz2.open(wikipedia_input, mode="rb") as file:
            article_count = 0
            article_text = ""
            article_title = None
            article_id = None
            reading_text = False
            reading_revision = False

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
                            article_title, article_text, wp_to_id
                        )
                        if clean_text is not None and entities is not None:
                            _write_training_entities(
                                entity_file, article_id, clean_text, entities
                            )

                            if article_title in wp_to_id and parse_descriptions:
                                description = " ".join(
                                    clean_text[:1000].split(" ")[:-1]
                                )
                                _write_training_description(
                                    descr_file, wp_to_id[article_title], description
                                )
                            article_count += 1
                            if article_count % 10000 == 0 and article_count > 0:
                                logger.info(
                                    "Processed {} articles".format(article_count)
                                )
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


def _process_wp_text(article_title, article_text, wp_to_id):
    # ignore meta Wikipedia pages
    if ns_regex.match(article_title):
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
    clean_text = html_regex.sub("", clean_text)

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
                raise ValueError("Not sure at point", clean_text[index - 2 : index + 2])

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
    entities_data = [
        {"alias": ent[0], "entity": ent[1], "start": ent[2], "end": ent[3]}
        for ent in entities
    ]
    line = (
        json.dumps(
            {
                "article_id": article_id,
                "clean_text": clean_text,
                "entities": entities_data,
            },
            ensure_ascii=False,
        )
        + "\n"
    )
    outputfile.write(line)


def read_training_indices(entity_file_path):
    """ This method creates two lists of indices into the training file: one with indices for the
     training examples, and one for the dev examples."""
    train_indices = []
    dev_indices = []

    with entity_file_path.open("r", encoding="utf8") as file:
        for i, line in enumerate(file):
            example = json.loads(line)
            article_id = example["article_id"]
            clean_text = example["clean_text"]

            if is_valid_article(clean_text):
                if is_dev(article_id):
                    dev_indices.append(i)
                else:
                    train_indices.append(i)

    return train_indices, dev_indices


def read_el_docs_golds(nlp, entity_file_path, dev, line_ids, kb, labels_discard=None):
    """ This method provides training/dev examples that correspond to the entity annotations found by the nlp object.
     For training, it will include both positive and negative examples by using the candidate generator from the kb.
     For testing (kb=None), it will include all positive examples only."""
    if not labels_discard:
        labels_discard = []

    texts = []
    entities_list = []

    with entity_file_path.open("r", encoding="utf8") as file:
        for i, line in enumerate(file):
            if i in line_ids:
                example = json.loads(line)
                article_id = example["article_id"]
                clean_text = example["clean_text"]
                entities = example["entities"]

                if dev != is_dev(article_id) or not is_valid_article(clean_text):
                    continue

                texts.append(clean_text)
                entities_list.append(entities)

    docs = nlp.pipe(texts, batch_size=50)

    for doc, entities in zip(docs, entities_list):
        gold = _get_gold_parse(doc, entities, dev=dev, kb=kb, labels_discard=labels_discard)
        if gold and len(gold.links) > 0:
            yield doc, gold


def _get_gold_parse(doc, entities, dev, kb, labels_discard):
    gold_entities = {}
    tagged_ent_positions = {
        (ent.start_char, ent.end_char): ent
        for ent in doc.ents
        if ent.label_ not in labels_discard
    }

    for entity in entities:
        entity_id = entity["entity"]
        alias = entity["alias"]
        start = entity["start"]
        end = entity["end"]

        candidate_ids = []
        if kb and not dev:
            candidates = kb.get_candidates(alias)
            candidate_ids = [cand.entity_ for cand in candidates]

        tagged_ent = tagged_ent_positions.get((start, end), None)
        if tagged_ent:
            # TODO: check that alias == doc.text[start:end]
            should_add_ent = (dev or entity_id in candidate_ids) and is_valid_sentence(
                tagged_ent.sent.text
            )

            if should_add_ent:
                value_by_id = {entity_id: 1.0}
                if not dev:
                    random.shuffle(candidate_ids)
                    value_by_id.update(
                        {kb_id: 0.0 for kb_id in candidate_ids if kb_id != entity_id}
                    )
                gold_entities[(start, end)] = value_by_id

    return GoldParse(doc, links=gold_entities)


def is_dev(article_id):
    if not article_id:
        return False
    return article_id.endswith("3")


def is_valid_article(doc_text):
    # custom length cut-off
    return 10 < len(doc_text) < 30000


def is_valid_sentence(sent_text):
    if not 10 < len(sent_text) < 3000:
        # custom length cut-off
        return False

    if sent_text.strip().startswith("*") or sent_text.strip().startswith("#"):
        # remove 'enumeration' sentences (occurs often on Wikipedia)
        return False

    return True
