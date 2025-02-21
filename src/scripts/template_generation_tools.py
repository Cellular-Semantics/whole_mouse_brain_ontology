import pandas as pd
import json
import os
import logging
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDFS

from dendrogram_tools import cas_json_2_nodes_n_edges, read_json_file
from template_generation_utils import get_synonyms_from_taxonomy, read_taxonomy_config, \
    get_subtrees, generate_dendrogram_tree, read_taxonomy_details_yaml, read_csv_to_dict,\
    read_csv, read_gene_data, read_markers, get_gross_cell_type, merge_tables, read_allen_descriptions, \
    extract_taxonomy_name_from_path, get_collapsed_nodes
from nomenclature_tools import nomenclature_2_nodes_n_edges
from pcl_id_factory import PCLIdFactory
from marker_tools import get_nsforest_confidences


log = logging.getLogger(__name__)


PCL_BASE = 'http://purl.obolibrary.org/obo/PCL_'
PCL_INDV_BASE = 'http://purl.obolibrary.org/obo/pcl/'
BICAN_INDV_BASE = 'https://purl.brain-bican.org/taxonomy/CCN20230722/'

PCL_PREFIX = 'PCL:'

TEMPLATES_FOLDER_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../templates/")
MARKER_PATH = '../markers/CS{}_markers.tsv'
ALLEN_MARKER_PATH = "../markers/CS{}_Allen_markers.tsv"
NOMENCLATURE_TABLE_PATH = '../dendrograms/nomenclature_table_{}.csv'
ENSEMBLE_PATH = os.path.join(TEMPLATES_FOLDER_PATH, "{}.tsv")

CLUSTER_ANNOTATIONS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                        '../dendrograms/supplementary/version2/cluster_annotation_CCN20230722.csv')
NT_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/version2/neurotransmitters.tsv")
NT_SYMBOLS_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/version2/Neurotransmitter_symbols_mapping.tsv")
BRAIN_REGION_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/Brain_region_mapping.tsv")

CROSS_SPECIES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  "../dendrograms/nomenclature_table_CCN202002270.csv")
MBA_ONTOLOGY = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  "../ontology/mirror/mba.owl")

# centralized data files
ALLEN_DESCRIPTIONS_PATH = "{}/{}/All Descriptions_{}.json"
DATASET_INFO_CSV = "{}/{}/{}_landingpage_dataset_info.csv"
TAXONOMY_INFO_CSV = "{}/{}/{}_Taxonomy_Info_Panel.csv"
NSFOREST_MARKER_CSV = "{}/NSForestMarkers/{}_{}_NSForest_Markers.csv"

EXPRESSION_SEPARATOR = "|"

ACRONYM_REGION = "CCF acronym region"
BROAD_REGION = "CCF broad region"


def generate_ind_template(taxonomy_file_path, output_filepath):
    # path_parts = taxonomy_file_path.split(os.path.sep)
    # taxon = path_parts[len(path_parts) - 1].split(".")[0]

    dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
    all_nodes = {node['cell_set_accession']: node for node in dend['nodes']}
    id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))
    dend_tree = generate_dendrogram_tree(dend)
    nodes_to_collapse = get_collapsed_nodes(dend_tree, all_nodes)

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
                           'Rank': "A 'cell_type_rank' SPLIT=|"
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
        if o['cell_set_accession'] in nodes_to_collapse:
            d['Exemplar_of'] = PCL_BASE + id_factory.get_class_id(nodes_to_collapse[o['cell_set_accession']]['cell_set_accession'])
        else:
            d['Exemplar_of'] = PCL_BASE + id_factory.get_class_id(o['cell_set_accession'])

        dl.append(d)
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_base_class_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
        all_nodes = {node['cell_set_accession']: node for node in dend['nodes']}
        id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))
        dend_tree = generate_dendrogram_tree(dend)
        nodes_to_collapse = get_collapsed_nodes(dend_tree, all_nodes)
        # subtrees = get_subtrees(dend_tree, taxonomy_config)

        duplicate_labels = find_duplicate_cell_labels(dend['nodes'])

        gene_db = read_gene_dbs(TEMPLATES_FOLDER_PATH)
        gene_names = dict()
        if "Reference_gene_list" in taxonomy_config:
            gene_db_path = ENSEMBLE_PATH.format(str(taxonomy_config["Reference_gene_list"][0]).strip().lower())
            gene_names = read_gene_data(gene_db_path)
            minimal_markers = read_markers(MARKER_PATH.format(taxon.replace("CCN", "").replace("CS", "")), gene_names)
            allen_markers = read_markers(ALLEN_MARKER_PATH.format(taxon.replace("CCN", "").replace("CS", "")), gene_names)
        else:
            minimal_markers = {}
            allen_markers = {}

        cluster_annotations = read_csv_to_dict(CLUSTER_ANNOTATIONS_PATH, id_column_name="cell_set_accession.cluster")[1]
        neurotransmitters = read_csv_to_dict(NT_MAPPING, delimiter="\t")[1]
        nt_symbols_mapping = read_csv_to_dict(NT_SYMBOLS_MAPPING, delimiter="\t")[1]
        brain_region_mapping = read_csv_to_dict(BRAIN_REGION_MAPPING, delimiter="\t")[1]
        mba_symbols = get_mba_symbols_map()
        mba_labels = get_mba_labels_map()

        class_seed = ['defined_class',
                      'prefLabel',
                      'Alias_citations',
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
                      'NT',
                      'NT_label',
                      'NT_markers'
                      'CL',
                      'Nomenclature_Layers',
                      'Nomenclature_Projection',
                      'marker_gene_set',
                      'MBA',
                      'MBA_text'
                      ]
        class_template = []
        obsolete_template = []
        processed_accessions = set()
        for o in dend['nodes']:
            node = o
            if o['cell_set_accession'] in nodes_to_collapse:
                node = nodes_to_collapse[o['cell_set_accession']]
                collapsed = True
            else:
                collapsed = False
            if node.get('cell_set_accession') and node['cell_set_accession'] not in processed_accessions:
                d = dict()
                d['defined_class'] = PCL_BASE + id_factory.get_class_id(node['cell_set_accession'])
                if node['cell_label'] in duplicate_labels:
                    d['prefLabel'] = node['cell_label'] + " (" + node['labelset'] + ")"
                else:
                    d['prefLabel'] = node['cell_label']
                # if o.get('cell_fullname'):
                #     d['prefLabel'] = o['cell_fullname']
                d['Synonyms_from_taxonomy'] = "|".join(sorted(node.get("synonyms", [])))
                d['Gross_cell_type'] = get_gross_cell_type(node['cell_set_accession'], dend['nodes'])
                d['Taxon'] = taxonomy_config['Species'][0]
                d['Taxon_abbv'] = taxonomy_config['Gene_abbv'][0]
                d['Brain_region'] = taxonomy_config['Brain_region'][0]
                cluster_id = node['cell_set_accession']
                if collapsed:
                    cluster_id = "|".join(node["chain"])
                d['Cluster_IDs'] = cluster_id
                d['Labelset'] = node['labelset']
                d['Dataset_url'] = "https://purl.brain-bican.org/taxonomy/CCN20230722"
                if 'rationale_dois' in node and node['rationale_dois']:
                    alias_citations = [citation.strip() for citation in node['rationale_dois']
                                       if citation and citation.strip()]
                    d["Alias_citations"] = "|".join(alias_citations)
                else:
                    d["Alias_citations"] = ""

                markers_str = node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo", "")
                markers_list = [marker.strip() for marker in markers_str.split(",") if marker.strip()]
                d['Minimal_markers'] = "|".join([get_gene_id(gene_db, marker) for marker in markers_list if str(marker).lower() != "none"])

                # Allen markers are not used, legacy code
                # if o['cell_set_accession'] in allen_markers:
                #     d['Allen_markers'] = allen_markers[o['cell_set_accession']]
                # else:
                #     if str(o["author_annotation_fields"].get(f"{o['labelset']}.markers.combo", "")).lower() != "none":
                #         d['Allen_markers'] = o["author_annotation_fields"].get(f"{o['labelset']}.markers.combo", "")
                #     else:
                d['Allen_markers'] = ""
                if 'Brain_region_abbv' in taxonomy_config:
                    d['Brain_region_abbv'] = taxonomy_config['Brain_region_abbv'][0]
                if 'Species_abbv' in taxonomy_config:
                    d['Species_abbv'] = taxonomy_config['Species_abbv'][0]
                individuals = BICAN_INDV_BASE + node['cell_set_accession']
                if collapsed:
                    individuals = "|".join([BICAN_INDV_BASE + indv_id for indv_id in node["chain"]])
                d['Individuals'] = individuals

                # for index, subtree in enumerate(subtrees):
                #     if o['cell_set_accession'] in subtree:
                #         location_rel = taxonomy_config['Root_nodes'][index]['Location_relation']
                #         if location_rel == "part_of":
                #             d['part_of'] = taxonomy_config['Brain_region'][0]
                #             d['has_soma_location'] = ''
                #         elif location_rel == "has_soma_location":
                #             d['part_of'] = ''
                #             d['has_soma_location'] = taxonomy_config['Brain_region'][0]

                # TODO check this
                d['part_of'] = ''
                d['has_soma_location'] = taxonomy_config['Brain_region'][0]

                d['aligned_alias'] = ""
                if node.get('marker_gene_evidence'):
                    d['marker_gene_set'] = PCL_PREFIX + id_factory.get_marker_gene_set_id(node['cell_set_accession'])
                elif  ("author_annotation_fields" in node and
                       node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo") and
                       str(node["author_annotation_fields"].get(f"{node['labelset']}.markers.combo", "")).lower() != "none"):
                    d['marker_gene_set'] = PCL_PREFIX + id_factory.get_marker_gene_set_id(
                        node['cell_set_accession'])
                else:
                    d['marker_gene_set'] = ""
                if "cell_ontology_term_id" in node and node["cell_ontology_term_id"]:
                    d['CL'] = node["cell_ontology_term_id"]
                else:
                    d['CL'] = ""
                # if "layer" in o and o["layer"]:
                #     d['Nomenclature_Layers'] = o["layer"]
                # else:
                #     d['Nomenclature_Layers'] = ""
                # if "projection" in o and o["projection"]:
                #     d['Nomenclature_Projection'] = o["projection"]
                # else:
                #     d['Nomenclature_Projection'] = ""

                # CS202212150_1 -> 1
                # cluster_index = str(o['cell_set_accession']).replace(taxon + "_", "")
                d['NT'] = ""
                d['NT_markers'] = ""
                if node['cell_set_accession'] in neurotransmitters:
                    nt_symbol = neurotransmitters[node['cell_set_accession']]["neurotransmitter_label"]
                    # TODO add evidence comment "inferred to be {x}-ergic based on expression of {y}"
                    if nt_symbol in nt_symbols_mapping:
                        d['NT'] = nt_symbols_mapping.get(nt_symbol)["CELL TYPE NEUROTRANSMISSION ID"]
                        d['NT_label'] = " and ".join(nt_symbols_mapping.get(nt_symbol)["CELL TYPE LABEL"].split("|"))
                if node['cell_set_accession'] in cluster_annotations:
                    nt_markers = cluster_annotations[node['cell_set_accession']]["nt.markers"]
                    d['NT_markers'] = "|".join([entry.split(':')[0] for entry in nt_markers.split(",") if entry])

                missed_regions = set()
                if node['cell_set_accession'] in cluster_annotations:
                    ccf_broad_freq = cluster_annotations[node['cell_set_accession']]["CCF_broad.freq"]
                    ccf_acronym_freq = cluster_annotations[node['cell_set_accession']]["CCF_acronym.freq"]

                    index = 1
                    index = populate_mba_relations(ccf_broad_freq, BROAD_REGION, d, index, mba_symbols, mba_labels, missed_regions)
                    populate_mba_relations(ccf_acronym_freq, ACRONYM_REGION, d, index, mba_symbols, mba_labels, missed_regions)

                d['MBA_assay'] = "EFO:0008992"
                for missed_region in missed_regions:
                    print("MBA symbol not found for region: ", missed_region)

                # if o['cell_set_accession'] in brain_region_mapping:
                #     d['MBA'] = brain_region_mapping[o['cell_set_accession']]["TENTATIVE_MBA_ID"].replace("http://purl.obolibrary.org/obo/MBA_", "MBA:")
                #     index = 1
                #
                #     if brain_region_mapping[o['cell_set_accession']]["TENTATIVE_MBA_ID"]:
                #         tentative_regions = brain_region_mapping[o['cell_set_accession']]["TENTATIVE_MBA_ID"].split("|")
                #         for tentative_region in tentative_regions:
                #             d['MBA_' + str(index)] = tentative_region.replace("http://purl.obolibrary.org/obo/MBA_", "MBA:")
                #             d['MBA_' + str(index) + '_comment'] = "Location assignment based on tentative anatomical annotations."
                #             index += 1
                #
                #     if brain_region_mapping[o['cell_set_accession']]["MAX_DISSECTION_MBA_ID"]:
                #         max_dissection_regions = brain_region_mapping[o['cell_set_accession']]["MAX_DISSECTION_MBA_ID"].split("|")
                #         for max_dissection_region in max_dissection_regions:
                #             d['MBA_' + str(index)] = max_dissection_region.replace("http://purl.obolibrary.org/obo/MBA_", "MBA:")
                #             d['MBA_' + str(index) + '_comment'] = "Location assignment based on max dissection region."
                #             index += 1

                for k in class_seed:
                    if not (k in d.keys()):
                        d[k] = ''
                class_template.append(d)
                processed_accessions.add(node['cell_set_accession'])
            else:
                # process obsoleted classes due to chain compressing
                if collapsed and o.get('cell_set_accession') not in processed_accessions:
                    d = dict()
                    d['defined_class'] = PCL_BASE + id_factory.get_class_id(o['cell_set_accession'])
                    d['prefLabel'] = "obsolete " + o['cell_label']
                    d['Comment'] = "This class is obsoleted due to chain compression."
                    d['Deprecated'] = "true"
                    d['Gross_cell_type'] = get_gross_cell_type(o['cell_set_accession'],
                                                               dend['nodes'])
                    d['Taxon'] = taxonomy_config['Species'][0]
                    d['Taxon_abbv'] = taxonomy_config['Gene_abbv'][0]
                    d['Comment'] = "This term is obsoleted due to identical cell set chain compression."
                    d['Classification'] = "CL:0000000"
                    obsolete_template.append(d)

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)
        if obsolete_template:
            obsolete_filepath = output_filepath.replace("_base.tsv", "_obsolete.tsv")
            class_obsolete_template = pd.DataFrame.from_records(obsolete_template)
            class_obsolete_template.to_csv(obsolete_filepath, sep="\t", index=False)


def populate_mba_relations(ccf_broad_freq, approach, d, index, mba_symbols, mba_labels, missed_regions):
    regions = [{"region": item.split(":")[0].strip(),
                "percentage": float(item.split(":")[1].strip()) if ":" in item else 0}
               for item in ccf_broad_freq.split(",")]
    mbas = set()
    mba_text = set()
    for region in regions:
        if region["percentage"] >= 0.05 and region["region"] != "NA":
            if region["region"] in mba_symbols:
                d['MBA_' + str(index)] = mba_symbols[region["region"]]
                d['MBA_' + str(index) + '_cell_percentage'] = region["percentage"]
                # d['MBA_' + str(index) + '_assay'] = "EFO:0008992"
                d['MBA_' + str(
                    index) + '_comment'] = "Location assignment based on {}.".format(approach)
                mbas.add(mba_symbols[region["region"]])
                # {fullname} ({symbol}, {fraction of cells})}
                mba_text.add(mba_labels[d['MBA_' + str(index)]] + " (" + region["region"] + ", " + str(region["percentage"]) + ")")
                index += 1
            else:
                missed_regions.add(region["region"])
    if approach == BROAD_REGION:
        d['MBA'] = "|".join(mbas)
        d['MBA_text'] = ", ".join(mba_text)
    elif approach == ACRONYM_REGION:
        d['CCF_acronym_freq'] = "|".join(mbas)
    return index


def generate_curated_class_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
        all_nodes = {node['cell_set_accession']: node for node in dend['nodes']}
        id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))
        dend_tree = generate_dendrogram_tree(dend)
        nodes_to_collapse = get_collapsed_nodes(dend_tree, all_nodes)

        # subtrees = get_subtrees(dend_tree, taxonomy_config)

        class_curation_seed = ['defined_class',
                               'Curated_synonyms',
                               'Classification',
                               'Classification_comment',
                               'Classification_pub',
                               'Expresses',
                               'Expresses_comment',
                               'Expresses_pub',
                               'Projection_type',
                               'Layers',
                               'Cross_species_text',
                               'Comment'
                               ]
        class_template = []
        processed_accessions = set()
        for o in dend['nodes']:
            node = o
            if o['cell_set_accession'] in nodes_to_collapse:
                node = nodes_to_collapse[o['cell_set_accession']]
                collapsed = True
            else:
                collapsed = False
            if node.get('cell_set_accession') and node['cell_set_accession'] not in processed_accessions:
                d = dict()
                d['defined_class'] = PCL_BASE + id_factory.get_class_id(node['cell_set_accession'])
                if node.get('cell_fullname'):
                    d['prefLabel'] = node['cell_fullname']

                for k in class_curation_seed:
                    if not (k in d.keys()):
                        d[k] = ''
                class_template.append(d)
                processed_accessions.add(node['cell_set_accession'])

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_homologous_to_template(taxonomy_file_path, all_base_files, output_filepath):
    """
    Homologous_to relations require a separate template. If this operation is driven by the nomenclature tables,
    some dangling classes may be generated due to root classes that don't have a class and should not be aligned.
    So, instead of nomenclature tables, base files are used for populating homologous to relations. This ensures all
    alignments has a corresponding class.
    Args:
        taxonomy_file_path: path of the taxonomy file
        all_base_files: paths of the all class template base files
        output_filepath: template output file path
    """
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    other_taxonomy_aliases = index_base_files([t for t in all_base_files if taxon not in t])

    if taxonomy_config:
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
        id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))

        dend_tree = generate_dendrogram_tree(dend)
        subtrees = get_subtrees(dend_tree, taxonomy_config)

        data_template = []

        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees) and (o['cell_set_preferred_alias'] or
                                                                    o['cell_set_additional_aliases']):
                d = dict()
                d['defined_class'] = PCL_BASE + id_factory.get_class_id(o['cell_set_accession'])
                homologous_to = list()
                for other_aliases in other_taxonomy_aliases:
                    if "cell_set_aligned_alias" in o and o["cell_set_aligned_alias"] \
                            and str(o["cell_set_aligned_alias"]).lower() in other_aliases:
                        homologous_to.append(other_aliases[str(o["cell_set_aligned_alias"])
                                             .lower()]["defined_class"])
                d['homologous_to'] = "|".join(homologous_to)

                data_template.append(d)

        robot_template = pd.DataFrame.from_records(data_template)
        robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_non_taxonomy_classification_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))

    cell_set_accession = 3
    child_cell_set_accessions = 14
    nomenclature_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     NOMENCLATURE_TABLE_PATH.format(taxon))

    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config and os.path.exists(nomenclature_path):
        nomenclature_records = read_csv(nomenclature_path, id_column=cell_set_accession)
        nomenclature_template = []

        non_taxo_roots = {}
        for root in taxonomy_config['non_taxonomy_roots']:
            non_taxo_roots[root["Node"]] = root["Cell_type"]

        for record in nomenclature_records:
            columns = nomenclature_records[record]
            if columns[cell_set_accession] in non_taxo_roots:
                # dendrogram is not mandatory for human & marmoset
                # if columns[cell_set_accession] in dend_nodes:
                #     raise Exception("Node {} exists both in dendrogram and nomenclature of the taxonomy: {}."
                #                     .format(columns[cell_set_accession], taxon))
                children = columns[child_cell_set_accessions].split("|")
                for child in children:
                    # child of root with cell_set_preferred_alias
                    if child not in non_taxo_roots and nomenclature_records[child][0]:
                        d = dict()
                        d['defined_class'] = PCL_BASE + id_factory.get_class_id(child)
                        d['Classification'] = non_taxo_roots[columns[cell_set_accession]]
                        nomenclature_template.append(d)

        class_robot_template = pd.DataFrame.from_records(nomenclature_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_cross_species_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
        id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))

        dend_tree = generate_dendrogram_tree(dend)
        subtrees = get_subtrees(dend_tree, taxonomy_config)
        cross_species_template = []

        headers, cs_by_preferred_alias = read_csv_to_dict(CROSS_SPECIES_PATH,
                                                          id_column_name="cell_set_preferred_alias", id_to_lower=True)
        headers, cs_by_aligned_alias = read_csv_to_dict(CROSS_SPECIES_PATH,
                                                        id_column_name="cell_set_aligned_alias", id_to_lower=True)

        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees) and (o['cell_set_preferred_alias'] or
                                                                    o['cell_set_additional_aliases']):
                cross_species_classes = set()
                if o["cell_set_aligned_alias"] and str(o["cell_set_aligned_alias"]).lower() in cs_by_aligned_alias:
                    cross_species_classes.add(PCL_BASE + id_factory.get_class_id(cs_by_aligned_alias[str(o["cell_set_aligned_alias"])
                                              .lower()]["cell_set_accession"]))

                if "cell_set_additional_aliases" in o and o["cell_set_additional_aliases"]:
                    additional_aliases = str(o["cell_set_additional_aliases"]).lower().split(EXPRESSION_SEPARATOR)
                    for additional_alias in additional_aliases:
                        if additional_alias in cs_by_preferred_alias:
                            cross_species_classes.add(PCL_BASE + id_factory.get_class_id(
                                                      cs_by_preferred_alias[additional_alias]["cell_set_accession"]))

                if len(cross_species_classes):
                    d = dict()
                    d['defined_class'] = PCL_BASE + id_factory.get_class_id(o['cell_set_accession'])
                    d['cross_species_classes'] = EXPRESSION_SEPARATOR.join(cross_species_classes)

                    cross_species_template.append(d)

        class_robot_template = pd.DataFrame.from_records(cross_species_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_taxonomies_template(centralized_data_folder, output_filepath):
    taxon_configs = read_taxonomy_details_yaml()

    robot_template_seed = {'ID': 'ID',
                           'TYPE': 'TYPE',
                           'Entity Type': 'TI %',
                           'Label': 'LABEL',
                           'Number of Cell Types': "A 'cell_types_count'",
                           'Number of Cell Subclasses': "A 'cell_subclasses_count'",
                           'Number of Cell Classes': "A 'cell_classes_count'",
                           'Anatomic Region': "A 'has_brain_region'",
                           'Species Label': "A skos:prefLabel",
                           'Age': "A 'has_age'",
                           'Sex': "A 'has_sex'",
                           'Primary Citation': "A oboInOwl:hasDbXref",
                           'Title': "A dcterms:title",
                           'Description': "A rdfs:comment",
                           'Attribution': "A dcterms:provenance",
                           'SubDescription': "A dcterms:description",
                           'Anatomy': "A dcterms:subject",
                           'Anatomy_image': "A dcterms:relation"
                           }
    dl = [robot_template_seed]

    for taxon_config in taxon_configs:
        d = dict()
        d['ID'] = 'BICAN:' + taxon_config["Taxonomy_id"]
        d['TYPE'] = 'owl:NamedIndividual'
        d['Entity Type'] = 'PCL:0010002'  # Taxonomy
        d['Label'] = taxon_config["Taxonomy_id"]
        d['Anatomic Region'] = taxon_config['Brain_region'][0]
        d['Primary Citation'] = taxon_config['PMID'][0]

        add_taxonomy_info_panel_properties(centralized_data_folder, d, taxon_config)

        dl.append(d)
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def add_taxonomy_info_panel_properties(centralized_data_folder, d, taxon_config):
    expected_folder_name = get_centralized_taxonomy_folder(taxon_config)
    taxonomy_metadata_path = TAXONOMY_INFO_CSV.format(centralized_data_folder, expected_folder_name,
                                                      taxon_config["Taxonomy_id"])
    print(taxonomy_metadata_path)
    if os.path.isfile(taxonomy_metadata_path):
        headers, taxonomies_metadata = read_csv_to_dict(taxonomy_metadata_path)
        taxonomy_metadata = taxonomies_metadata[taxon_config["Taxonomy_id"]]
        d['Number of Cell Types'] = taxonomy_metadata["Cell Types"]
        d['Number of Cell Subclasses'] = taxonomy_metadata["Cell Subclasses"]
        d['Number of Cell Classes'] = taxonomy_metadata["Cell Classes"]
        d['Species Label'] = taxonomy_metadata["Species"]
        d['Age'] = taxonomy_metadata["Age"]
        d['Sex'] = taxonomy_metadata["Sex"]
        d['Title'] = taxonomy_metadata["header"]
        d['Description'] = taxonomy_metadata["mainDescription"]
        d['Attribution'] = taxonomy_metadata["attribution"]
        d['SubDescription'] = taxonomy_metadata["subDescription"]
        d['Anatomy'] = taxonomy_metadata["Anatomy"]
        if "Anatomy_image" in taxonomy_metadata:
            d['Anatomy_image'] = taxonomy_metadata["Anatomy_image"]
    else:
        raise ValueError("Couldn't find taxonomy '{}' landingpage dataset info file at: '{}'"
                         .format(taxon_config["Taxonomy_id"], taxonomy_metadata_path))


# def generate_datasets_template(centralized_data_folder, output_filepath):
#     path_parts = output_filepath.split(os.path.sep)
#     taxonomy_id = str(path_parts[len(path_parts) - 1]).split("_")[0]
#     taxonomy_config = read_taxonomy_config(taxonomy_id)
#
#     expected_file_name = DATASET_INFO_CSV.format(centralized_data_folder,
#                                                  get_centralized_taxonomy_folder(taxonomy_config), taxonomy_id)
#
#     if os.path.isfile(expected_file_name):
#         headers, dataset_metadata = read_csv_to_dict(expected_file_name, generated_ids=True)
#
#         robot_template_seed = {'ID': 'ID',
#                                'TYPE': 'TYPE',
#                                'Entity Type': 'TI %',
#                                'Label': 'LABEL',
#                                'PrefLabel': 'A skos:prefLabel',
#                                'Symbol': 'A IAO:0000028',
#                                'Taxonomy': 'AI schema:includedInDataCatalog',
#                                'Cell Count': "AT 'cell_count'^^xsd:integer",
#                                'Nuclei Count': "AT 'nuclei_count'^^xsd:integer",
#                                'Dataset': "A schema:headline",
#                                'Species': "A schema:assesses",
#                                'Region': "A schema:position",
#                                'Description': "A rdfs:comment",
#                                'Download Link': "A schema:archivedAt",
#                                'Explore Link': "A schema:discussionUrl"
#                                }
#         dl = [robot_template_seed]
#
#         dataset_index = 0
#         for dataset in dataset_metadata:
#             d = dict()
#             d['ID'] = 'PCL:' + get_dataset_id(taxonomy_id, dataset_index)
#             d['TYPE'] = 'owl:NamedIndividual'
#             d['Entity Type'] = 'schema:Dataset'  # Taxonomy
#             d['Label'] = dataset_metadata[dataset]['Ontology Name']
#             d['PrefLabel'] = dataset_metadata[dataset]['Dataset']
#             d['Symbol'] = dataset_metadata[dataset]['Ontology Symbol']
#             d['Taxonomy'] = 'PCL_INDV:' + taxonomy_id
#             cells_nuclei = dataset_metadata[dataset]['cells/nuclei']
#             if 'nuclei' in cells_nuclei:
#                 d['Nuclei Count'] = int(''.join(c for c in cells_nuclei if c.isdigit()))
#             elif 'cells' in cells_nuclei:
#                 d['Cell Count'] = int(''.join(c for c in cells_nuclei if c.isdigit()))
#             d['Dataset'] = dataset_metadata[dataset]['dataset_number']
#             d['Species'] = dataset_metadata[dataset]['species']
#             d['Region'] = dataset_metadata[dataset]['region']
#             d['Description'] = dataset_metadata[dataset]['text']
#             d['Download Link'] = dataset_metadata[dataset]['download_link']
#             d['Explore Link'] = dataset_metadata[dataset]['explore_link']
#
#             dataset_index += 1
#             dl.append(d)
#         robot_template = pd.DataFrame.from_records(dl)
#         robot_template.to_csv(output_filepath, sep="\t", index=False)
#     else:
#         raise ValueError("Couldn't find taxonomy '{}' landingpage dataset info file at: '{}'"
#                          .format(taxonomy_id, expected_file_name))


def generate_marker_gene_set_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
        id_factory = PCLIdFactory(read_json_file(taxonomy_file_path))

        duplicate_labels = find_duplicate_cell_labels(dend['nodes'])

        # dend_tree = generate_dendrogram_tree(dend)
        # subtrees = get_subtrees(dend_tree, taxonomy_config)

        # if "Reference_gene_list" in taxonomy_config:
        #     gene_db_path = ENSEMBLE_PATH.format(str(taxonomy_config["Reference_gene_list"][0]).strip().lower())
        #     gene_names = read_gene_data(gene_db_path)
        #     minimal_markers = read_markers(MARKER_PATH.format(taxon.replace("CCN", "").replace("CS", "")), gene_names)
        # else:
        #     minimal_markers = {}
        #
        # ns_forest_marker_file = NSFOREST_MARKER_CSV.format(centralized_data_folder,
        #                                                    taxonomy_config['Species_abbv'][0],
        #                                                    taxonomy_config['Brain_region_abbv'][0])
        # confidences = get_nsforest_confidences(taxon, dend, ns_forest_marker_file)

        gene_db = read_gene_dbs(TEMPLATES_FOLDER_PATH)

        class_seed = ['defined_class',
                      'Marker_set_of',
                      'Minimal_markers',
                      'Minimal_markers_label',
                      'Species_abbv',
                      'Brain_region',
                      'Parent',
                      'FBeta_confidence_score'
                      ]
        class_template = []

        for o in dend['nodes']:
            if o['cell_set_accession'] :
                if ("author_annotation_fields" in o and
                        o["author_annotation_fields"].get(f"{o['labelset']}.markers.combo", "") and
                        str(o["author_annotation_fields"].get(f"{o['labelset']}.markers.combo", "")).lower() != "none"):
                    d = dict()
                    d['defined_class'] = PCL_BASE + id_factory.get_marker_gene_set_id(o['cell_set_accession'])
                    if o['cell_label'] in duplicate_labels:
                        d['Marker_set_of'] = o['cell_label'] + " (" + o['labelset'] + ")"
                    else:
                        d['Marker_set_of'] = o['cell_label']
                    markers_str = o["author_annotation_fields"].get(f"{o['labelset']}.markers.combo", "")
                    markers_list = [marker.strip() for marker in markers_str.split(",")]
                    d['Minimal_markers'] = "|".join([get_gene_id(gene_db, marker) for marker in markers_list if str(marker).lower() != "none"])
                    d['Minimal_markers_label'] = o["author_annotation_fields"].get(f"{o['labelset']}.markers.combo", "")
                    if 'Species_abbv' in taxonomy_config:
                        d['Species_abbv'] = taxonomy_config['Species_abbv'][0]
                    d['Brain_region'] = taxonomy_config['Brain_region'][0]
                    d['Parent'] = "SO:0001260"  # sequence collection
                    # if o['cell_set_accession'] in confidences:
                    #     d['FBeta_confidence_score'] = confidences[o['cell_set_accession']]

                    for k in class_seed:
                        if not (k in d.keys()):
                            d[k] = ''
                    class_template.append(d)

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_app_specific_template(taxonomy_file_path, output_filepath):
    if str(taxonomy_file_path).endswith(".json"):
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
    else:
        dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)

    robot_template_seed = {'ID': 'ID',
                           'TYPE': 'TYPE',
                           'cell_set_color': "A ALLENHELP:cell_set_color"
                           }
    dl = [robot_template_seed]

    for o in dend['nodes']:
        if "cell_set_color" in o and o["cell_set_color"]:
            d = dict()
            d['ID'] = 'BICAN_INDV:' + o['cell_set_accession']
            d['TYPE'] = 'owl:NamedIndividual'
            d['cell_set_color'] = str(o["cell_set_color"]).strip()
            dl.append(d)

    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


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
    if str(gene_name) in gene_db:
        return gene_db[str(gene_name)]
    else:
        # gene_db may have styling issues, so workaround
        # TODO remove this workaround after fixing the gene_db
        for gene in gene_db:
            if gene_name.lower() in gene.lower():
                return gene_db[gene]
    raise Exception(f"Gene ID not found for gene: {gene_name}")

def get_mba_symbols_map():
    OBOINOWL = Namespace("http://www.geneontology.org/formats/oboInOwl#")

    g = Graph()
    g.parse(MBA_ONTOLOGY, format="xml")

    synonyms = {}
    for s, p, o in g:
        if str(s).startswith("https://purl.brain-bican.org/ontology/mbao/MBA_") and p == OBOINOWL.hasExactSynonym:
            synonyms[str(o).strip()] = "MBA:" + str(s).split("_")[-1]

    return synonyms

def get_mba_labels_map():
    g = Graph()
    g.parse(MBA_ONTOLOGY, format="xml")

    labels = {}
    for s, p, o in g:
        if str(s).startswith("https://purl.brain-bican.org/ontology/mbao/MBA_") and p == RDFS.label:
            labels["MBA:" + str(s).split("_")[-1]] = str(o).strip().lower()

    return labels

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

