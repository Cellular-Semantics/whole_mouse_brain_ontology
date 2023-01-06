import os
import pandas as pd

from template_generation_utils import read_csv_to_dict

DENDROGRAM_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms")


def convert_tsv_to_csv(nomenclature_name: str, new_name: str):
    taxonomy_file_path = os.path.join(DENDROGRAM_FOLDER, nomenclature_name)
    headers, data = read_csv_to_dict(taxonomy_file_path, delimiter="\t", id_column=1)

    all_data = []
    for accession_id in data:
        row_data = {}
        for header in headers:
            if header:
                row_data[header] = data[accession_id][header]
        all_data.append(row_data)

    class_robot_template = pd.DataFrame.from_records(all_data)
    class_robot_template.to_csv(os.path.join(DENDROGRAM_FOLDER, new_name), sep=",", index=False)


convert_tsv_to_csv("nomenclature_with_mba.tsv", "nomenclature_table_CS202211210.csv")
