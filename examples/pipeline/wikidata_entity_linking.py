# coding: utf-8
from __future__ import unicode_literals

"""
Demonstrate how to build a knowledge base from WikiData and run an Entity Linking algorithm.
"""
import re
import csv
import json
import spacy
import datetime
import bz2
from spacy.kb import KnowledgeBase
from spacy.vocab import Vocab

# TODO: remove hardcoded paths
WIKIDATA_JSON = 'C:/Users/Sofie/Documents/data/wikidata/wikidata-20190304-all.json.bz2'
ENWIKI_DUMP = 'C:/Users/Sofie/Documents/data/wikipedia/enwiki-20190320-pages-articles-multistream.xml.bz2'
ENWIKI_INDEX = 'C:/Users/Sofie/Documents/data/wikipedia/enwiki-20190320-pages-articles-multistream-index.txt.bz2'

PRIOR_PROB = 'C:/Users/Sofie/Documents/data/wikipedia/prior_prob.csv'
ENTITY_COUNTS = 'C:/Users/Sofie/Documents/data/wikipedia/entity_freq.csv'

KB_FILE = 'C:/Users/Sofie/Documents/data/wikipedia/kb'
VOCAB_DIR = 'C:/Users/Sofie/Documents/data/wikipedia/vocab'


# these will/should be matched ignoring case
wiki_namespaces = ["b", "betawikiversity", "Book", "c", "Category", "Commons",
                   "d", "dbdump", "download", "Draft", "Education", "Foundation",
                   "Gadget", "Gadget definition", "gerrit", "File", "Help", "Image", "Incubator",
                   "m", "mail", "mailarchive", "media", "MediaWiki", "MediaWiki talk", "Mediawikiwiki",
                   "MediaZilla", "Meta", "Metawikipedia", "Module",
                   "mw", "n", "nost", "oldwikisource", "outreach", "outreachwiki", "otrs", "OTRSwiki",
                   "Portal", "phab", "Phabricator", "Project", "q", "quality", "rev",
                   "s", "spcom", "Special", "species", "Strategy", "sulutil", "svn",
                   "Talk", "Template", "Template talk", "Testwiki", "ticket", "TimedText", "Toollabs", "tools", "tswiki",
                   "User", "User talk", "v", "voy",
                   "w", "Wikibooks", "Wikidata", "wikiHow", "Wikinvest", "wikilivres", "Wikimedia", "Wikinews",
                   "Wikipedia", "Wikipedia talk", "Wikiquote", "Wikisource", "Wikispecies", "Wikitech",
                   "Wikiversity", "Wikivoyage", "wikt", "wiktionary", "wmf", "wmania", "WP"]

map_alias_to_link = dict()


def create_kb(vocab, max_entities_per_alias, min_occ, to_print=False):
    kb = KnowledgeBase(vocab=vocab)

    print()
    print("1. _read_wikidata_entities", datetime.datetime.now())
    print()
    # title_to_id = _read_wikidata_entities_regex(limit=1000)
    title_to_id = _read_wikidata_entities_json(limit=1000)

    title_list = list(title_to_id.keys())
    entity_list = [title_to_id[x] for x in title_list]

    print()
    print("2. _get_entity_frequencies", datetime.datetime.now())
    print()
    entity_frequencies = _get_entity_frequencies(entities=title_list)

    print()
    print("3. _add_entities", datetime.datetime.now())
    print()
    kb.set_entities(entity_list=entity_list, prob_list=entity_frequencies, vector_list=None, feature_list=None)
    # _add_entities(kb, entities=entity_list, probs=entity_frequencies, to_print=to_print)

    print()
    print("4. _add_aliases", datetime.datetime.now())
    print()
    _add_aliases(kb, title_to_id=title_to_id, max_entities_per_alias=max_entities_per_alias, min_occ=min_occ,)

    # TODO: read wikipedia texts for entity context
    # _read_wikipedia()

    if to_print:
        print()
        print("kb size:", len(kb), kb.get_size_entities(), kb.get_size_aliases())

    print("done with kb", datetime.datetime.now())

    return kb


def _get_entity_frequencies(entities):
    entity_to_count = dict()
    with open(ENTITY_COUNTS, 'r', encoding='utf8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        # skip header
        next(csvreader)
        for row in csvreader:
            entity_to_count[row[0]] = int(row[1])

    return [entity_to_count.get(e, 0) for e in entities]


def _write_entity_counts(to_print=False):
    entity_to_count = dict()
    total_count = 0

    with open(PRIOR_PROB, mode='r', encoding='utf8') as prior_file:
        # skip header
        prior_file.readline()
        line = prior_file.readline()

        while line:
            splits = line.replace('\n', "").split(sep='|')
            # alias = splits[0]
            count = int(splits[1])
            entity = splits[2]

            current_count = entity_to_count.get(entity, 0)
            entity_to_count[entity] = current_count + count

            total_count += count

            line = prior_file.readline()

    with open(ENTITY_COUNTS, mode='w', encoding='utf8') as entity_file:
        entity_file.write("entity" + "|" + "count" + "\n")
        for entity, count in entity_to_count.items():
            entity_file.write(entity + "|" + str(count) + "\n")

    if to_print:
        for entity, count in entity_to_count.items():
            print("Entity count:", entity, count)
        print("Total count:", total_count)


def _add_entities_depr(kb, entities, probs, to_print=False):
    for entity, prob in zip(entities, probs):
        kb.add_entity(entity=entity, prob=prob)

    if to_print:
        print("added", kb.get_size_entities(), "entities:", kb.get_entity_strings())


def _add_aliases(kb, title_to_id, max_entities_per_alias, min_occ, to_print=False):
    wp_titles = title_to_id.keys()

    if to_print:
        print("wp titles:", wp_titles)

    # adding aliases with prior probabilities
    with open(PRIOR_PROB, mode='r', encoding='utf8') as prior_file:
        # skip header
        prior_file.readline()
        line = prior_file.readline()
        # we can read this file sequentially, it's sorted by alias, and then by count
        previous_alias = None
        total_count = 0
        counts = list()
        entities = list()
        while line:
            splits = line.replace('\n', "").split(sep='|')
            new_alias = splits[0]
            count = int(splits[1])
            entity = splits[2]

            if new_alias != previous_alias and previous_alias:
                # done reading the previous alias --> output
                if len(entities) > 0:
                    selected_entities = list()
                    prior_probs = list()
                    for ent_count, ent_string in zip(counts, entities):
                        if ent_string in wp_titles:
                            wd_id = title_to_id[ent_string]
                            p_entity_givenalias = ent_count / total_count
                            selected_entities.append(wd_id)
                            prior_probs.append(p_entity_givenalias)

                    if selected_entities:
                        kb.add_alias(alias=previous_alias, entities=selected_entities, probabilities=prior_probs)
                total_count = 0
                counts = list()
                entities = list()

            total_count += count

            if len(entities) < max_entities_per_alias and count >= min_occ:
                counts.append(count)
                entities.append(entity)
            previous_alias = new_alias

            line = prior_file.readline()

    if to_print:
        print("added", kb.get_size_aliases(), "aliases:", kb.get_alias_strings())


def _read_wikidata_entities_json(limit=None, to_print=False):
    """ Read the JSON wiki data and parse out the entities. Takes about 7u30 to parse 55M lines. """

    languages = {'en', 'de'}
    prop_filter = {'P31': {'Q5', 'Q15632617'}}     # currently defined as OR: one property suffices to be selected
    site_filter = 'enwiki'

    title_to_id = dict()

    # parse appropriate fields - depending on what we need in the KB
    parse_properties = False
    parse_sitelinks = True
    parse_labels = False
    parse_descriptions = False
    parse_aliases = False

    with bz2.open(WIKIDATA_JSON, mode='rb') as file:
        line = file.readline()
        cnt = 0
        while line and (not limit or cnt < limit):
            if cnt % 100000 == 0:
                print(datetime.datetime.now(), "processed", cnt, "lines of WikiData dump")
            clean_line = line.strip()
            if clean_line.endswith(b","):
                clean_line = clean_line[:-1]
            if len(clean_line) > 1:
                obj = json.loads(clean_line)
                entry_type = obj["type"]

                if entry_type == "item":
                    # filtering records on their properties
                    keep = False

                    claims = obj["claims"]
                    for prop, value_set in prop_filter.items():
                        claim_property = claims.get(prop, None)
                        if claim_property:
                            for cp in claim_property:
                                cp_id = cp['mainsnak'].get('datavalue', {}).get('value', {}).get('id')
                                cp_rank = cp['rank']
                                if cp_rank != "deprecated" and cp_id in value_set:
                                    keep = True

                    if keep:
                        unique_id = obj["id"]

                        if to_print:
                            print("ID:", unique_id)
                            print("type:", entry_type)

                        # parsing all properties that refer to other entities
                        if parse_properties:
                            for prop, claim_property in claims.items():
                                cp_dicts = [cp['mainsnak']['datavalue'].get('value') for cp in claim_property if cp['mainsnak'].get('datavalue')]
                                cp_values = [cp_dict.get('id') for cp_dict in cp_dicts if isinstance(cp_dict, dict) if cp_dict.get('id') is not None]
                                if cp_values:
                                    if to_print:
                                        print("prop:", prop, cp_values)

                        if parse_sitelinks:
                            site_value = obj["sitelinks"].get(site_filter, None)
                            if site_value:
                                site = site_value['title']
                                if to_print:
                                    print(site_filter, ":", site)
                                title_to_id[site] = unique_id
                                # print(site, "for", unique_id)

                        if parse_labels:
                            labels = obj["labels"]
                            if labels:
                                for lang in languages:
                                    lang_label = labels.get(lang, None)
                                    if lang_label:
                                        if to_print:
                                            print("label (" + lang + "):", lang_label["value"])

                        if parse_descriptions:
                            descriptions = obj["descriptions"]
                            if descriptions:
                                for lang in languages:
                                    lang_descr = descriptions.get(lang, None)
                                    if lang_descr:
                                        if to_print:
                                            print("description (" + lang + "):", lang_descr["value"])

                        if parse_aliases:
                            aliases = obj["aliases"]
                            if aliases:
                                for lang in languages:
                                    lang_aliases = aliases.get(lang, None)
                                    if lang_aliases:
                                        for item in lang_aliases:
                                            if to_print:
                                                print("alias (" + lang + "):", item["value"])

                        if to_print:
                            print()
            line = file.readline()
            cnt += 1

    return title_to_id


def _read_wikidata_entities_regex_depr(limit=None, to_print=False):
    """ Read the JSON wiki data and parse out the entities with regular expressions. Takes XXX to parse 55M lines. """

    regex_p31 = re.compile(r'mainsnak[^}]*\"P31\"[^}]*}', re.UNICODE)
    regex_id = re.compile(r'\"id\":"Q[0-9]*"', re.UNICODE)
    regex_enwiki = re.compile(r'\"enwiki\":[^}]*}', re.UNICODE)
    regex_title = re.compile(r'\"title\":"[^"]*"', re.UNICODE)

    title_to_id = dict()

    with bz2.open(WIKIDATA_JSON, mode='rb') as file:
        line = file.readline()
        cnt = 0
        while line and (not limit or cnt < limit):
            if cnt % 100000 == 0:
                print(datetime.datetime.now(), "processed", cnt, "lines of WikiData dump")
            clean_line = line.strip()
            if clean_line.endswith(b","):
                clean_line = clean_line[:-1]
            if len(clean_line) > 1:
                clean_line = line.strip().decode("utf-8")
                keep = False

                p31_matches = regex_p31.findall(clean_line)
                if p31_matches:
                    for p31_match in p31_matches:
                        id_matches = regex_id.findall(p31_match)
                        for id_match in id_matches:
                            id_match = id_match[6:][:-1]
                            if id_match == "Q5" or id_match == "Q15632617":
                                keep = True

                if keep:
                    id_match = regex_id.search(clean_line).group(0)
                    id_match = id_match[6:][:-1]

                    enwiki_matches = regex_enwiki.findall(clean_line)
                    if enwiki_matches:
                        for enwiki_match in enwiki_matches:
                            title_match = regex_title.search(enwiki_match).group(0)
                            title = title_match[9:][:-1]
                            title_to_id[title] = id_match
                            # print(title, "for", id_match)

            line = file.readline()
            cnt += 1

    return title_to_id


def _read_wikipedia_prior_probs():
    """ Read the XML wikipedia data and parse out intra-wiki links to estimate prior probabilities
    The full file takes about 2h to parse 1100M lines (update printed every 5M lines)
     """

    # find the links
    link_regex = re.compile(r'\[\[[^\[\]]*\]\]')

    # match on interwiki links, e.g. `en:` or `:fr:`
    ns_regex = r":?" + "[a-z][a-z]" + ":"

    # match on Namespace: optionally preceded by a :
    for ns in wiki_namespaces:
        ns_regex += "|" + ":?" + ns + ":"

    ns_regex = re.compile(ns_regex, re.IGNORECASE)

    with bz2.open(ENWIKI_DUMP, mode='rb') as file:
        line = file.readline()
        cnt = 0
        while line:
            if cnt % 5000000 == 0:
                print(datetime.datetime.now(), "processed", cnt, "lines of Wikipedia dump")
            clean_line = line.strip().decode("utf-8")

            matches = link_regex.findall(clean_line)
            for match in matches:
                match = match[2:][:-2].replace("_", " ").strip()

                if ns_regex.match(match):
                    pass  # ignore namespaces at the beginning of the string

                # this is a simple link, with the alias the same as the mention
                elif "|" not in match:
                    _store_alias(match, match, normalize_alias=True, normalize_entity=True)

                # in wiki format, the link is written as [[entity|alias]]
                else:
                    splits = match.split("|")
                    entity = splits[0].strip()
                    alias = splits[1].strip()
                    # specific wiki format  [[alias (specification)|]]
                    if len(alias) == 0 and "(" in entity:
                        alias = entity.split("(")[0]
                        _store_alias(alias, entity, normalize_alias=False, normalize_entity=True)
                    else:
                        _store_alias(alias, entity, normalize_alias=False, normalize_entity=True)

            line = file.readline()
            cnt += 1

    # write all aliases and their entities and occurrences to file
    with open(PRIOR_PROB, mode='w', encoding='utf8') as outputfile:
        outputfile.write("alias" + "|" + "count" + "|" + "entity" + "\n")
        for alias, alias_dict in sorted(map_alias_to_link.items(), key=lambda x: x[0]):
            for entity, count in sorted(alias_dict.items(), key=lambda x: x[1], reverse=True):
                outputfile.write(alias + "|" + str(count) + "|" + entity + "\n")


def _store_alias(alias, entity, normalize_alias=False, normalize_entity=True):
    alias = alias.strip()
    entity = entity.strip()

    # remove everything after # as this is not part of the title but refers to a specific paragraph
    if normalize_entity:
        # wikipedia titles are always capitalized
        entity = capitalize_first(entity.split("#")[0])
    if normalize_alias:
        alias = alias.split("#")[0]

    if alias and entity:
        alias_dict = map_alias_to_link.get(alias, dict())
        entity_count = alias_dict.get(entity, 0)
        alias_dict[entity] = entity_count + 1
        map_alias_to_link[alias] = alias_dict


def _read_wikipedia():
    """ Read the XML wikipedia data """

    with bz2.open(ENWIKI_DUMP, mode='rb') as file:
        line = file.readline()
        cnt = 1
        article_text = ""
        article_title = None
        article_id = None
        reading_text = False
        while line and cnt < 1000000:
            clean_line = line.strip().decode("utf-8")

            # Start reading new page
            if clean_line == "<page>":
                article_text = ""
                article_title = None
                article_id = 342

            # finished reading this page
            elif clean_line == "</page>":
                if article_id:
                    _store_wp_article(article_id, article_title, article_text.strip())

            # start reading text within a page
            if "<text" in clean_line:
                reading_text = True

            if reading_text:
                article_text += " " + clean_line

            # stop reading text within a page
            if "</text" in clean_line:
                reading_text = False

            # read the ID of this article
            ids = re.findall(r"(?<=<id>)\d*(?=</id>)", clean_line)
            if ids:
                article_id = ids[0]

            # read the title of this article
            titles = re.findall(r"(?<=<title>).*(?=</title>)", clean_line)
            if titles:
                article_title = titles[0].strip()

            line = file.readline()
            cnt += 1


def _store_wp_article(article_id, article_title, article_text):
    pass
    print("WP article", article_id, ":", article_title)
    print(article_text)
    print(_get_clean_wp_text(article_text))
    print()


def _get_clean_wp_text(article_text):
    # TODO: compile the regular expressions

    # remove Category and File statements
    clean_text = re.sub(r'\[\[Category:[^\[]*]]', '', article_text)
    print("1", clean_text)
    clean_text = re.sub(r'\[\[File:[^\[]*]]', '', clean_text)       # TODO: this doesn't work yet
    print("2", clean_text)

    # remove bolding markup
    clean_text = re.sub('\'\'\'', '', clean_text)
    clean_text = re.sub('\'\'', '', clean_text)

    # remove nested {{info}} statements by removing the inner/smallest ones first and iterating
    try_again = True
    previous_length = len(clean_text)
    while try_again:
        clean_text = re.sub('{[^{]*?}', '', clean_text)  # non-greedy match excluding a nested {
        if len(clean_text) < previous_length:
            try_again = True
        else:
            try_again = False
        previous_length = len(clean_text)

    # remove multiple spaces
    while '  ' in clean_text:
        clean_text = re.sub('  ', ' ', clean_text)

    # remove simple interwiki links (no alternative name)
    clean_text = re.sub('\[\[([^|]*?)]]', r'\1', clean_text)

    # remove simple interwiki links by picking the alternative name
    clean_text = re.sub(r'\[\[[^|]*?\|([^|]*?)]]', r'\1', clean_text)

    # remove HTML comments
    clean_text = re.sub('&lt;!--[^!]*--&gt;', '', clean_text)

    return clean_text


def add_el(kb, nlp):
    el_pipe = nlp.create_pipe(name='entity_linker', config={"kb": kb})
    nlp.add_pipe(el_pipe, last=True)

    text = "In The Hitchhiker's Guide to the Galaxy, written by Douglas Adams, " \
           "Douglas reminds us to always bring our towel. " \
           "The main character in Doug's novel is the man Arthur Dent, " \
           "but Douglas doesn't write about George Washington or Homer Simpson."
    doc = nlp(text)

    print()
    for token in doc:
        print("token", token.text, token.ent_type_, token.ent_kb_id_)

    print()
    for ent in doc.ents:
        print("ent", ent.text, ent.label_, ent.kb_id_)


def capitalize_first(text):
    if not text:
        return None
    result = text[0].capitalize()
    if len(result) > 0:
        result += text[1:]
    return result


if __name__ == "__main__":
    print("START", datetime.datetime.now())

    to_create_prior_probs = False
    to_create_entity_counts = False
    to_create_kb = True
    to_read_kb = True

    # STEP 1 : create prior probabilities from WP
    # run only once !
    if to_create_prior_probs:
        print("STEP 1: to_create_prior_probs", datetime.datetime.now())
        _read_wikipedia_prior_probs()
        print()

    # STEP 2 : deduce entity frequencies from WP
    # run only once !
    if to_create_entity_counts:
        print("STEP 2: to_create_entity_counts", datetime.datetime.now())
        _write_entity_counts()
        print()

    if to_create_kb:
        # STEP 3 : create KB
        print("STEP 3: to_create_kb", datetime.datetime.now())
        my_nlp = spacy.load('en_core_web_sm')
        my_vocab = my_nlp.vocab
        my_kb = create_kb(my_vocab, max_entities_per_alias=10, min_occ=5, to_print=False)
        print("kb entities:", my_kb.get_size_entities())
        print("kb aliases:", my_kb.get_size_aliases())
        print()

        # STEP 4 : write KB to file
        print("STEP 4: write KB", datetime.datetime.now())
        my_kb.dump(KB_FILE)
        my_vocab.to_disk(VOCAB_DIR)
        print()

    if to_read_kb:
        # STEP 5 : read KB back in from file
        print("STEP 5: to_read_kb", datetime.datetime.now())
        my_vocab = Vocab()
        my_vocab.from_disk(VOCAB_DIR)
        my_kb = KnowledgeBase(vocab=my_vocab)
        my_kb.load_bulk(KB_FILE)
        print("kb entities:", my_kb.get_size_entities())
        print("kb aliases:", my_kb.get_size_aliases())
        print()

        # test KB
        candidates = my_kb.get_candidates("Bush")
        for c in candidates:
            print("entity:", c.entity_)
            print("entity freq:", c.entity_freq)
            print("alias:", c.alias_)
            print("prior prob:", c.prior_prob)
            print()

    # STEP 6: add KB to NLP pipeline
    # print("STEP 6: use KB", datetime.datetime.now())
    # add_el(my_kb, nlp)

    print("STOP", datetime.datetime.now())
