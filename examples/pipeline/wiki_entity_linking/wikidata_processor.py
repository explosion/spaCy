# coding: utf-8
from __future__ import unicode_literals

import re
import bz2
import json
import datetime

# TODO: remove hardcoded paths
WIKIDATA_JSON = 'C:/Users/Sofie/Documents/data/wikidata/wikidata-20190304-all.json.bz2'


def read_wikidata_entities_json(limit=None, to_print=False):
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
            if cnt % 500000 == 0:
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


def _read_wikidata_entities_regex_depr(limit=None):
    """
    Read the JSON wiki data and parse out the entities with regular expressions. Takes XXX to parse 55M lines.
    TODO: doesn't work yet. may be deleted ?
    """

    regex_p31 = re.compile(r'mainsnak[^}]*\"P31\"[^}]*}', re.UNICODE)
    regex_id = re.compile(r'\"id\":"Q[0-9]*"', re.UNICODE)
    regex_enwiki = re.compile(r'\"enwiki\":[^}]*}', re.UNICODE)
    regex_title = re.compile(r'\"title\":"[^"]*"', re.UNICODE)

    title_to_id = dict()

    with bz2.open(WIKIDATA_JSON, mode='rb') as file:
        line = file.readline()
        cnt = 0
        while line and (not limit or cnt < limit):
            if cnt % 500000 == 0:
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

            line = file.readline()
            cnt += 1

    return title_to_id
