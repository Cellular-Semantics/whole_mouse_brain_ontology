#!/usr/bin/env python3
import json
import csv
import os
import re

current_dir = os.path.dirname(os.path.realpath(__file__))
CAS_PATH = os.path.join(current_dir, "../../CCN20230722.json")
OUTPUT_PATH = os.path.join(current_dir, "CL_ontology_subset.tsv")


# Define the desired order for labelsets.
LABELSET_ORDER = {
    "class": 0,
    "subclass": 1,
    "supertype": 2,
    "cluster": 3,
}


def get_accession_index(cell_set):
    """
    Extracts the integer from the last underscore-delimited part of a cell_set_accession.
    For example, from "CS20230722_CLAS_01" it extracts 1.
    """
    parts = cell_set.split("_")
    if parts:
        try:
            return int(parts[-1])
        except ValueError:
            # In case the last part is not directly an integer, capture digits.
            match = re.search(r'(\d+)$', parts[-1])
            if match:
                return int(match.group(1))
    return 0


def sort_key(annotation):
    """
    Returns a tuple to use for sorting:
      - First element: index of the labelset based on LABELSET_ORDER.
      - Second element: the integer from the last part of cell_set_accession.

    If the annotation does not have a labelset from LABELSET_ORDER, it is sorted last.
    """
    labelset = annotation.get("labelset", "").lower()
    order = LABELSET_ORDER.get(labelset, 99)
    cell_set_acc = annotation.get("cell_set_accession", "")
    last_int = get_accession_index(cell_set_acc) if cell_set_acc else 0
    return order, last_int


def main():
    # Load the JSON file.
    with open(CAS_PATH, "r") as json_file:
        cas = json.load(json_file)

    annotations = cas.get("annotations", [])

    filtered_annotations = [
        ann for ann in annotations
        if ann.get("labelset", "").lower() != "neurotransmitter"
    ]

    # Sort annotations:
    #   1. By labelset in the order: class, subclass, supertype, cluster.
    #   2. Within the same labelset, by the integer extracted from cell_set_accession.
    sorted_annotations = sorted(filtered_annotations, key=sort_key)

    # Write the TSV file with columns: cell_set_accession, cell_label, Add_toCL (empty).
    with open(OUTPUT_PATH, "w", newline="") as tsvfile:
        writer = csv.writer(tsvfile, delimiter="\t")
        writer.writerow(["cell_set_accession", "cell_label", "Add_to_CL"])
        for ann in sorted_annotations:
            cell_set_accession = ann.get("cell_set_accession", "")
            cell_label = ann.get("cell_label", "")
            writer.writerow([cell_set_accession, cell_label, ""])

    print(f"TSV file created: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()