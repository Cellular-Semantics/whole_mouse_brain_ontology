import os
import csv
import re
from template_generation_utils import read_csv, read_csv_to_dict

CLUSTER_ANNOTATION_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/cluster_annotation_CS202212150.tsv")
SUBCLASS_ANNOTATION_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/subclass_annotation_CS202212150.tsv")
SUPERTYPE_ANNOTATION_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/supertype_annotation_CS202212150.tsv")
MBA_ABBREVIATIONS = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/mba_regions.tsv")
NT_SYMBOL_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/Neurotransmitter_symbols_mapping.tsv")
BRAIN_REGION_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/Brain_region_mapping.tsv")


def get_unique_nts(raw_file_path):
    unique_nts = set()
    headers, records = read_csv_to_dict(raw_file_path, delimiter="\t")

    for record in records:
        neurotransmitters = records[record]["Neurotransmitter auto-annotation"].strip()
        if neurotransmitters:
            unique_nts.update(neurotransmitters.split(" "))

    with open(NT_SYMBOL_MAPPING, mode='w') as out:
        writer = csv.writer(out, delimiter="\t", quotechar='"')
        writer.writerow(["SYMBOL", "CELL TYPE LABEL", "CELL TYPE NEUROTRANSMISSION ID", "GENES", "COMMENTS"])

        for unique_nt in unique_nts:
            writer.writerow([unique_nt, "", "", "", ""])


def get_brain_regions(raw_file_path):
    regions_map = dict()

    mba_abbreviations = read_csv_to_dict(MBA_ABBREVIATIONS, delimiter="\t", id_column_name="abbreviation", id_to_lower=True)[1]
    headers, records = read_csv_to_dict(raw_file_path, delimiter="\t")

    delimiters = " ", ",", "-", "/"
    regex_pattern = '|'.join(map(re.escape, delimiters))

    unmatched = set()
    for cluster_id in records:
        brain_regions = records[cluster_id]["tentative_anatomical_annotation"].strip().replace("?", "").replace("(", "").replace(")", "").lower()
        if brain_regions and brain_regions != "NA":
            parts = re.split(regex_pattern, brain_regions)
            regions = list()
            for part in parts:
                if part in mba_abbreviations:
                    regions.append("http://purl.obolibrary.org/obo/MBA_" + mba_abbreviations[part]["structure ID"])
                else:
                    unmatched.add(part)
            regions_map["CS202212150_" + cluster_id] = "|".join(regions)

    with open(BRAIN_REGION_MAPPING, mode='w') as out:
        writer = csv.writer(out, delimiter="\t", quotechar='"')
        writer.writerow(["Accession_ID", "Label", "MBA_ID"])

        for region in regions_map:
            writer.writerow([region, records[region.replace("CS202212150_", "")]["cluster_label"], regions_map[region]])

    print("Couldn't find the following abbreviations (" + str(len(unmatched)) + "):")
    for unmatch in unmatched:
        print(unmatch)


# get_unique_nts(CLUSTER_ANNOTATION_PATH)
get_brain_regions(CLUSTER_ANNOTATION_PATH)
