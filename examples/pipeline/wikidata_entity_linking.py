# coding: utf-8
from __future__ import unicode_literals

"""Demonstrate how to build a knowledge base from WikiData and run an Entity Linking algorithm.
"""
import re
import json
import spacy
import datetime
import bz2
from spacy.kb import KnowledgeBase

# TODO: remove hardcoded paths
WIKIDATA_JSON = 'C:/Users/Sofie/Documents/data/wikidata/wikidata-20190304-all.json.bz2'
ENWIKI_DUMP = 'C:/Users/Sofie/Documents/data/wikipedia/enwiki-20190320-pages-articles-multistream.xml.bz2'
ENWIKI_INDEX = 'C:/Users/Sofie/Documents/data/wikipedia/enwiki-20190320-pages-articles-multistream-index.txt.bz2'
PRIOR_PROB = 'C:/Users/Sofie/Documents/data/wikipedia/prior_prob.csv'


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


def create_kb(vocab, max_entities_per_alias, min_occ):
    kb = KnowledgeBase(vocab=vocab)

    _add_entities(kb)
    _add_aliases(kb, max_entities_per_alias, min_occ)

    # _read_wikidata()
    # _read_wikipedia()

    print()
    print("kb size:", len(kb), kb.get_size_entities(), kb.get_size_aliases())

    return kb


def _add_entities(kb):

    kb.add_entity(entity="Earthquake", prob=0.342)
    kb.add_entity(entity="2010 haiti earthquake", prob=0.1)
    kb.add_entity(entity="1906 san francisco earthquake", prob=0.1)
    kb.add_entity(entity="2011 christchurch earthquak", prob=0.1)

    kb.add_entity(entity="Soft drink", prob=0.342)

    print("added", kb.get_size_entities(), "entities:", kb.get_entity_strings())


def _add_aliases(kb, max_entities_per_alias, min_occ):
    all_entities = kb.get_entity_strings()
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
                        if ent_string in all_entities:
                            p_entity_givenalias = ent_count / total_count
                            selected_entities.append(ent_string)
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

    print()
    print("added", kb.get_size_aliases(), "aliases:", kb.get_alias_strings())


def _read_wikidata():
    """ Read the JSON wiki data """
    # TODO remove hardcoded path

    languages = {'en', 'de'}
    properties = {'P31'}
    sites = {'enwiki'}

    with bz2.open(WIKIDATA_JSON, mode='rb') as file:
        line = file.readline()
        cnt = 1
        while line and cnt < 100000:
            clean_line = line.strip()
            if clean_line.endswith(b","):
                clean_line = clean_line[:-1]
            if len(clean_line) > 1:
                obj = json.loads(clean_line)

                unique_id = obj["id"]
                print("ID:", unique_id)

                entry_type = obj["type"]
                print("type:", entry_type)

                # TODO: filter on rank:  preferred, normal or deprecated
                claims = obj["claims"]
                for prop in properties:
                    claim_property = claims.get(prop, None)
                    if claim_property:
                        for cp in claim_property:
                            print(prop, cp['mainsnak']['datavalue']['value']['id'])

                entry_sites = obj["sitelinks"]
                for site in sites:
                    site_value = entry_sites.get(site, None)
                    print(site, ":", site_value['title'])

                labels = obj["labels"]
                if labels:
                    for lang in languages:
                        lang_label = labels.get(lang, None)
                        if lang_label:
                            print("label (" + lang + "):", lang_label["value"])

                descriptions = obj["descriptions"]
                if descriptions:
                    for lang in languages:
                        lang_descr = descriptions.get(lang, None)
                        if lang_descr:
                            print("description (" + lang + "):", lang_descr["value"])

                aliases = obj["aliases"]
                if aliases:
                    for lang in languages:
                        lang_aliases = aliases.get(lang, None)
                        if lang_aliases:
                            for item in lang_aliases:
                                print("alias (" + lang + "):", item["value"])

                print()
            line = file.readline()
            cnt += 1


def _read_wikipedia_prior_probs():
    """ Read the XML wikipedia data and parse out intra-wiki links to estimate prior probabilities """

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
                print(datetime.datetime.now(), "processed", cnt, "lines")
            clean_line = line.strip().decode("utf-8")

            matches = link_regex.findall(clean_line)
            for match in matches:
                match = match[2:][:-2].replace("_", " ").strip()

                if ns_regex.match(match):
                    pass  # ignore namespaces at the beginning of the string

                # this is a simple link, with the alias the same as the mention
                elif "|" not in match:
                    _store_alias(match, match)

                # in wiki format, the link is written as [[entity|alias]]
                else:
                    splits = match.split("|")
                    entity = splits[0].strip()
                    alias = splits[1].strip()
                    # specific wiki format  [[alias (specification)|]]
                    if len(alias) == 0 and "(" in entity:
                        alias = entity.split("(")[0]
                        _store_alias(alias, entity)
                    else:
                        _store_alias(alias, entity)

            line = file.readline()
            cnt += 1

    # write all aliases and their entities and occurrences to file
    with open(PRIOR_PROB, mode='w', encoding='utf8') as outputfile:
        outputfile.write("alias" + "|" + "count" + "|" + "entity" + "\n")
        for alias, alias_dict in sorted(map_alias_to_link.items(), key=lambda x: x[0]):
            for entity, count in sorted(alias_dict.items(), key=lambda x: x[1], reverse=True):
                outputfile.write(alias + "|" + str(count) + "|" + entity + "\n")


def _store_alias(alias, entity):
    alias = alias.strip()
    entity = entity.strip()

    # remove everything after # as this is not part of the title but refers to a specific paragraph
    clean_entity = entity.split("#")[0].capitalize()

    if len(alias) > 0 and len(clean_entity) > 0:
        alias_dict = map_alias_to_link.get(alias, dict())
        entity_count = alias_dict.get(clean_entity, 0)
        alias_dict[clean_entity] = entity_count + 1
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
           "The main character in Doug's novel is called Arthur Dent."
    doc = nlp(text)

    print()
    for token in doc:
        print("token", token.text, token.ent_type_, token.ent_kb_id_)

    print()
    for ent in doc.ents:
        print("ent", ent.text, ent.label_, ent.kb_id_)


if __name__ == "__main__":
    # STEP 1 : create prior probabilities from WP
    # run only once !
    # _read_wikipedia_prior_probs()

    # STEP 2 : create KB
    nlp = spacy.load('en_core_web_sm')
    my_kb = create_kb(nlp.vocab, max_entities_per_alias=10, min_occ=5)
    # add_el(my_kb, nlp)

    # clean_text = "[[File:smomething]] jhk"
    # clean_text = re.sub(r'\[\[Category:[^\[]*]]', '', clean_text)
    # clean_text = re.sub(r'\[\[File:[^\[]*]]', '', clean_text)
    # print(clean_text)
