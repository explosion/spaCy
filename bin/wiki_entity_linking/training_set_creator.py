# coding: utf-8
from __future__ import unicode_literals

import os
import re
import bz2
import datetime

from spacy.gold import GoldParse
from bin.wiki_entity_linking import kb_creator

"""
Process Wikipedia interlinks to generate a training dataset for the EL algorithm.
Gold-standard entities are stored in one file in standoff format (by character offset).
"""

ENTITY_FILE = "gold_entities.csv"


def create_training(wikipedia_input, entity_def_input, training_output):
    wp_to_id = kb_creator.get_entity_to_id(entity_def_input)
    _process_wikipedia_texts(wikipedia_input, wp_to_id, training_output, limit=None)


def _process_wikipedia_texts(wikipedia_input, wp_to_id, training_output, limit=None):
    """
    Read the XML wikipedia data to parse out training data:
    raw text data + positive instances
    """
    title_regex = re.compile(r'(?<=<title>).*(?=</title>)')
    id_regex = re.compile(r'(?<=<id>)\d*(?=</id>)')

    read_ids = set()
    entityfile_loc = training_output / ENTITY_FILE
    with open(entityfile_loc, mode="w", encoding='utf8') as entityfile:
        # write entity training header file
        _write_training_entity(outputfile=entityfile,
                               article_id="article_id",
                               alias="alias",
                               entity="WD_id",
                               start="start",
                               end="end")

        with bz2.open(wikipedia_input, mode='rb') as file:
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
                            _process_wp_text(wp_to_id, entityfile, article_id, article_title, article_text.strip(),
                                             training_output)
                        except Exception as e:
                            print("Error processing article", article_id, article_title, e)
                    else:
                        print("Done processing a page, but couldn't find an article_id ?", article_title)
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

                # read the title of this article (outside the revision portion of the document)
                if not reading_revision:
                    titles = title_regex.search(clean_line)
                    if titles:
                        article_title = titles[0].strip()

                line = file.readline()
                cnt += 1


text_regex = re.compile(r'(?<=<text xml:space=\"preserve\">).*(?=</text)')


def _process_wp_text(wp_to_id, entityfile, article_id, article_title, article_text, training_output):
    found_entities = False

    # ignore meta Wikipedia pages
    if article_title.startswith("Wikipedia:"):
        return

    # remove the text tags
    text = text_regex.search(article_text).group(0)

    # stop processing if this is a redirect page
    if text.startswith("#REDIRECT"):
        return

    # get the raw text without markup etc, keeping only interwiki links
    clean_text = _get_clean_wp_text(text)

    # read the text char by char to get the right offsets for the interwiki links
    final_text = ""
    open_read = 0
    reading_text = True
    reading_entity = False
    reading_mention = False
    reading_special_case = False
    entity_buffer = ""
    mention_buffer = ""
    for index, letter in enumerate(clean_text):
        if letter == '[':
            open_read += 1
        elif letter == ']':
            open_read -= 1
        elif letter == '|':
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
                raise ValueError("Not sure at point", clean_text[index-2:index+2])

        if open_read > 2:
            reading_special_case = True

        if open_read == 2 and reading_text:
            reading_text = False
            reading_entity = True
            reading_mention = False

        # we just finished reading an entity
        if open_read == 0 and not reading_text:
            if '#' in entity_buffer or entity_buffer.startswith(':'):
                reading_special_case = True
            # Ignore cases with nested structures like File: handles etc
            if not reading_special_case:
                if not mention_buffer:
                    mention_buffer = entity_buffer
                start = len(final_text)
                end = start + len(mention_buffer)
                qid = wp_to_id.get(entity_buffer, None)
                if qid:
                    _write_training_entity(outputfile=entityfile,
                                           article_id=article_id,
                                           alias=mention_buffer,
                                           entity=qid,
                                           start=start,
                                           end=end)
                found_entities = True
                final_text += mention_buffer

            entity_buffer = ""
            mention_buffer = ""

            reading_text = True
            reading_entity = False
            reading_mention = False
            reading_special_case = False

    if found_entities:
        _write_training_article(article_id=article_id, clean_text=final_text, training_output=training_output)


info_regex = re.compile(r'{[^{]*?}')
htlm_regex = re.compile(r'&lt;!--[^-]*--&gt;')
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
    file_loc = training_output / str(article_id) + ".txt"
    with open(file_loc, mode='w', encoding='utf8') as outputfile:
        outputfile.write(clean_text)


def _write_training_entity(outputfile, article_id, alias, entity, start, end):
    outputfile.write(article_id + "|" + alias + "|" + entity + "|" + str(start) + "|" + str(end) + "\n")


def is_dev(article_id):
    return article_id.endswith("3")


def read_training(nlp, training_dir, dev, limit):
    # This method provides training examples that correspond to the entity annotations found by the nlp object
    entityfile_loc = training_dir / ENTITY_FILE
    data = []

    # assume the data is written sequentially, so we can reuse the article docs
    current_article_id = None
    current_doc = None
    ents_by_offset = dict()
    skip_articles = set()
    total_entities = 0

    with open(entityfile_loc, mode='r', encoding='utf8') as file:
        for line in file:
            if not limit or len(data) < limit:
                fields = line.replace('\n', "").split(sep='|')
                article_id = fields[0]
                alias = fields[1]
                wp_title = fields[2]
                start = fields[3]
                end = fields[4]

                if dev == is_dev(article_id) and article_id != "article_id" and article_id not in skip_articles:
                    if not current_doc or (current_article_id != article_id):
                        # parse the new article text
                        file_name = article_id + ".txt"
                        try:
                            with open(os.path.join(training_dir, file_name), mode="r", encoding='utf8') as f:
                                text = f.read()
                                if len(text) < 30000:   # threshold for convenience / speed of processing
                                    current_doc = nlp(text)
                                    current_article_id = article_id
                                    ents_by_offset = dict()
                                    for ent in current_doc.ents:
                                        sent_length = len(ent.sent)
                                        # custom filtering to avoid too long or too short sentences
                                        if 5 < sent_length < 100:
                                            ents_by_offset[str(ent.start_char) + "_" + str(ent.end_char)] = ent
                                else:
                                    skip_articles.add(article_id)
                                    current_doc = None
                        except Exception as e:
                            print("Problem parsing article", article_id, e)
                            skip_articles.add(article_id)
                            raise e

                    # repeat checking this condition in case an exception was thrown
                    if current_doc and (current_article_id == article_id):
                        found_ent = ents_by_offset.get(start + "_" + end,  None)
                        if found_ent:
                            if found_ent.text != alias:
                                skip_articles.add(article_id)
                                current_doc = None
                            else:
                                sent = found_ent.sent.as_doc()
                                # currently feeding the gold data one entity per sentence at a time
                                gold_start = int(start) - found_ent.sent.start_char
                                gold_end = int(end) - found_ent.sent.start_char
                                gold_entities = [(gold_start, gold_end, wp_title)]
                                gold = GoldParse(doc=sent, links=gold_entities)
                                data.append((sent, gold))
                                total_entities += 1
                                if len(data) % 2500 == 0:
                                    print(" -read", total_entities, "entities")

    print(" -read", total_entities, "entities")
    return data
