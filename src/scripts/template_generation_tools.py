import pandas as pd
import os
import ast
import csv
import json
import logging
from rdflib import Graph, Namespace
from rdflib.namespace import RDFS

from dendrogram_tools import cas_json_2_nodes_n_edges, read_json_file
from template_generation_utils import read_taxonomy_config, generate_dendrogram_tree, read_csv_to_dict,\
    get_gross_cell_type, merge_tables, \
    extract_taxonomy_name_from_path, get_collapsed_nodes, read_one_concept_one_name_tsv, format_cell_label, get_class_membership_dict
from disclaimer_generator import (get_anatomical_location_inconsistencies, get_location_symbols,
                                  get_neurotransmitter_inconsistencies)
from pcl_id_factory import PCLIdFactory
from cl_id_factory import CLIdFactory
from clm_id_factory import CLMIdFactory


log = logging.getLogger(__name__)


PCL_BASE = 'http://purl.obolibrary.org/obo/PCL_'
CL_BASE = 'http://purl.obolibrary.org/obo/CL_'
CLM_BASE = 'http://purl.obolibrary.org/obo/CLM_'
PCL_INDV_BASE = 'http://purl.obolibrary.org/obo/pcl/'
BICAN_INDV_BASE = 'https://purl.brain-bican.org/taxonomy/CCN20230722/'

PCL_PREFIX = 'PCL:'

# This is the minimum threshold for a brain region to be considered significant in the context of the template generation.
BRAIN_REGION_THRESHOLD = 0.1

TEMPLATES_FOLDER_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../templates/")
MARKER_PATH = '../markers/CS{}_markers.tsv'
ALLEN_MARKER_PATH = "../markers/CS{}_Allen_markers.tsv"
NOMENCLATURE_TABLE_PATH = '../dendrograms/nomenclature_table_{}.csv'
ENSEMBLE_PATH = os.path.join(TEMPLATES_FOLDER_PATH, "{}.tsv")

CLUSTER_ANNOTATIONS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                        '../dendrograms/supplementary/version2/cluster_annotation_CCN20230722.csv')
# NT_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/version2/neurotransmitters.tsv")
NT_SYMBOLS_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/version2/Neurotransmitter_symbols_mapping.tsv")
BRAIN_REGION_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/Brain_region_mapping.tsv")

CROSS_SPECIES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  "../dendrograms/nomenclature_table_CCN202002270.csv")
NAME_CURATION_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/version2/one_concept_one_name_curation.tsv")
CL_SUBSET_TABLE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/version2/CL_ontology_subset.tsv")
ABC_URLS_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/CCN20230722_abc_urls.json")
ABC_URLS_MARKER_SET_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/CCN20230722_abc_urls_marker_set.json")
ABC_URLS_NSF_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/CCN20230722_abc_urls_nsforest_marker_set.json")
ABC_URLS_WS_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/CCN20230722_abc_urls_ws_marker_set.json")
ABC_URLS_EVIDENCE_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/CCN20230722_abc_urls_evidence_marker_set.json")

# centralized data files
ALLEN_DESCRIPTIONS_PATH = "{}/{}/All Descriptions_{}.json"
DATASET_INFO_CSV = "{}/{}/{}_landingpage_dataset_info.csv"
TAXONOMY_INFO_CSV = "{}/{}/{}_Taxonomy_Info_Panel.csv"
NSFOREST_MARKER_CSV = "{}/NSForestMarkers/{}_{}_NSForest_Markers.csv"

EXPRESSION_SEPARATOR = "|"

ACRONYM_REGION = "CCF acronym region"
BROAD_REGION = "CCF broad region"


def generate_ind_template(taxonomy_file_path, output_filepath):
    path_parts = taxonomy_file_path.split(os.path.sep)
    taxon = path_parts[-1].split(".")[0]

    dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
    all_nodes = {node['cell_set_accession']: node for node in dend['nodes']}
    pcl_id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))
    cl_id_factory = CLIdFactory(read_json_file(taxonomy_file_path))

    dend_tree = generate_dendrogram_tree(dend)
    nodes_to_collapse = get_collapsed_nodes(dend_tree, all_nodes)
    class_membership = get_class_membership_dict(dend_tree)

    excluded_classes = get_excluded_classes(taxon)
    atlas_payloads = read_abc_urls(ABC_URLS_MAPPING)
    cl_subset = get_cl_subset_nodes(nodes_to_collapse)

    # dend_tree = generate_dendrogram_tree(dend)
    # taxonomy_config = read_taxonomy_config(taxon)
    # subtrees = get_subtrees(dend_tree, taxonomy_config)

    robot_template_seed = {'ID': 'ID',
                           'Label': 'LABEL',
                           'PrefLabel': 'A skos:prefLabel',
                           'Entity Type': 'TI %',
                           'TYPE': 'TYPE',
                           'Property Assertions': "I 'subcluster of' SPLIT=|",
                           'Synonyms': 'A oboInOwl:hasExactSynonym SPLIT=|',
                           'Cluster_ID': "A 'cluster id'",
                           'Function': 'TI capable_of some %',
                           'cell_set_preferred_alias': "A n2o:cell_set_preferred_alias",
                           'original_label': "A n2o:original_label",
                           'cell_set_label': "A n2o:cell_set_label",
                           'cell_set_aligned_alias': "A n2o:cell_set_aligned_alias",
                           'cell_set_additional_aliases': "A n2o:cell_set_additional_aliases SPLIT=|",
                           'cell_set_alias_assignee': "A n2o:cell_set_alias_assignee SPLIT=|",
                           'cell_set_alias_citation': "A n2o:cell_set_alias_citation SPLIT=|",
                           'Metadata': "A n2o:node_metadata",
                           'Exemplar_of': "TI 'exemplar data of' some %",
                           'Comment': "A rdfs:comment",
                           'Aliases': "A oboInOwl:hasRelatedSynonym SPLIT=|",
                           'Rank': "A 'cell_type_rank' SPLIT=|",
                           'Atlas_url': "A rdfs:seeAlso",
                           'Atlas_url_label': ">A rdfs:label",
                           'Matrix_url': "A rdfs:seeAlso",
                           'Matrix_url_label': ">A rdfs:label",
                           'Matrix_url_comment': ">A rdfs:comment",
                           }
    dl = [robot_template_seed]

    for o in dend['nodes']:
        d = dict()
        d['ID'] = 'BICAN_INDV:' + o['cell_set_accession']
        d['TYPE'] = 'owl:NamedIndividual'
        # d['Label'] = o['cell_label'] + ' - ' + o['cell_set_accession']
        if 'cell_set_preferred_alias' in o and o['cell_set_preferred_alias']:
            d['PrefLabel'] = o['cell_set_preferred_alias']
        else:
            d['PrefLabel'] = o['cell_label'] + " "+ o['cell_set_accession']
        d['Label'] = d['PrefLabel']
        d['Entity Type'] = 'PCL:0010001'  # Cluster
        # d['Metadata'] = json.dumps(o)
        d['Synonyms'] = '|'.join(o.get('synonyms', []))
        d['Property Assertions'] = '|'.join(
            sorted(['BICAN_INDV:' + e[1] for e in dend['edges'] if e[0] == o['cell_set_accession'] and e[1]]))
        meta_properties = ['cell_fullname']
        for prop in meta_properties:
            if prop in o.keys():
                d[prop] = '|'.join([prop_val.strip() for prop_val in str(o[prop]).split("|") if prop_val])
            else:
                d[prop] = ''
        d['Cluster_ID'] = o['cell_set_accession']

        if o['cell_set_accession'] in cl_subset:
            id_factory = cl_id_factory
            id_base = CL_BASE
        else:
            id_factory = pcl_id_factory
            id_base = PCL_BASE
        if o['cell_set_accession'] in nodes_to_collapse:
            class_url = id_base + id_factory.get_class_id(nodes_to_collapse[o['cell_set_accession']]['cell_set_accession'])
        else:
            class_url = id_base + id_factory.get_class_id(o['cell_set_accession'])
        if class_url not in excluded_classes:
            d['Exemplar_of'] = class_url
        if atlas_payloads.get(o["cell_set_accession"]):
            d["Atlas_url"] = "https://knowledge.brain-map.org/abcatlas#" + atlas_payloads.get(
                o["cell_set_accession"])
            d["Atlas_url_label"] = "Reference data on Allen Brain Cell Atlas"
        d["Matrix_url"] = "https://purl.brain-bican.org/taxonomy/CCN20230722/" + class_membership[o["cell_set_accession"]] + ".h5ad"
        d["Matrix_url_label"] = "h5ad data file for " + class_membership[o["cell_set_accession"]]
        d["Matrix_url_comment"] = "Warning large data file!"

        if "author_annotation_fields" in o:
            for k, v in o["author_annotation_fields"].items():
                if v and str(v).lower() != "none":
                    d[k] = v
                    if k not in robot_template_seed.keys():
                        robot_template_seed[k] = "A https://purl.brain-bican.org/taxonomy/CCN20230722#" + k.replace(" ", "_").replace(".", "_")

        dl.append(d)
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_base_class_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
        all_nodes = {node['cell_set_accession']: node for node in dend['nodes']}
        all_names = {node['cell_label']: node for node in dend['nodes']}
        pcl_id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))
        cl_id_factory = CLIdFactory(read_json_file(taxonomy_file_path))
        clm_id_factory = CLMIdFactory(read_json_file(taxonomy_file_path))

        dend_tree = generate_dendrogram_tree(dend)
        nodes_to_collapse = get_collapsed_nodes(dend_tree, all_nodes)
        name_curations = read_one_concept_one_name_tsv(NAME_CURATION_MAPPING)
        # subtrees = get_subtrees(dend_tree, taxonomy_config)
        all_pref_labels = get_all_unique_cell_labels(dend, nodes_to_collapse, all_names, name_curations)
        class_membership = get_class_membership_dict(dend_tree)
        cl_subset = get_cl_subset_nodes(nodes_to_collapse)

        gene_db = read_gene_dbs(TEMPLATES_FOLDER_PATH)
        author_markers = read_author_markers_dataframe()
        author_local_markers = read_author_local_markers_dataframe()
        ns_forest_markers = read_nsforest_markers_dataframe()

        cluster_annotations = read_csv_to_dict(CLUSTER_ANNOTATIONS_PATH, id_column_name="cell_set_accession.cluster")[1]
        nt_symbols_mapping = read_csv_to_dict(NT_SYMBOLS_MAPPING, delimiter="\t")[1]
        mba_symbols = get_mba_symbols_map()
        mba_labels = get_mba_labels_map()
        anatomical_loc_inconsistencies = get_anatomical_location_inconsistencies(CLUSTER_ANNOTATIONS_PATH)
        nt_inconsistencies = get_neurotransmitter_inconsistencies(CLUSTER_ANNOTATIONS_PATH)
        atlas_payloads = read_abc_urls(ABC_URLS_MAPPING)

        class_seed = ['defined_class',
                      'prefLabel',
                      'Taxonomy_label',
                      'Alias_citations',
                      'Short_form_citation',
                      'Synonyms_from_taxonomy',
                      'Gross_cell_type',
                      'Taxon',
                      'Taxon_abbv',
                      'Brain_region',
                      'Minimal_markers',
                      'Allen_markers',
                      'Individuals',
                      'Brain_region_abbv',
                      'Species_abbv',
                      'Cluster_IDs',
                      'Labelset',
                      'Dataset_url',
                      'part_of',
                      'has_soma_location',
                      'aligned_alias',
                      'Parent_label',
                      'NT',
                      'NT_label',
                      'NT_markers',
                      'CL',
                      'Nomenclature_Layers',
                      'Nomenclature_Projection',
                      'evidence_marker_gene_set',
                      'marker_gene_set',
                      'marker_gene_set_confidence',
                      'ws_marker_gene_set',
                      'ws_marker_gene_set_confidence',
                      'nsforest_marker_gene_set_1',
                      'nsforest_marker_gene_set_1_confidence',
                      'nsforest_marker_gene_set_2',
                      'nsforest_marker_gene_set_2_confidence',
                      'MBA',
                      'MBA_text',
                      'Subclass_markers',
                      'Location_disclaimer',
                      'NT_disclaimer',
                      'Atlas_url',
                      'Atlas_url_label',
                      'Matrix_url',
                      'Class_name',
                      ]
        class_template = []
        obsolete_template = []
        processed_accessions = set()
        terms_moved_to_cl_subset = []
        for o in dend['nodes']:
            node = o
            if o['cell_set_accession'] in nodes_to_collapse:
                node = nodes_to_collapse[o['cell_set_accession']]
                collapsed = True
            else:
                collapsed = False
            if node.get('cell_set_accession') and node['cell_set_accession'] not in processed_accessions:
                d = dict()
                if o['cell_set_accession'] in cl_subset:
                    id_factory = cl_id_factory
                    marker_id_factory = clm_id_factory
                    id_base = CL_BASE
                    marker_id_base = CLM_BASE
                else:
                    id_factory = pcl_id_factory
                    marker_id_factory = pcl_id_factory
                    id_base = PCL_BASE
                    marker_id_base = PCL_BASE

                d['defined_class'] = id_base + id_factory.get_class_id(node['cell_set_accession'])

                d["prefLabel"] = all_pref_labels[node['cell_set_accession']]
                if node.get('taxonomy_cell_label'):
                    d["Taxonomy_label"] = node['taxonomy_cell_label']
                else:
                    d["Taxonomy_label"] = node['cell_label']
                synonyms = node.get("synonyms", [])
                synonyms.append(node['cell_label'])
                if collapsed:
                    synonyms.extend([ all_nodes[accession_id]['cell_label'] for accession_id in node["chain"]])
                d['Synonyms_from_taxonomy'] = "|".join(sorted(list(set(synonyms))))
                d['Gross_cell_type'] = get_gross_cell_type(node['cell_set_accession'], dend['nodes'])
                d['Taxon'] = taxonomy_config['Species'][0]
                d['Taxon_abbv'] = taxonomy_config['Gene_abbv'][0]
                d['Brain_region'] = taxonomy_config['Brain_region'][0]
                cluster_id = node['cell_set_accession']
                if collapsed:
                    cluster_id = "|".join(node["chain"])
                d['Cluster_IDs'] = cluster_id
                d['Labelset'] = node['labelset'].capitalize()
                d['Dataset_url'] = "https://purl.brain-bican.org/taxonomy/CCN20230722"
                reference_paper = "https://doi.org/10.1038/s41586-023-06812-z"
                if 'rationale_dois' in node and node['rationale_dois']:
                    alias_citations = {citation.strip() for citation in node['rationale_dois']
                                       if citation and citation.strip()}
                    alias_citations.add(reference_paper)
                    d["Alias_citations"] = "|".join(alias_citations)
                else:
                    d["Alias_citations"] = reference_paper
                d["Short_form_citation"] = "Yao et al. (2023), Whole Mouse Brain"
                if node.get('parent_cell_set_accession'):
                    d['Parent_label'] = all_pref_labels[node['parent_cell_set_accession']]
                markers_str = node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo", "")
                markers_list = [marker.strip() for marker in markers_str.split(",") if marker.strip()]
                d['Minimal_markers'] = "|".join([get_gene_id(gene_db, marker) for marker in markers_list if str(marker).lower() != "none"])

                d['Allen_markers'] = ""
                if 'Brain_region_abbv' in taxonomy_config:
                    d['Brain_region_abbv'] = taxonomy_config['Brain_region_abbv'][0]
                if 'Species_abbv' in taxonomy_config:
                    d['Species_abbv'] = taxonomy_config['Species_abbv'][0]
                d['Individuals'] = BICAN_INDV_BASE + node['cell_set_accession']
                d['part_of'] = ''
                d['has_soma_location'] = taxonomy_config['Brain_region'][0]


                associate_marker_sets(all_nodes, author_local_markers, author_markers, collapsed, d,
                                      marker_id_factory, marker_id_base, node, ns_forest_markers, o)

                if "cell_ontology_term_id" in node and node["cell_ontology_term_id"]:
                    d['CL'] = node["cell_ontology_term_id"]
                else:
                    d['CL'] = ""

                d['NT'] = ""
                d['NT_markers'] = ""
                if node.get('neurotransmitter_accession'):
                    nt_accession = node.get('neurotransmitter_accession')
                    if nt_accession in nt_symbols_mapping:
                        d['NT'] = nt_symbols_mapping.get(nt_accession)["CELL TYPE NEUROTRANSMISSION ID"]
                        d['NT_label'] = " and ".join(nt_symbols_mapping.get(nt_accession)["CELL TYPE LABEL"].split("|"))
                if node.get('neurotransmitter_marker_gene_evidence'):
                    nt_marker_names = node.get('neurotransmitter_marker_gene_evidence')
                    d['NT_markers'] = "|".join(nt_marker_names)
                    for i in range(1, 9):
                        if i <= len(nt_marker_names):
                            d['NT_marker_' + str(i)] = get_gene_id(gene_db, nt_marker_names[i - 1])
                        else:
                            d['NT_marker_' + str(i)] = ''
                    if len(nt_marker_names) > 8:
                        raise ValueError("More than 8 NT markers found for cluster: " + node['cell_set_accession'])

                missed_regions = set()
                if node['cell_set_accession'] in cluster_annotations:
                    ccf_broad_freq = cluster_annotations[node['cell_set_accession']]["CCF_broad.freq"]
                    ccf_acronym_freq = cluster_annotations[node['cell_set_accession']]["CCF_acronym.freq"]

                    # BROAD_REGION:
                    broad_mbas, mba_text = populate_mba_relations(ccf_broad_freq, BROAD_REGION, d, 1, mba_symbols, mba_labels, missed_regions)
                    d['MBA'] = "|".join(broad_mbas)
                    d['MBA_text'] = ", ".join(mba_text)
                    # ACRONYM_REGION:
                    acronym_mbas, mba_text = populate_mba_relations(ccf_acronym_freq, ACRONYM_REGION, d, len(broad_mbas) + 1, mba_symbols, mba_labels, missed_regions, broad_mbas)
                    acronym_mbas = [acronym_mba for acronym_mba in acronym_mbas if acronym_mba not in broad_mbas]
                    d['CCF_acronym_freq'] = "|".join(acronym_mbas)

                d['MBA_assay'] = "EFO:0008992"
                for missed_region in missed_regions:
                    print("MBA symbol not found for region: ", missed_region)

                d["Subclass_markers"] = (node.get("author_annotation_fields", dict()).
                                         get("cluster.markers.combo _within subclass_", "").replace("None", "").replace(",", "|"))
                if node["cell_label"] in anatomical_loc_inconsistencies:
                    mentioned_locations = get_location_symbols(node["cell_label"])
                    inconsistent_locations = anatomical_loc_inconsistencies[node["cell_label"]]
                    location_names = ", ".join([mba_labels[mba_symbols[loc]] + " (" + loc + ")" for loc in inconsistent_locations])
                    if len(mentioned_locations) == len(inconsistent_locations):
                        d["Location_disclaimer"] = "Warning: This type {name} does not have cells in any of the regions it is named for {location_names}. " \
                         "The name merely indicates that it is a subtype of more general transcriptomic type that does. This assertion is based on data " \
                         "from registration to a reference standard common co-ordinate framework and parcelation scheme.".format(name=d["prefLabel"], location_names=location_names)
                    else:
                        d["Location_disclaimer"] = ("Warning: Despite its name, {name} does not have cells in {location_names}. " 
                                                    "This assertion is based on data from registration to a reference standard common co-ordinate "
                                                    "framework and parcelation scheme.").format(name=d["prefLabel"], location_names=location_names)
                if node["cell_set_accession"] in nt_inconsistencies:
                    inconsistent_nts = nt_inconsistencies[node["cell_set_accession"]]
                    d["NT_disclaimer"] = "Warning: Despite its name, {name} does not secrete the neurotransmitter {nt}, as assessed by expression of multiple marker genes.".format(name=d["prefLabel"], nt=", ".join(inconsistent_nts))

                if atlas_payloads.get(o["cell_set_accession"]):
                    d["Atlas_url"] = "https://knowledge.brain-map.org/abcatlas#" + atlas_payloads.get(
                        o["cell_set_accession"])
                    d["Atlas_url_label"] = "Reference data on Allen Brain Cell Atlas"

                d["Matrix_url"] = "https://purl.brain-bican.org/taxonomy/CCN20230722/" + \
                                  class_membership[node["cell_set_accession"]] + ".h5ad"
                d["Class_name"] = class_membership[node["cell_set_accession"]]

                for k in class_seed:
                    if not (k in d.keys()):
                        d[k] = ''
                class_template.append(d)
                processed_accessions.add(node['cell_set_accession'])

                if o['cell_set_accession'] in cl_subset:
                    cloned = d.copy()
                    cloned['cell_set_accession'] = node['cell_set_accession']
                    terms_moved_to_cl_subset.append(cloned)
            else:
                # process obsoleted classes due to chain compressing
                if collapsed and o.get('cell_set_accession') not in processed_accessions:
                    d = dict()
                    d['defined_class'] = PCL_BASE + pcl_id_factory.get_class_id(o['cell_set_accession'])
                    d['prefLabel'] = "obsolete " + o['cell_label']
                    d['Comment'] = "This class is obsoleted due to chain compression."
                    d['Deprecated'] = "true"
                    d['Gross_cell_type'] = get_gross_cell_type(o['cell_set_accession'],
                                                               dend['nodes'])
                    d['Taxon'] = taxonomy_config['Species'][0]
                    d['Taxon_abbv'] = taxonomy_config['Gene_abbv'][0]
                    d['Comment'] = "This term is obsoleted due to identical cell set chain compression."
                    d['Classification'] = "CL:0000000"
                    d['ReplacedBy'] = ""
                    obsolete_template.append(d)

        for cl_obsolete in terms_moved_to_cl_subset:
            obsolete_d = dict()
            obsolete_d['defined_class'] = PCL_BASE + pcl_id_factory.get_class_id(cl_obsolete['cell_set_accession'])
            obsolete_d['prefLabel'] = "obsolete " + cl_obsolete['prefLabel']
            obsolete_d['Comment'] = "This PCL class is no longer in use; it has been relocated to CL."
            obsolete_d['Deprecated'] = "true"
            obsolete_d['Gross_cell_type'] = cl_obsolete['Gross_cell_type']
            obsolete_d['Classification'] = "CL:0000000"
            obsolete_d['ReplacedBy'] = cl_obsolete['defined_class']
            obsolete_template.append(obsolete_d)

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)
        if obsolete_template:
            obsolete_filepath = output_filepath.replace("_base.tsv", "_obsolete.tsv")
            class_obsolete_template = pd.DataFrame.from_records(obsolete_template)
            class_obsolete_template.to_csv(obsolete_filepath, sep="\t", index=False)


def associate_marker_sets(all_nodes, author_local_markers, author_markers, collapsed, d, id_factory,
                          id_prefix, node, ns_forest_markers, o):
    """
    Associates the following marker sets to the node:
    - evidence_marker_gene_set
    - marker_gene_set
    - within_subclass_marker_gene_set
    - nsforest_marker_gene_sets
    Args:
        all_nodes:
        author_local_markers:
        author_markers:
        collapsed:
        d:
        id_factory:
        id_prefix:
        node:
        ns_forest_markers:
        o:

    Returns:
    """
    d['aligned_alias'] = ""
    if node.get('marker_gene_evidence'):
        d['evidence_marker_gene_set'] = id_prefix + id_factory.get_evidence_marker_gene_set_id(
            node['cell_set_accession'])
    if ("author_annotation_fields" in node and
            node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo") and
            str(node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo",
                                                     "")).lower() != "none"):
        d['marker_gene_set'] = id_prefix + id_factory.get_marker_gene_set_id(
            node['cell_set_accession'])
        filtered_df = author_markers[author_markers['clusterName'] == o['cell_label']]
        if not filtered_df.empty:
            d['marker_gene_set_confidence'] = filtered_df['f_score'].values[0]
    if ("author_annotation_fields" in node and
            node["author_annotation_fields"].get(
                f"{node['labelset']}.markers.combo _within subclass_") and
            str(node["author_annotation_fields"].get(
                f"{node['labelset']}.markers.combo _within subclass_", "")).lower() != "none"):
        d['ws_marker_gene_set'] = id_prefix + id_factory.get_ws_marker_gene_set_id(
            node['cell_set_accession'])
        filtered_df = author_local_markers[author_local_markers['clusterName'] == o['cell_label']]
        if not filtered_df.empty:
            d['ws_marker_gene_set_confidence'] = filtered_df['f_score'].values[0]
    if not collapsed:
        filtered_df = ns_forest_markers[ns_forest_markers['clusterName'] == o['cell_label']]
        if not filtered_df.empty:
            d['nsforest_marker_gene_set_1'] = id_prefix + id_factory.get_nsf_marker_gene_set_id(
                node['cell_set_accession'])
            d['nsforest_marker_gene_set_1_confidence'] = filtered_df['f_score'].values[0]
    else:
        index = 1
        for collapsed_accession in node['chain']:
            collapsed_node = all_nodes[collapsed_accession]
            filtered_df = ns_forest_markers[
                ns_forest_markers['clusterName'] == collapsed_node['cell_label']]
            if not filtered_df.empty:
                d['nsforest_marker_gene_set_' + str(
                    index)] = id_prefix + id_factory.get_nsf_marker_gene_set_id(
                    collapsed_node['cell_set_accession'])
                d['nsforest_marker_gene_set_' + str(index) + '_confidence'] = \
                filtered_df['f_score'].values[0]
                index += 1


def get_all_unique_cell_labels(dend, nodes_to_collapse, all_names, name_curations):
    all_pref_labels = dict()

    processed_accessions = set()
    all_cell_set_labels = set()
    for o in dend['nodes']:
        node = o
        if o['cell_set_accession'] in nodes_to_collapse:
            node = nodes_to_collapse[o['cell_set_accession']]
            collapsed = True
        else:
            collapsed = False
        if node.get('cell_set_accession'):
            if node['cell_set_accession'] not in processed_accessions:
                all_pref_labels[o['cell_set_accession']] = get_unique_cell_label(o, node,
                                                                                 all_cell_set_labels,
                                                                                 all_names,
                                                                                 name_curations,
                                                                                 collapsed)
                processed_accessions.add(node['cell_set_accession'])
            else:
                all_pref_labels[o['cell_set_accession']] = get_unique_cell_label(o, node,
                                                                                 all_cell_set_labels,
                                                                                 all_names,
                                                                                 name_curations,
                                                                                 collapsed, fail_on_duplicate=False)
    return all_pref_labels

def get_unique_cell_label(o, node, generated_labels, all_names, name_curations, is_collapsed=False, fail_on_duplicate=True):
    """
    Provides a unique cell label by checking the manual curation and existing labels in the taxonomy.
    Args:
        o: Taxonomy node
        node: compressed node or 'o' if no compression
        generated_labels: all labels added to ontology
        all_names: all labels existing in the taxonomy
        name_curations: manual curation of cell labels
        is_collapsed: True if the node is part of a collapsed chain
        fail_on_duplicate: True if the function should raise an error if a duplicate label is found
    Returns: unique cell label
    """
    if o['cell_label'] in name_curations:
        cell_label = name_curations[o['cell_label']]
    else:
        cell_label = node['cell_label']
    cell_label = format_cell_label(cell_label, node, all_names, generated_labels, is_collapsed, fail_on_duplicate)
    generated_labels.add(cell_label)
    return cell_label


def populate_mba_relations(ccf_text, approach, d, index, mba_symbols, mba_labels, missed_regions, existing_mbas=None):
    """

    Args:
        ccf_text: ccf_broad_freq or ccf_acronym_freq text
        approach: broad vs acronym
        d: data node
        index: MBA id index offset
        mba_symbols: dict of MBA symbols - ids
        mba_labels: dict of MBA ids - labels
        missed_regions: regions couldn't be mapped
        existing_mbas: list of existing mbas to avoid duplication

    Returns: list of mba ids and mba percentage text

    """
    if existing_mbas is None:
        existing_mbas = []
    regions = [{"region": item.split(":")[0].strip(),
                "percentage": float(item.split(":")[1].strip()) if ":" in item else 0}
               for item in ccf_text.split(",")]
    mbas = []
    mba_text = []
    for region in regions:
        if region["percentage"] >= BRAIN_REGION_THRESHOLD:
            region_label = str(region["region"]).strip()
            if region_label.lower() == "na":
                region_label = 'root'  # handle NA as brain
            if mba_symbols.get(region_label) not in existing_mbas:
                if region_label in mba_symbols:
                    mbas.append(mba_symbols[region_label])
                    mba_text.append(mba_labels[mba_symbols[region_label]] + " (" + str(region["region"]) + ", " + str(region["percentage"]) + ")")
                    region["mba_id"] = mba_symbols[region_label]
                else:
                    missed_regions.add(region["region"])

    # Sort mbas and mba_text together
    sorted_pairs = sorted(zip(mbas, mba_text))
    mbas, mba_text = zip(*sorted_pairs) if sorted_pairs else ([], [])

    for i, mba in enumerate(mbas, start=index):
        d['MBA_' + str(i)] = mba
        region = [reg for reg in regions if reg.get("mba_id") == mba][0]
        d['MBA_' + str(i) + '_cell_percentage'] = region["percentage"]
        d['MBA_' + str(i) + '_comment'] = "Location assignment based on {}.".format(approach)

    return mbas, mba_text


def generate_curated_class_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
        all_nodes = {node['cell_set_accession']: node for node in dend['nodes']}
        pcl_id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))
        cl_id_factory = CLIdFactory(read_json_file(taxonomy_file_path))
        dend_tree = generate_dendrogram_tree(dend)
        nodes_to_collapse = get_collapsed_nodes(dend_tree, all_nodes)
        cl_subset = get_cl_subset_nodes(nodes_to_collapse)

        class_curation_seed = ['defined_class',
                               'cell_set_accession',
                               'Taxonomy_label',
                               'Exclude_from_ontology',
                               'defined_class_name',
                               'defined_class_definition',
                               'Curated_synonyms',
                               'Classification',
                               'Classification_comment',
                               'Classification_pub',
                               'Expresses',
                               'Expresses_comment',
                               'Expresses_pub',
                               'Projection_type',
                               'Locations',
                               'Neurotransmitters',
                               'Neurotransmitters_comment',
                               'Neurotransmitters_publication',
                               'Cross_species_text',
                               'Comment'
                               ]
        class_template = []
        processed_accessions = set()
        for o in dend['nodes']:
            node = o
            if o['cell_set_accession'] in nodes_to_collapse:
                node = nodes_to_collapse[o['cell_set_accession']]
            if node.get('cell_set_accession') and node['cell_set_accession'] not in processed_accessions:
                d = dict()
                if o['cell_set_accession'] in cl_subset:
                    id_factory = cl_id_factory
                    id_base = CL_BASE
                else:
                    id_factory = pcl_id_factory
                    id_base = PCL_BASE

                d['defined_class'] = id_base + id_factory.get_class_id(node['cell_set_accession'])
                d["cell_set_accession"] = node['cell_set_accession']
                d["Taxonomy_label"] = node['cell_label']
                d["Exclude_from_ontology"] = ""  # set `True` to exclude from ontology

                for k in class_curation_seed:
                    if not (k in d.keys()):
                        d[k] = ''
                class_template.append(d)
                processed_accessions.add(node['cell_set_accession'])

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_marker_gene_set_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
        all_nodes = {node['cell_set_accession']: node for node in dend['nodes']}
        all_names = {node['cell_label']: node for node in dend['nodes']}
        pcl_id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))
        clm_id_factory = CLMIdFactory(read_json_file(taxonomy_file_path))
        dend_tree = generate_dendrogram_tree(dend)
        nodes_to_collapse = get_collapsed_nodes(dend_tree, all_nodes)
        name_curations = read_one_concept_one_name_tsv(NAME_CURATION_MAPPING)
        author_markers = read_author_markers_dataframe()
        all_pref_labels = get_all_unique_cell_labels(dend, nodes_to_collapse, all_names,
                                                     name_curations)
        atlas_payloads = read_abc_urls(ABC_URLS_MARKER_SET_MAPPING)

        gene_db = read_gene_dbs(TEMPLATES_FOLDER_PATH)
        cl_subset = get_cl_subset_nodes(nodes_to_collapse)

        class_seed = ['defined_class',
                      'Marker_set_of',
                      'Markers',
                      'Markers_label',
                      'Species_abbv',
                      'Brain_region',
                      'Parent',
                      'FBeta_confidence_score',
                      'precision',
                      'recall',
                      'Algorithm',
                      'Source',
                      'Cell_label',
                      'Labelset',
                      'Atlas_url',
                      'Atlas_url_label'
                      ]
        class_template = []
        processed_accessions = set()
        marker_labels = dict()
        for o in dend['nodes']:
            node = o
            if o['cell_set_accession'] in nodes_to_collapse:
                node = nodes_to_collapse[o['cell_set_accession']]
            if node.get('cell_set_accession') and node['cell_set_accession'] not in processed_accessions :
                if ("author_annotation_fields" in node and
                        node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo", "") and
                        str(node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo", "")).lower() != "none"):
                    d = dict()
                    if node['cell_set_accession'] in cl_subset:
                        id_factory = clm_id_factory
                        id_base = CLM_BASE
                    else:
                        id_factory = pcl_id_factory
                        id_base = PCL_BASE

                    d['defined_class'] = id_base + id_factory.get_marker_gene_set_id(node['cell_set_accession'])
                    cell_set_label = all_pref_labels[node["cell_set_accession"]]
                    d['Marker_set_of'] = cell_set_label
                    markers_str = node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo", "")
                    markers_list = [marker.strip() for marker in markers_str.split(",")]
                    d['Markers'] = "|".join([get_gene_id(gene_db, marker) for marker in markers_list if str(marker).lower() != "none"])
                    d['Markers_label'] = node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo", "")
                    if d['Markers_label'] not in marker_labels:
                        marker_labels[d['Markers_label']] = 1
                    else:
                        # avoid label conflicts by appending a number
                        marker_labels[d['Markers_label']] += 1
                        d['Markers_label'] = d['Markers_label'] + " " + str(marker_labels[d['Markers_label']])
                    if 'Species_abbv' in taxonomy_config:
                        d['Species_abbv'] = taxonomy_config['Species_abbv'][0]
                    d['Brain_region'] = taxonomy_config['Brain_region'][0]
                    d['Parent'] = "SO:0001260"  # sequence collection
                    d['FBeta_confidence_score'] = ""
                    d['Algorithm'] = ""
                    d['Source'] = "Yao"
                    d['Reference'] = "https://doi.org/10.1038/s41586-023-06812-z"
                    filtered_df = author_markers[author_markers['clusterName'] == o['cell_label']]
                    if not filtered_df.empty:
                        d['FBeta_confidence_score'] = filtered_df['f_score'].values[0]
                        d['precision'] = filtered_df['precision'].values[0]
                        d['recall'] = filtered_df['recall'].values[0]
                    d['Cell_label'] = o['cell_label']
                    d['Labelset'] = o['labelset']
                    if d['defined_class'] in atlas_payloads:
                        d["Atlas_url"] = "https://knowledge.brain-map.org/abcatlas#" + atlas_payloads.get(d['defined_class'])
                        d["Atlas_url_label"] = "markers in reference data on Allen Brain Cell Atlas"

                    for k in class_seed:
                        if not (k in d.keys()):
                            d[k] = ''
                    class_template.append(d)
                    processed_accessions.add(node['cell_set_accession'])

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)

def generate_within_subclass_marker_gene_set_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
        all_nodes = {node['cell_set_accession']: node for node in dend['nodes']}
        all_names = {node['cell_label']: node for node in dend['nodes']}
        pcl_id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))
        clm_id_factory = CLMIdFactory(read_json_file(taxonomy_file_path))
        dend_tree = generate_dendrogram_tree(dend)
        nodes_to_collapse = get_collapsed_nodes(dend_tree, all_nodes)
        name_curations = read_one_concept_one_name_tsv(NAME_CURATION_MAPPING)
        author_local_markers = read_author_local_markers_dataframe()
        all_pref_labels = get_all_unique_cell_labels(dend, nodes_to_collapse, all_names,
                                                     name_curations)
        atlas_payloads = read_abc_urls(ABC_URLS_WS_MAPPING)

        gene_db = read_gene_dbs(TEMPLATES_FOLDER_PATH)
        cl_subset = get_cl_subset_nodes(nodes_to_collapse)

        class_seed = ['defined_class',
                      'Marker_set_of',
                      'Markers',
                      'Markers_label',
                      'Species_abbv',
                      'Brain_region',
                      'Parent',
                      'FBeta_confidence_score',
                      'precision',
                      'recall',
                      'Algorithm',
                      'Source',
                      'Cell_label',
                      'Labelset',
                      'Atlas_url',
                      'Atlas_url_label'
                      ]
        class_template = []
        processed_accessions = set()
        marker_labels = dict()
        for o in dend['nodes']:
            node = o
            if o['cell_set_accession'] in nodes_to_collapse:
                node = nodes_to_collapse[o['cell_set_accession']]
            if node.get('cell_set_accession') and node['cell_set_accession'] not in processed_accessions :
                if ("author_annotation_fields" in node and
                        node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo _within subclass_", "") and
                        str(node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo _within subclass_", "")).lower() != "none"):
                    d = dict()
                    if node['cell_set_accession'] in cl_subset:
                        id_factory = clm_id_factory
                        id_base = CLM_BASE
                    else:
                        id_factory = pcl_id_factory
                        id_base = PCL_BASE

                    d['defined_class'] = id_base + id_factory.get_ws_marker_gene_set_id(node['cell_set_accession'])
                    cell_set_label = all_pref_labels[node["cell_set_accession"]]
                    d['Marker_set_of'] = cell_set_label
                    markers_str = node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo _within subclass_", "")
                    markers_list = [marker.strip() for marker in markers_str.split(",")]
                    d['Markers'] = "|".join([get_gene_id(gene_db, marker) for marker in markers_list if str(marker).lower() != "none"])
                    d['Markers_label'] = node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo _within subclass_", "")
                    if d['Markers_label'] not in marker_labels:
                        marker_labels[d['Markers_label']] = 1
                    else:
                        # avoid label conflicts by appending a number
                        marker_labels[d['Markers_label']] += 1
                        d['Markers_label'] = d['Markers_label'] + " " + str(marker_labels[d['Markers_label']])
                    if 'Species_abbv' in taxonomy_config:
                        d['Species_abbv'] = taxonomy_config['Species_abbv'][0]
                    d['Brain_region'] = taxonomy_config['Brain_region'][0]
                    d['Parent'] = "SO:0001260"  # sequence collection
                    d['FBeta_confidence_score'] = ""
                    d['Algorithm'] = ""
                    d['Source'] = "Yao - within subclass"
                    d['Reference'] = "https://doi.org/10.1038/s41586-023-06812-z"
                    filtered_df = author_local_markers[author_local_markers['clusterName'] == o['cell_label']]
                    if not filtered_df.empty:
                        d['FBeta_confidence_score'] = filtered_df['f_score'].values[0]
                        d['precision'] = filtered_df['precision'].values[0]
                        d['recall'] = filtered_df['recall'].values[0]
                    d['Cell_label'] = o['cell_label']
                    d['Labelset'] = o['labelset']
                    if d['defined_class'] in atlas_payloads:
                        d["Atlas_url"] = "https://knowledge.brain-map.org/abcatlas#" + atlas_payloads.get(d['defined_class'])
                        d["Atlas_url_label"] = "markers in reference data on Allen Brain Cell Atlas"

                    for k in class_seed:
                        if not (k in d.keys()):
                            d[k] = ''
                    class_template.append(d)
                    processed_accessions.add(node['cell_set_accession'])

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_evidence_marker_gene_set_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
        all_nodes = {node['cell_set_accession']: node for node in dend['nodes']}
        all_names = {node['cell_label']: node for node in dend['nodes']}
        pcl_id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))
        clm_id_factory = CLMIdFactory(read_json_file(taxonomy_file_path))
        dend_tree = generate_dendrogram_tree(dend)
        nodes_to_collapse = get_collapsed_nodes(dend_tree, all_nodes)
        name_curations = read_one_concept_one_name_tsv(NAME_CURATION_MAPPING)
        all_pref_labels = get_all_unique_cell_labels(dend, nodes_to_collapse, all_names,
                                                     name_curations)
        atlas_payloads = read_abc_urls(ABC_URLS_EVIDENCE_MAPPING)

        gene_db = read_gene_dbs(TEMPLATES_FOLDER_PATH)
        cl_subset = get_cl_subset_nodes(nodes_to_collapse)

        class_seed = ['defined_class',
                      'Marker_set_of',
                      'Markers',
                      'Markers_label',
                      'Species_abbv',
                      'Brain_region',
                      'Parent',
                      'FBeta_confidence_score',
                      'precision',
                      'recall',
                      'Algorithm',
                      'Source',
                      'Cell_label',
                      'Labelset',
                      'Atlas_url',
                      'Atlas_url_label'
                      ]
        class_template = []
        processed_accessions = set()
        marker_labels = dict()
        for o in dend['nodes']:
            node = o
            if o['cell_set_accession'] in nodes_to_collapse:
                node = nodes_to_collapse[o['cell_set_accession']]
            if node.get('cell_set_accession') and node['cell_set_accession'] not in processed_accessions :
                if "marker_gene_evidence" in node and node["marker_gene_evidence"]:
                    d = dict()
                    if node['cell_set_accession'] in cl_subset:
                        id_factory = clm_id_factory
                        id_base = CLM_BASE
                    else:
                        id_factory = pcl_id_factory
                        id_base = PCL_BASE

                    d['defined_class'] = id_base + id_factory.get_evidence_marker_gene_set_id(node['cell_set_accession'])
                    cell_set_label = all_pref_labels[node["cell_set_accession"]]
                    d['Marker_set_of'] = cell_set_label
                    markers_list = [marker.strip() for marker in node["marker_gene_evidence"]]
                    d['Markers'] = "|".join([get_gene_id(gene_db, marker) for marker in markers_list if str(marker).lower() != "none"])
                    d['Markers_label'] = ", ".join(markers_list)
                    if d['Markers_label'] not in marker_labels:
                        marker_labels[d['Markers_label']] = 1
                    else:
                        # avoid label conflicts by appending a number
                        marker_labels[d['Markers_label']] += 1
                        d['Markers_label'] = d['Markers_label'] + " " + str(marker_labels[d['Markers_label']])
                    if 'Species_abbv' in taxonomy_config:
                        d['Species_abbv'] = taxonomy_config['Species_abbv'][0]
                    d['Brain_region'] = taxonomy_config['Brain_region'][0]
                    d['Parent'] = "SO:0001260"  # sequence collection
                    d['FBeta_confidence_score'] = ""
                    d['Algorithm'] = ""
                    d['Source'] = "CAS evidence"
                    d['Reference'] = ""
                    d['FBeta_confidence_score'] = ""
                    d['precision'] = ""
                    d['recall'] = ""
                    d['Cell_label'] = o['cell_label']
                    d['Labelset'] = o['labelset']
                    if d['defined_class'] in atlas_payloads:
                        d["Atlas_url"] = "https://knowledge.brain-map.org/abcatlas#" + atlas_payloads.get(d['defined_class'])
                        d["Atlas_url_label"] = "markers in reference data on Allen Brain Cell Atlas"

                    for k in class_seed:
                        if not (k in d.keys()):
                            d[k] = ''
                    class_template.append(d)
                    processed_accessions.add(node['cell_set_accession'])

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_nsforest_marker_gene_set_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
        all_nodes = {node['cell_set_accession']: node for node in dend['nodes']}
        all_names = {node['cell_label']: node for node in dend['nodes']}
        pcl_id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))
        clm_id_factory = CLMIdFactory(read_json_file(taxonomy_file_path))
        dend_tree = generate_dendrogram_tree(dend)
        nodes_to_collapse = get_collapsed_nodes(dend_tree, all_nodes)
        name_curations = read_one_concept_one_name_tsv(NAME_CURATION_MAPPING)
        nsforest_markers = read_nsforest_markers_dataframe()
        all_pref_labels = get_all_unique_cell_labels(dend, nodes_to_collapse, all_names,
                                                     name_curations)
        atlas_payloads = read_abc_urls(ABC_URLS_NSF_MAPPING)

        gene_db = read_gene_dbs(TEMPLATES_FOLDER_PATH)
        cl_subset = get_cl_subset_nodes(nodes_to_collapse)

        class_seed = ['defined_class',
                      'Marker_set_of',
                      'Markers',
                      'Markers_label',
                      'Species_abbv',
                      'Brain_region',
                      'Parent',
                      'FBeta_confidence_score',
                      'precision',
                      'recall',
                      'Algorithm',
                      'Source',
                      'Cell_label',
                      'Labelset',
                      'Atlas_url',
                      'Atlas_url_label'
                      ]
        class_template = []
        marker_labels = dict()
        for o in dend['nodes']:
            node = o
            if o['cell_set_accession'] in nodes_to_collapse:
                node = nodes_to_collapse[o['cell_set_accession']]
            if node.get('cell_set_accession'):
                filtered_df = nsforest_markers[nsforest_markers['clusterName'] == o['cell_label']]
                if not filtered_df.empty:
                    d = dict()
                    if node['cell_set_accession'] in cl_subset:
                        id_factory = clm_id_factory
                        id_base = CLM_BASE
                    else:
                        id_factory = pcl_id_factory
                        id_base = PCL_BASE

                    d['defined_class'] = id_base + id_factory.get_nsf_marker_gene_set_id(o['cell_set_accession'])
                    cell_set_label = all_pref_labels[node["cell_set_accession"]]
                    d['Marker_set_of'] = cell_set_label
                    markers_list = ast.literal_eval(filtered_df['markers'].values[0])  # convert "['Vxn', 'C1ql3']" string to list
                    d['Markers'] = "|".join([get_gene_id(gene_db, marker) for marker in markers_list])
                    d['Markers_label'] = ", ".join(markers_list)
                    if d['Markers_label'] not in marker_labels:
                        marker_labels[d['Markers_label']] = 1
                    else:
                        # avoid label conflicts by appending a number
                        marker_labels[d['Markers_label']] += 1
                        d['Markers_label'] = d['Markers_label'] + " " + str(marker_labels[d['Markers_label']])
                    if 'Species_abbv' in taxonomy_config:
                        d['Species_abbv'] = taxonomy_config['Species_abbv'][0]
                    d['Brain_region'] = taxonomy_config['Brain_region'][0]
                    d['Parent'] = "SO:0001260"  # sequence collection
                    d['FBeta_confidence_score'] = filtered_df['f_score'].values[0]
                    d['precision'] = filtered_df['PPV'].values[0]
                    d['recall'] = filtered_df['recall'].values[0]
                    d['Algorithm'] = "NSforest"
                    d['Source'] = "NSforest"
                    d['Reference'] = "https://doi.org/10.1101/2020.09.23.308932"
                    d['Cell_label'] = o['cell_label']
                    d['Labelset'] = o['labelset']
                    if d['defined_class'] in atlas_payloads:
                        d["Atlas_url"] = "https://knowledge.brain-map.org/abcatlas#" + atlas_payloads.get(d['defined_class'])
                        d["Atlas_url_label"] = "markers in reference data on Allen Brain Cell Atlas"

                    for k in class_seed:
                        if not (k in d.keys()):
                            d[k] = ''
                    class_template.append(d)

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def read_author_markers_dataframe():
    """
    Author markers dataframe is read from the CSV file.
    Returns: Author markers dataframe
    """
    author_marker_subclass_df = pd.read_csv(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     '../dendrograms/supplementary/version2/AP_WMB_evaluation_author_markers/subclass_results.csv'))
    author_marker_supertype_df = pd.read_csv(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     '../dendrograms/supplementary/version2/AP_WMB_evaluation_author_markers/supertype_results.csv'))
    author_marker_cluster_df = pd.read_csv(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     '../dendrograms/supplementary/version2/AP_WMB_evaluation_author_markers/cluster_results.csv'))
    author_markers = pd.merge(author_marker_subclass_df, author_marker_supertype_df,
                                how='outer')
    author_markers = pd.merge(author_markers, author_marker_cluster_df,
                                how='outer')
    return author_markers


def read_author_local_markers_dataframe():
    """
    Author local markers dataframe is read from the CSV file.
    Returns: Author markers dataframe
    """
    author_local_markers = pd.read_csv(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     '../dendrograms/supplementary/version2/AP_WMB_evaluation_author_markers/local_cluster_results.csv'))

    return author_local_markers


def read_nsforest_markers_dataframe():
    """
    NS Forest markers dataframe is read from the CSV file.
    Returns: NS Forest markers dataframe
    """
    ns_forest_marker_class_df = pd.read_csv(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     '../dendrograms/supplementary/version2/NSForest_global_class_results.csv'))
    ns_forest_marker_subclass_df = pd.read_csv(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     '../dendrograms/supplementary/version2/NSForest_global_subclass_comb_results.csv'))
    nsforest_markers = pd.merge(ns_forest_marker_class_df, ns_forest_marker_subclass_df,
                                how='outer')
    return nsforest_markers


def index_base_files(base_files):
    index = list()
    for base_file in base_files:
        headers, records = read_csv_to_dict(base_file, delimiter="\t", id_column_name="aligned_alias",
                                            id_to_lower=True)
        index.append(records)

    return index


def merge_class_templates(base_tsv, curation_tsv, output_filepath):
    """
    Applies all columns of the curation_tsv to the base_tsv and generates a new merged class template in the
    output_filepath.
    Args:
        base_tsv: Path of the base table to add new columns.
        curation_tsv: Path of the manual curations' table
        output_filepath: Output file path
    """
    merge_tables(base_tsv, curation_tsv, output_filepath)


def get_centralized_taxonomy_folder(taxonomy_config):
    """
    Expected folder name is: lower(Species_abbv) + Brain_region_abbv + "_" + Taxonomy_id
    Args:
        taxonomy_config: taxonomy configuration

    Returns: expected centralized data location for the given taxonomy
    """
    return str(taxonomy_config['Species_abbv'][0]).lower() + taxonomy_config['Brain_region_abbv'][0] \
           + "_" + taxonomy_config["Taxonomy_id"]

def get_gene_id(gene_db, gene_name):
    gene_name = gene_name.strip()
    gene_id = None
    if str(gene_name) in gene_db:
        gene_id = gene_db[str(gene_name)]
    else:
        # gene_db may have styling issues, so workaround
        for gene in gene_db:
            if gene_name.lower() in gene.lower():
                gene_id = gene_db[gene]
    if gene_id:
        if gene_id.startswith("ensembl:"):
            print("Using Ensembl gene ID for gene: {}".format(gene_name))
        return gene_id
    else:
        raise Exception(f"Gene ID not found for gene: {gene_name}")

def get_mba_symbols_map():
    obo_in_owl = Namespace("http://www.geneontology.org/formats/oboInOwl#")
    g = get_mba_ontology()

    synonyms = {}
    for s, p, o in g:
        if str(s).startswith("https://purl.brain-bican.org/ontology/mbao/MBA_") and p == obo_in_owl.hasExactSynonym:
            synonyms[str(o).strip()] = "MBA:" + str(s).split("_")[-1]

    return synonyms

def get_mba_labels_map():
    g = get_mba_ontology()

    labels = {}
    for s, p, o in g:
        if str(s).startswith("https://purl.brain-bican.org/ontology/mbao/MBA_") and p == RDFS.label:
            labels["MBA:" + str(s).split("_")[-1]] = str(o).strip().lower()

    return labels

mba_ontology = None

def get_mba_ontology():
    global mba_ontology
    if not mba_ontology:
        mba_ontology = Graph()
        mba_ontology.parse('https://purl.brain-bican.org/ontology/mbao/mbao.owl', format="xml")
    return mba_ontology

def read_gene_dbs(folder_path: str):
    """
    Reads all TSV files in the templates folder and creates a dictionary of genes
    where the key is the NAME column and the value is the ID column.
    Args:
        folder_path: Path to the folder containing gene TSV files.
    Returns:
        dict: Dictionary with gene NAME as keys and ID as values.

    """
    gene_dict = {}

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.tsv') and not file_name.startswith("CS") and not file_name.startswith("CCN"):
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(file_path, sep='\t')
            for _, row in df.iterrows():
                if pd.notna(row['ID']):
                    gene_dict[row['NAME'].replace("(Mmus)", "").strip()] = row['ID']

    return gene_dict

def find_duplicate_cell_labels(nodes):
    seen_labels = set()
    duplicates = []

    for node in nodes:
        label = node.get('cell_label')
        if label in seen_labels:
            duplicates.append(label)
        else:
            seen_labels.add(label)

    return duplicates

def get_excluded_classes(taxonomy_id):
    """
    Reads the class curation TSV file for the given taxonomy_id and returns a list of
    class urls where Exclude_from_ontology equals True (case insensitive).

    Args:
        taxonomy_id: Taxonomy identifier (string)

    Returns:
        List of defined_class values for rows with Exclude_from_ontology set to True.
    """
    excluded = []
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                 f"../patterns/data/default/{taxonomy_id}_class_curation.tsv")
    with open(file_path, newline='') as fd:
        reader = csv.DictReader(fd, delimiter='\t')
        for row in reader:
            if row.get("Exclude_from_ontology", "") and row.get("Exclude_from_ontology", "").strip().lower() == "true":
                excluded.append(row.get("defined_class", "").strip())
    return excluded

def read_abc_urls(file_path):
    """
    Reads the ABC URLs from a json file and returns them as a dictionary.
    Args:
        file_path: Path to the json file containing ABC URLs.
    Returns:
        dict: Dictionary with ABC URLs.
    """
    data_dict = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data_dict = json.load(file)
    return data_dict

def get_cl_subset_nodes(nodes_to_collapse):
    """
    Reads the CL curation TSV file for the given taxonomy_id and returns a list of
    accession IDs where Add_toCL equals True (case insensitive).

    Args:
        nodes_to_collapse: Dictionary of nodes to collapse, where keys are cell_set_accession.
    Returns:
        List of accession IDs for the nodes to be added to CL.
    """
    cl_subset = []
    with open(CL_SUBSET_TABLE, newline='') as fd:
        reader = csv.DictReader(fd, delimiter='\t')
        for row in reader:
            if row.get("Add_to_CL", "") and row.get("Add_to_CL", "").strip().lower() == "true":
                cl_subset.append(row.get("cell_set_accession", "").strip())

    # extend these with the compressed nodes
    to_extend = []
    for cl_candidate in cl_subset:
        if cl_candidate in nodes_to_collapse:
            to_extend.append(nodes_to_collapse[cl_candidate]['cell_set_accession'])
    cl_subset.extend(to_extend)
    return cl_subset

