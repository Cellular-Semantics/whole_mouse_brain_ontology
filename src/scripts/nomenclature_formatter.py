import os

import networkx as nx
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


def reformat_csv(nomenclature_name: str, new_name: str):
    """
    Original nomenclature has quotations and an index column. This functions formats input csv to the standard form.
    Args:
        nomenclature_name: original nomenclature
        new_name: output file name

    Returns:
    """
    taxonomy_file_path = os.path.join(DENDROGRAM_FOLDER, nomenclature_name)
    headers, data = read_csv_to_dict(taxonomy_file_path, id_column=1)

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
    Creates dendrogram config roots for all intermediate nodes.
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


def list_level2_nodes(nomenclature_name):
    """
    Lists all nodes that are direct parents of the leaf nodes
    """
    taxonomy_file_path = os.path.join(DENDROGRAM_FOLDER, nomenclature_name)
    dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
    tree = generate_dendrogram_tree(dend)

    leaf_nodes = [x[0] for x in tree.nodes(data=True) if tree.out_degree(x[0]) == 0]
    higher_level_nodes = [x[0] for x in tree.nodes(data=True) if tree.out_degree(x[0]) > 0]

    l1_nodes = set()
    for leaf_node in leaf_nodes:
        for predecessor in tree.predecessors(leaf_node):
            l1_nodes.add(predecessor)
    target_group = [x for x in higher_level_nodes if x not in l1_nodes]

    print("Leaf count: " + str(len(leaf_nodes)))
    print("L1 count: " + str(len(l1_nodes)))
    print("Higher count: " + str(len(target_group)))

    my_list = list()
    for o in dend['nodes']:
        if o['cell_set_accession'] in l1_nodes and o['cell_set_preferred_alias']:
            my_list.append(o['cell_set_preferred_alias'])
            print(o['cell_set_preferred_alias'] + "(" + o['cell_set_accession'] + ")")

    # shawn_list = ['All cells', 'IT-ET|IT-ET', 'NP-CT-L6b|NP-CT-L6b', 'DG-MOB-IMN', 'CGE', 'MGE', 'CNU GABA', 'LSX', 'TH', 'HY MM Glut', 'CNU-HY GABA', 'CNU-HYa Glut', 'HY Glut', 'MB Glut', 'P Glut', 'MY Glut', 'P Gaba', 'MY Gaba','MB Gaba', 'CB Gaba', 'CB Grandule', 'Neuroglial', 'Vascular', 'Immune', 'Pallium glutamatergic', 'Subpallium GABAergic', 'PAL-sAMY-TH-HY-MB-HB neuronal', 'CBX-MOB-other neuronal', 'CGE-MGE', 'HEAD', 'HEAD-Gaba1', 'HEAD-Gaba2', 'HEAD-Glut', 'MB-HB', 'MB-HB-Gaba', 'MB-HB-Glut', 'NN-IMN-GC', 'Other-Sub-Gaba', 'Pallium_Glut', 'Subpallium-GABA', 'TH-EPI']
    #
    # mine_not_in_shawn = [x for x in my_list if x not in shawn_list]
    # print(mine_not_in_shawn)
    # shawn_not_in_mine = [x for x in shawn_list if x not in my_list]
    # print(shawn_not_in_mine)


# convert_tsv_to_csv("nomenclature_with_curation.tsv", "nomenclature_table_CS202211210.csv")
reformat_csv("CCN_nomenclature_table_WMB.csv", "nomenclature_table_CS202212150.csv")
# # log_root_nodes("nomenclature_table_CS202211210.csv")
# list_level2_nodes("nomenclature_table_CS202211210.csv")
