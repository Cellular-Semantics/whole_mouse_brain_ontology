"""
nomenclature_table_CS202211210.csv is manually annotated by Shawn Tan. Then a new version of the nomenclature
(nomenclature_table_CS202212150.csv) is released. This script migrates annotations from old nomenclature to the new one.
"""
import os
import re

import networkx as nx
import pandas as pd

from difflib import SequenceMatcher
from Levenshtein import ratio
from template_generation_utils import read_csv_to_dict, generate_dendrogram_tree
from nomenclature_tools import nomenclature_2_nodes_n_edges


NEW_LEAF_NAME_PATTERN = re.compile("^\\d\\d\\d\\d .+$")
OLD_LEAF_NAME_PATTERN = re.compile("^\\d+ .+$")

FORWARD_SEARCH_DISTANCE = 30

DENDROGRAM_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms")
OLD_NOMENCLATURE = "nomenclature_table_CS202211210.csv"
NEW_NOMENCLATURE = "nomenclature_table_CS202212150.csv"
NEW_NOMENCLATURE_ANNOTATED = "nomenclature_table_CS202212150_annotated.csv"


def align_nomenclatures(old_nomenclature, new_nomenclature):
    old_headers, old_data = read_csv_to_dict(os.path.join(DENDROGRAM_FOLDER, old_nomenclature))
    new_headers, new_data = read_csv_to_dict(os.path.join(DENDROGRAM_FOLDER, new_nomenclature))

    old_data_scan_index = -1
    all_data = []
    counterparts = list()
    for accession_id in new_data:
        row_data = {}
        label = new_data[accession_id]["cell_set_preferred_alias"]
        old_data_record, old_data_scan_index = find_old_data_counterpart(label, old_data, old_data_scan_index)
        for header in new_headers:
            if header:
                row_data[header] = new_data[accession_id][header]
        annotation_added = False
        if old_data_record:
            # migrate old annotations
            if "MBA" in old_data_record and old_data_record["MBA"]:
                row_data["MBA"] = old_data_record["MBA"]
                annotation_added = True
            if "NT" in old_data_record and old_data_record["NT"]:
                row_data["NT"] = old_data_record["NT"]
                annotation_added = True
            if "CL" in old_data_record and old_data_record["CL"]:
                row_data["CL"] = old_data_record["CL"]
                annotation_added = True
            if "layer" in old_data_record and old_data_record["layer"]:
                row_data["layer"] = old_data_record["layer"]
                annotation_added = True
            if "projection" in old_data_record and old_data_record["projection"]:
                row_data["projection"] = old_data_record["projection"]
                annotation_added = True
            if annotation_added:
                counterparts.append(old_data_record["cell_set_accession"])
        else:
            row_data["MBA"] = ""
            row_data["NT"] = ""
            row_data["CL"] = ""
            row_data["layer"] = ""
            row_data["projection"] = ""

        all_data.append(row_data)

    class_robot_template = pd.DataFrame.from_records(all_data)
    class_robot_template.to_csv(os.path.join(DENDROGRAM_FOLDER, NEW_NOMENCLATURE_ANNOTATED), sep=",", index=False)

    print("Not migrated annotations: ")
    not_migrated = list()
    for accession_id in old_data:
        if (old_data[accession_id]["MBA"] or
            old_data[accession_id]["NT"] or
            old_data[accession_id]["CL"] or
            old_data[accession_id]["layer"] or
            old_data[accession_id]["projection"]) \
                and accession_id not in counterparts:
            print(accession_id)
            not_migrated.append(accession_id)

    print(str(len(counterparts)) + " records migrated from old to new nomenclature")
    print(str(len(not_migrated)) + " records NOT migrated from old to new nomenclature")



def find_old_data_counterpart(new_label, old_data, old_data_scan_index):
    # 2873 PAG-MRN Pou3f1 Glut_1 -> PAG-MRN Pou3f1 Glut
    new_label_base = new_label
    if NEW_LEAF_NAME_PATTERN.match(new_label_base):
        new_label_base = new_label_base[new_label_base.find(" "):].strip()
    if '_' in new_label_base:
        new_label_base = new_label_base[0:new_label_base.rindex('_')]
    # print(new_label)
    # print(new_label_base)

    index = 0
    for accession_id in old_data:
        if old_data_scan_index < index < old_data_scan_index + FORWARD_SEARCH_DISTANCE:
            old_label = old_data[accession_id]["cell_set_preferred_alias"]
            old_label_base = old_label
            if OLD_LEAF_NAME_PATTERN.match(old_label_base):
                old_label_base = old_label_base[old_label_base.find(" "):].strip()
            # if SequenceMatcher(None, new_label_base, old_label_base).ratio() >= 0.8:
            if index <= 5104 and ratio(new_label_base.lower(), old_label_base.lower()) >= 0.7:
                # apply similarity to leafs
                # print("match: " + new_label + "  ||||  " + old_label)
                return old_data[accession_id], index
            elif index > 5104 and new_label_base.lower() == old_label_base.lower():
                # print("match: " + new_label + "  ||||  " + old_label)
                return old_data[accession_id], index
            elif ' '.join(new_label_base.split(" ")[-2:]).lower() == ' '.join(old_label_base.split(" ")[-2:]).lower():
                # 3463 RPO-CS-NI Meis2 Gaba_1 vs 3464 PCG-LDT-DTN-RPO-CS Meis2 Gaba
                # print("match: " + new_label + "  ||||  " + old_label)
                return old_data[accession_id], index
        index += 1

    # print("no match: " + new_label + "  (" + str(old_data_scan_index) + ")")
    return None, old_data_scan_index


align_nomenclatures(OLD_NOMENCLATURE, NEW_NOMENCLATURE)
