#!/usr/bin/env python3
import csv
import os
import argparse
import logging


current_dir = os.path.dirname(os.path.realpath(__file__))
OLD_TABLE_PATH = os.path.join(current_dir, f"../patterns/data/default/CCN20230722_class_curation_old.tsv")
CURRENT_TABLE_PATH = os.path.join(current_dir, f"../patterns/data/default/CCN20230722_class_curation.tsv")
OUTPUT_TABLE_PATH = os.path.join(current_dir, f"../patterns/data/default/CCN20230722_class_curation_new.tsv")

logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')


def read_tsv(filename):
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
    return rows, reader.fieldnames


def write_tsv(filename, fieldnames, rows):
    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)


def merge_tables(old_file, new_file, output_file):
    old_rows, old_fields = read_tsv(old_file)
    new_rows, new_fields = read_tsv(new_file)

    ignore_cols = {"cell_set_accession", "defined_class", "Taxonomy_label"}

    old_dict = {row["cell_set_accession"]: row for row in old_rows}
    # Process each new row: if annotation exists in old then copy over manual annotations
    for new_row in new_rows:
        cell_access = new_row.get("cell_set_accession")
        if not cell_access:
            continue
        old_row = old_dict.get(cell_access)
        if old_row:
            for col, value in old_row.items():
                if col in ignore_cols:
                    continue
                if col in new_fields:
                    new_row[col] = value
                else:
                    logging.warning(
                        "Column %s from old file is missing in new file (cell_set_accession: %s)",
                        col, cell_access)

    write_tsv(output_file, new_fields, new_rows)


if __name__ == "__main__":
    merge_tables(OLD_TABLE_PATH, CURRENT_TABLE_PATH, OUTPUT_TABLE_PATH)