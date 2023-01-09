import os
import pandas as pd

from template_generation_utils import read_csv_to_dict, generate_dendrogram_tree
from nomenclature_tools import nomenclature_2_nodes_n_edges

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


def log_root_nodes(nomenclature_name):
    """


    """
    taxonomy_file_path = os.path.join(DENDROGRAM_FOLDER, nomenclature_name)
    dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
    tree = generate_dendrogram_tree(dend)

    all_internediate_nodes = [x for x in tree.nodes(data=True) if tree.in_degree(x[0]) > 0 and tree.out_degree(x[0]) > 0]
    all_internediate_nodes.sort(key=lambda x: int(str(x[0]).split("_")[1]))
    for int_node in all_internediate_nodes:
        print("    - Node: " + int_node[0])
        print("      Cell_type: CL:0000000")
        print("      Location_relation: has_soma_location")


# convert_tsv_to_csv("nomenclature_with_mba.tsv", "nomenclature_table_CS202211210.csv")
log_root_nodes("nomenclature_table_CS202211210.csv")
