# coding: utf-8
from __future__ import unicode_literals

import bz2
import json
import datetime


def read_wikidata_entities_json(wikidata_file, limit=None, to_print=False):
    # Read the JSON wiki data and parse out the entities. Takes about 7u30 to parse 55M lines.
    # get latest-all.json.bz2 from https://dumps.wikimedia.org/wikidatawiki/entities/

    lang = 'en'
    site_filter = 'enwiki'

    # properties filter (currently disabled to get ALL data)
    prop_filter = dict()
    # prop_filter = {'P31': {'Q5', 'Q15632617'}}     # currently defined as OR: one property suffices to be selected

    title_to_id = dict()
    id_to_descr = dict()

    # parse appropriate fields - depending on what we need in the KB
    parse_properties = False
    parse_sitelinks = True
    parse_labels = False
    parse_descriptions = True
    parse_aliases = False
    parse_claims = False

    with bz2.open(wikidata_file, mode='rb') as file:
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
                    # filtering records on their properties (currently disabled to get ALL data)
                    # keep = False
                    keep = True

                    claims = obj["claims"]
                    if parse_claims:
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
                                cp_dicts = [cp['mainsnak']['datavalue'].get('value') for cp in claim_property
                                            if cp['mainsnak'].get('datavalue')]
                                cp_values = [cp_dict.get('id') for cp_dict in cp_dicts if isinstance(cp_dict, dict)
                                             if cp_dict.get('id') is not None]
                                if cp_values:
                                    if to_print:
                                        print("prop:", prop, cp_values)

                        found_link = False
                        if parse_sitelinks:
                            site_value = obj["sitelinks"].get(site_filter, None)
                            if site_value:
                                site = site_value['title']
                                if to_print:
                                    print(site_filter, ":", site)
                                title_to_id[site] = unique_id
                                found_link = True

                        if parse_labels:
                            labels = obj["labels"]
                            if labels:
                                lang_label = labels.get(lang, None)
                                if lang_label:
                                    if to_print:
                                        print("label (" + lang + "):", lang_label["value"])

                        if found_link and parse_descriptions:
                            descriptions = obj["descriptions"]
                            if descriptions:
                                lang_descr = descriptions.get(lang, None)
                                if lang_descr:
                                    if to_print:
                                        print("description (" + lang + "):", lang_descr["value"])
                                    id_to_descr[unique_id] = lang_descr["value"]

                        if parse_aliases:
                            aliases = obj["aliases"]
                            if aliases:
                                lang_aliases = aliases.get(lang, None)
                                if lang_aliases:
                                    for item in lang_aliases:
                                        if to_print:
                                            print("alias (" + lang + "):", item["value"])

                        if to_print:
                            print()
            line = file.readline()
            cnt += 1

    return title_to_id, id_to_descr
