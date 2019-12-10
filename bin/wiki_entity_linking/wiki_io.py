# coding: utf-8
from __future__ import unicode_literals

import sys
import csv

# min() needed to prevent error on windows, cf https://stackoverflow.com/questions/52404416/
csv.field_size_limit(min(sys.maxsize, 2147483646))

""" This class provides reading/writing methods for temp files """


# Entity definition: WP title -> WD ID #
def write_title_to_id(entity_def_output, title_to_id):
    with entity_def_output.open("w", encoding="utf8") as id_file:
        id_file.write("WP_title" + "|" + "WD_id" + "\n")
        for title, qid in title_to_id.items():
            id_file.write(title + "|" + str(qid) + "\n")


def read_title_to_id(entity_def_output):
    title_to_id = dict()
    with entity_def_output.open("r", encoding="utf8") as id_file:
        csvreader = csv.reader(id_file, delimiter="|")
        # skip header
        next(csvreader)
        for row in csvreader:
            title_to_id[row[0]] = row[1]
    return title_to_id


# Entity aliases from WD: WD ID -> WD alias #
def write_id_to_alias(entity_alias_path, id_to_alias):
    with entity_alias_path.open("w", encoding="utf8") as alias_file:
        alias_file.write("WD_id" + "|" + "alias" + "\n")
        for qid, alias_list in id_to_alias.items():
            for alias in alias_list:
                alias_file.write(str(qid) + "|" + alias + "\n")


def read_id_to_alias(entity_alias_path):
    id_to_alias = dict()
    with entity_alias_path.open("r", encoding="utf8") as alias_file:
        csvreader = csv.reader(alias_file, delimiter="|")
        # skip header
        next(csvreader)
        for row in csvreader:
            qid = row[0]
            alias = row[1]
            alias_list = id_to_alias.get(qid, [])
            alias_list.append(alias)
            id_to_alias[qid] = alias_list
    return id_to_alias


def read_alias_to_id_generator(entity_alias_path):
    """ Read (aliases, qid) tuples """

    with entity_alias_path.open("r", encoding="utf8") as alias_file:
        csvreader = csv.reader(alias_file, delimiter="|")
        # skip header
        next(csvreader)
        for row in csvreader:
            qid = row[0]
            alias = row[1]
            yield alias, qid


# Entity descriptions from WD: WD ID -> WD alias #
def write_id_to_descr(entity_descr_output, id_to_descr):
    with entity_descr_output.open("w", encoding="utf8") as descr_file:
        descr_file.write("WD_id" + "|" + "description" + "\n")
        for qid, descr in id_to_descr.items():
            descr_file.write(str(qid) + "|" + descr + "\n")


def read_id_to_descr(entity_desc_path):
    id_to_desc = dict()
    with entity_desc_path.open("r", encoding="utf8") as descr_file:
        csvreader = csv.reader(descr_file, delimiter="|")
        # skip header
        next(csvreader)
        for row in csvreader:
            id_to_desc[row[0]] = row[1]
    return id_to_desc


# Entity counts from WP: WP title -> count #
def write_entity_to_count(prior_prob_input, count_output):
    # Write entity counts for quick access later
    entity_to_count = dict()
    total_count = 0

    with prior_prob_input.open("r", encoding="utf8") as prior_file:
        # skip header
        prior_file.readline()
        line = prior_file.readline()

        while line:
            splits = line.replace("\n", "").split(sep="|")
            # alias = splits[0]
            count = int(splits[1])
            entity = splits[2]

            current_count = entity_to_count.get(entity, 0)
            entity_to_count[entity] = current_count + count

            total_count += count

            line = prior_file.readline()

    with count_output.open("w", encoding="utf8") as entity_file:
        entity_file.write("entity" + "|" + "count" + "\n")
        for entity, count in entity_to_count.items():
            entity_file.write(entity + "|" + str(count) + "\n")


def read_entity_to_count(count_input):
    entity_to_count = dict()
    with count_input.open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter="|")
        # skip header
        next(csvreader)
        for row in csvreader:
            entity_to_count[row[0]] = int(row[1])

    return entity_to_count
