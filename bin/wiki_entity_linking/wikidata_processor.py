# coding: utf-8
from __future__ import unicode_literals

import bz2
import json
import logging

from bin.wiki_entity_linking.wiki_namespaces import WD_META_ITEMS

logger = logging.getLogger(__name__)


def read_wikidata_entities_json(wikidata_file, limit=None, to_print=False, lang="en", parse_descr=True):
    # Read the JSON wiki data and parse out the entities. Takes about 7-10h to parse 55M lines.
    # get latest-all.json.bz2 from https://dumps.wikimedia.org/wikidatawiki/entities/

    site_filter = '{}wiki'.format(lang)

    # filter: currently defined as OR: one hit suffices to be removed from further processing
    exclude_list = WD_META_ITEMS

    # punctuation
    exclude_list.extend(["Q1383557", "Q10617810"])

    # letters etc
    exclude_list.extend(["Q188725", "Q19776628", "Q3841820", "Q17907810", "Q9788", "Q9398093"])

    neg_prop_filter = {
        'P31': exclude_list,    # instance of
        'P279': exclude_list    # subclass
    }

    title_to_id = dict()
    id_to_descr = dict()
    id_to_alias = dict()

    # parse appropriate fields - depending on what we need in the KB
    parse_properties = False
    parse_sitelinks = True
    parse_labels = False
    parse_aliases = True
    parse_claims = True

    with bz2.open(wikidata_file, mode='rb') as file:
        for cnt, line in enumerate(file):
            if limit and cnt >= limit:
                break
            if cnt % 500000 == 0 and cnt > 0:
                logger.info("processed {} lines of WikiData JSON dump".format(cnt))
            clean_line = line.strip()
            if clean_line.endswith(b","):
                clean_line = clean_line[:-1]
            if len(clean_line) > 1:
                obj = json.loads(clean_line)
                entry_type = obj["type"]

                if entry_type == "item":
                    keep = True

                    claims = obj["claims"]
                    if parse_claims:
                        for prop, value_set in neg_prop_filter.items():
                            claim_property = claims.get(prop, None)
                            if claim_property:
                                for cp in claim_property:
                                    cp_id = (
                                        cp["mainsnak"]
                                        .get("datavalue", {})
                                        .get("value", {})
                                        .get("id")
                                    )
                                    cp_rank = cp["rank"]
                                    if cp_rank != "deprecated" and cp_id in value_set:
                                        keep = False

                    if keep:
                        unique_id = obj["id"]

                        if to_print:
                            print("ID:", unique_id)
                            print("type:", entry_type)

                        # parsing all properties that refer to other entities
                        if parse_properties:
                            for prop, claim_property in claims.items():
                                cp_dicts = [
                                    cp["mainsnak"]["datavalue"].get("value")
                                    for cp in claim_property
                                    if cp["mainsnak"].get("datavalue")
                                ]
                                cp_values = [
                                    cp_dict.get("id")
                                    for cp_dict in cp_dicts
                                    if isinstance(cp_dict, dict)
                                    if cp_dict.get("id") is not None
                                ]
                                if cp_values:
                                    if to_print:
                                        print("prop:", prop, cp_values)

                        found_link = False
                        if parse_sitelinks:
                            site_value = obj["sitelinks"].get(site_filter, None)
                            if site_value:
                                site = site_value["title"]
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
                                        print(
                                            "label (" + lang + "):", lang_label["value"]
                                        )

                        if found_link and parse_descr:
                            descriptions = obj["descriptions"]
                            if descriptions:
                                lang_descr = descriptions.get(lang, None)
                                if lang_descr:
                                    if to_print:
                                        print(
                                            "description (" + lang + "):",
                                            lang_descr["value"],
                                        )
                                    id_to_descr[unique_id] = lang_descr["value"]

                        if parse_aliases:
                            aliases = obj["aliases"]
                            if aliases:
                                lang_aliases = aliases.get(lang, None)
                                if lang_aliases:
                                    for item in lang_aliases:
                                        if to_print:
                                            print(
                                                "alias (" + lang + "):", item["value"]
                                            )
                                        alias_list = id_to_alias.get(unique_id, [])
                                        alias_list.append(item["value"])
                                        id_to_alias[unique_id] = alias_list

                        if to_print:
                            print()

    # log final number of lines processed
    logger.info("Finished. Processed {} lines of WikiData JSON dump".format(cnt))
    return title_to_id, id_to_descr, id_to_alias


