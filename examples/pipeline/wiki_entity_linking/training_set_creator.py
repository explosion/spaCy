# coding: utf-8
from __future__ import unicode_literals

import os
import re
import bz2
import datetime
from os import listdir

from examples.pipeline.wiki_entity_linking import run_el
from spacy.gold import GoldParse
from spacy.matcher import PhraseMatcher
from . import wikipedia_processor as wp, kb_creator

"""
Process Wikipedia interlinks to generate a training dataset for the EL algorithm
"""

ENTITY_FILE = "gold_entities.csv"


def create_training(kb, entity_def_input, training_output):
    if not kb:
        raise ValueError("kb should be defined")
    wp_to_id = kb_creator._get_entity_to_id(entity_def_input)
    _process_wikipedia_texts(kb, wp_to_id, training_output, limit=100000000)  # TODO: full dataset


def _process_wikipedia_texts(kb, wp_to_id, training_output, limit=None):
    """
    Read the XML wikipedia data to parse out training data:
    raw text data + positive and negative instances
    """

    title_regex = re.compile(r'(?<=<title>).*(?=</title>)')
    id_regex = re.compile(r'(?<=<id>)\d*(?=</id>)')

    read_ids = set()

    entityfile_loc = training_output + "/" + ENTITY_FILE
    with open(entityfile_loc, mode="w", encoding='utf8') as entityfile:
        # write entity training header file
        _write_training_entity(outputfile=entityfile,
                               article_id="article_id",
                               alias="alias",
                               entity="entity",
                               correct="correct")

        with bz2.open(wp.ENWIKI_DUMP, mode='rb') as file:
            line = file.readline()
            cnt = 0
            article_text = ""
            article_title = None
            article_id = None
            reading_text = False
            reading_revision = False
            while line and (not limit or cnt < limit):
                if cnt % 1000000 == 0:
                    print(datetime.datetime.now(), "processed", cnt, "lines of Wikipedia dump")
                clean_line = line.strip().decode("utf-8")
                # print(clean_line)

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
                        try:
                            _process_wp_text(kb, wp_to_id, entityfile, article_id, article_text.strip(), training_output)
                        # on a previous run, an error occurred after 46M lines and 2h
                        except Exception as e:
                            print("Error processing article", article_id, article_title, e)
                    else:
                        print("Done processing a page, but couldn't find an article_id ?")
                        print(article_title)
                        print(article_text)
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
                            print("Found duplicate article ID", article_id, clean_line)  # This should never happen ...
                        read_ids.add(article_id)

                # read the title of this article  (outside the revision portion of the document)
                if not reading_revision:
                    titles = title_regex.search(clean_line)
                    if titles:
                        article_title = titles[0].strip()

                line = file.readline()
                cnt += 1


text_regex = re.compile(r'(?<=<text xml:space=\"preserve\">).*(?=</text)')


def _process_wp_text(kb, wp_to_id, entityfile, article_id, article_text, training_output):
    # remove the text tags
    text = text_regex.search(article_text).group(0)

    # stop processing if this is a redirect page
    if text.startswith("#REDIRECT"):
        return

    # print("WP article", article_id, ":", article_title)
    # print()
    # print(text)

    # get the raw text without markup etc
    clean_text = _get_clean_wp_text(text)
    # print()
    # print(clean_text)

    article_dict = dict()
    ambiguous_aliases = set()
    aliases, entities, normalizations = wp.get_wp_links(text)
    for alias, entity, norm in zip(aliases, entities, normalizations):
        if alias not in ambiguous_aliases:
            entity_id = wp_to_id.get(entity)
            if entity_id:
                # TODO: take care of these conflicts ! Currently they are being removed from the dataset
                if article_dict.get(alias) and article_dict[alias] != entity_id:
                    ambiguous_aliases.add(alias)
                    article_dict.pop(alias)
                    # print("Found conflicting alias", alias, "in article", article_id, article_title)
                else:
                    article_dict[alias] = entity_id

    # print("found entities:")
    for alias, entity in article_dict.items():
        # print(alias, "-->", entity)
        candidates = kb.get_candidates(alias)

        # as training data, we only store entities that are sufficiently ambiguous
        if len(candidates) > 1:
            _write_training_article(article_id=article_id, clean_text=clean_text, training_output=training_output)
            # print("alias", alias)

            # print all incorrect candidates
            for c in candidates:
                if entity != c.entity_:
                    _write_training_entity(outputfile=entityfile,
                                           article_id=article_id,
                                           alias=alias,
                                           entity=c.entity_,
                                           correct="0")

            # print the one correct candidate
            _write_training_entity(outputfile=entityfile,
                                   article_id=article_id,
                                   alias=alias,
                                   entity=entity,
                                   correct="1")

            # print("gold entity", entity)
            # print()

    # _run_ner_depr(nlp, clean_text, article_dict)
    # print()


info_regex = re.compile(r'{[^{]*?}')
interwiki_regex = re.compile(r'\[\[([^|]*?)]]')
interwiki_2_regex = re.compile(r'\[\[[^|]*?\|([^|]*?)]]')
htlm_regex = re.compile(r'&lt;!--[^!]*--&gt;')
category_regex = re.compile(r'\[\[Category:[^\[]*]]')
file_regex = re.compile(r'\[\[File:[^[\]]+]]')
ref_regex = re.compile(r'&lt;ref.*?&gt;')     # non-greedy
ref_2_regex = re.compile(r'&lt;/ref.*?&gt;')  # non-greedy


def _get_clean_wp_text(article_text):
    clean_text = article_text.strip()

    # remove bolding & italic markup
    clean_text = clean_text.replace('\'\'\'', '')
    clean_text = clean_text.replace('\'\'', '')

    # remove nested {{info}} statements by removing the inner/smallest ones first and iterating
    try_again = True
    previous_length = len(clean_text)
    while try_again:
        clean_text = info_regex.sub('', clean_text)  # non-greedy match excluding a nested {
        if len(clean_text) < previous_length:
            try_again = True
        else:
            try_again = False
        previous_length = len(clean_text)

    # remove simple interwiki links (no alternative name)
    clean_text = interwiki_regex.sub(r'\1', clean_text)

    # remove simple interwiki links by picking the alternative name
    clean_text = interwiki_2_regex.sub(r'\1', clean_text)

    # remove HTML comments
    clean_text = htlm_regex.sub('', clean_text)

    # remove Category and File statements
    clean_text = category_regex.sub('', clean_text)
    clean_text = file_regex.sub('', clean_text)

    # remove multiple =
    while '==' in clean_text:
        clean_text = clean_text.replace("==", "=")

    clean_text = clean_text.replace(". =", ".")
    clean_text = clean_text.replace(" = ", ". ")
    clean_text = clean_text.replace("= ", ".")
    clean_text = clean_text.replace(" =", "")

    # remove refs (non-greedy match)
    clean_text = ref_regex.sub('', clean_text)
    clean_text = ref_2_regex.sub('', clean_text)

    # remove additional wikiformatting
    clean_text = re.sub(r'&lt;blockquote&gt;', '', clean_text)
    clean_text = re.sub(r'&lt;/blockquote&gt;', '', clean_text)

    # change special characters back to normal ones
    clean_text = clean_text.replace(r'&lt;', '<')
    clean_text = clean_text.replace(r'&gt;', '>')
    clean_text = clean_text.replace(r'&quot;', '"')
    clean_text = clean_text.replace(r'&amp;nbsp;', ' ')
    clean_text = clean_text.replace(r'&amp;', '&')

    # remove multiple spaces
    while '  ' in clean_text:
        clean_text = clean_text.replace('  ', ' ')

    return clean_text.strip()


def _write_training_article(article_id, clean_text, training_output):
    file_loc = training_output + "/" + str(article_id) + ".txt"
    with open(file_loc, mode='w', encoding='utf8') as outputfile:
        outputfile.write(clean_text)


def _write_training_entity(outputfile, article_id, alias, entity, correct):
    outputfile.write(article_id + "|" + alias + "|" + entity + "|" + correct + "\n")


def read_training_entities(training_output, collect_correct=True, collect_incorrect=False):
    entityfile_loc = training_output + "/" + ENTITY_FILE
    incorrect_entries_per_article = dict()
    correct_entries_per_article = dict()
    with open(entityfile_loc, mode='r', encoding='utf8') as file:
        for line in file:
            fields = line.replace('\n', "").split(sep='|')
            article_id = fields[0]
            alias = fields[1]
            entity = fields[2]
            correct = fields[3]

            if correct == "1" and collect_correct:
                entry_dict = correct_entries_per_article.get(article_id, dict())
                if alias in entry_dict:
                    raise ValueError("Found alias", alias, "multiple times for article", article_id, "in", ENTITY_FILE)
                entry_dict[alias] = entity
                correct_entries_per_article[article_id] = entry_dict

            if correct == "0" and collect_incorrect:
                entry_dict = incorrect_entries_per_article.get(article_id, dict())
                entities = entry_dict.get(alias, set())
                entities.add(entity)
                entry_dict[alias] = entities
                incorrect_entries_per_article[article_id] = entry_dict

    return correct_entries_per_article, incorrect_entries_per_article


def read_training(nlp, training_dir, id_to_descr, doc_cutoff, dev, limit, to_print):
    correct_entries, incorrect_entries = read_training_entities(training_output=training_dir,
                                                                collect_correct=True,
                                                                collect_incorrect=True)

    data = []

    cnt = 0
    next_entity_nr = 1
    files = listdir(training_dir)
    for f in files:
        if not limit or cnt < limit:
            if dev == run_el.is_dev(f):
                article_id = f.replace(".txt", "")
                if cnt % 500 == 0 and to_print:
                    print(datetime.datetime.now(), "processed", cnt, "files in the training dataset")

                try:
                    # parse the article text
                    with open(os.path.join(training_dir, f), mode="r", encoding='utf8') as file:
                        text = file.read()
                        article_doc = nlp(text)
                        truncated_text = text[0:min(doc_cutoff, len(text))]

                    gold_entities = list()

                    # process all positive and negative entities, collect all relevant mentions in this article
                    for mention, entity_pos in correct_entries[article_id].items():
                        # find all matches in the doc for the mentions
                        # TODO: fix this - doesn't look like all entities are found
                        matcher = PhraseMatcher(nlp.vocab)
                        patterns = list(nlp.tokenizer.pipe([mention]))

                        matcher.add("TerminologyList", None, *patterns)
                        matches = matcher(article_doc)

                        # store gold entities
                        for match_id, start, end in matches:
                            gold_entities.append((start, end, entity_pos))

                    gold = GoldParse(doc=article_doc, links=gold_entities)
                    data.append((article_doc, gold))

                    cnt += 1
                except Exception as e:
                    print("Problem parsing article", article_id)
                    print(e)

    if to_print:
        print()
        print("Processed", cnt, "training articles, dev=" + str(dev))
        print()
    return data




