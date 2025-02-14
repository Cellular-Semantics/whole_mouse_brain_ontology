import unittest
import os
import csv
import requests
from cProfile import label

from dendrogram_tools import cas_json_2_nodes_n_edges, read_json_file
from nomenclature_tools import nomenclature_2_nodes_n_edges
from template_generation_utils import get_synonyms_from_taxonomy, get_synonym_pairs, \
    PAIR_SEPARATOR, OR_SEPARATOR, read_taxonomy_config, get_subtrees, read_dendrogram_tree, \
    find_singleton_chains, generate_dendrogram_tree

PATH_DENDROGRAM_JSON = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/CCN202002013.json")
PATH_NOMENCLATURE_CSV = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     "./test_data/nomenclature_table_CCN201912131.csv")
PATH_NOMENCLATURE_CSV_MOUSE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           "./test_data/nomenclature_table_CCN202002013.csv")

PATH_MOUSE_CAS = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           "../src/dendrograms/CCN20230722.json")
PATH_MOUSE_REPORT_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           "./test_data/one_concept_one_name.tsv")


class TemplateUtilsTest(unittest.TestCase):

    def test_get_synonyms_from_taxonomy(self):
        tree = nomenclature_2_nodes_n_edges(PATH_NOMENCLATURE_CSV_MOUSE)
        nodes = tree['nodes']

        node8_synonyms = get_synonyms_from_taxonomy(nodes[8]).split(OR_SEPARATOR)
        node8_synonyms = list(filter(None, node8_synonyms))
        self.assertEqual("CS202002013_125", nodes[8]["cell_set_accession"])
        self.assertEqual(1, len(node8_synonyms))
        self.assertTrue("Lamp5" in node8_synonyms)

        node20_synonyms = get_synonyms_from_taxonomy(nodes[20]).split(OR_SEPARATOR)
        node20_synonyms = list(filter(None, node20_synonyms))
        self.assertEqual("CS202002013_6", nodes[20]["cell_set_accession"])
        self.assertEqual(1, len(node20_synonyms))
        self.assertTrue("Lamp5 Pdlim5_2" in node20_synonyms)

        node50_synonyms = get_synonyms_from_taxonomy(nodes[50]).split(OR_SEPARATOR)
        node50_synonyms = list(filter(None, node50_synonyms))
        self.assertEqual("CS202002013_146", nodes[50]["cell_set_accession"])
        self.assertEqual(0, len(node50_synonyms))

    def test_get_synonym_pairs(self):
        tree = nomenclature_2_nodes_n_edges(PATH_NOMENCLATURE_CSV_MOUSE)
        nodes = tree['nodes']

        node3_pairs = get_synonym_pairs(nodes[3]).split(PAIR_SEPARATOR)
        self.assertEqual("CS202002013_120", nodes[3]["cell_set_accession"])
        self.assertEqual(5, len(node3_pairs))
        self.assertTrue("cell_set_preferred_alias:''" in node3_pairs)
        self.assertTrue("original_label:n4" in node3_pairs)
        self.assertTrue("cell_set_label:RNAseq 001-091" in node3_pairs)
        self.assertTrue("cell_set_aligned_alias:''" in node3_pairs)
        self.assertTrue("cell_set_additional_aliases:''" in node3_pairs)

        node20_pairs = get_synonym_pairs(nodes[20]).split(PAIR_SEPARATOR)
        self.assertEqual("CS202002013_6", nodes[20]["cell_set_accession"])
        self.assertEqual(5, len(node20_pairs))
        self.assertTrue("cell_set_preferred_alias:Lamp5 Pdlim5_2" in node20_pairs)
        self.assertTrue("original_label:Lamp5 Pdlim5_2" in node20_pairs)
        self.assertTrue("cell_set_label:RNAseq 006" in node20_pairs)
        self.assertTrue("cell_set_aligned_alias:''" in node20_pairs)
        self.assertTrue("cell_set_additional_aliases:''" in node20_pairs)

        node50_pairs = get_synonym_pairs(nodes[50]).split(PAIR_SEPARATOR)
        self.assertEqual("CS202002013_146", nodes[50]["cell_set_accession"])
        self.assertEqual(5, len(node50_pairs))
        self.assertTrue("cell_set_preferred_alias:''" in node50_pairs)
        self.assertTrue("original_label:n30" in node50_pairs)
        self.assertTrue("cell_set_label:RNAseq 022-025" in node50_pairs)
        self.assertTrue("cell_set_aligned_alias:''" in node50_pairs)
        self.assertTrue("cell_set_additional_aliases:''" in node50_pairs)

    def test_nomenclature_nodes_edges(self):
        tree = nomenclature_2_nodes_n_edges(PATH_NOMENCLATURE_CSV)
        nodes = tree['nodes']

        self.assertEqual(177, len(nodes))
        self.assertEqual("CS201912131_4", nodes[3]["cell_set_accession"])
        self.assertEqual("CS201912131_21", nodes[20]["cell_set_accession"])
        self.assertEqual("CS201912131_51", nodes[50]["cell_set_accession"])
        self.assertEqual("CS201912131_181", nodes[176]["cell_set_accession"])

        edges = tree['edges']
        self.assertTrue(("CS201912131_41", "CS201912131_163") in edges)
        self.assertTrue(("CS201912131_40", "CS201912131_144") in edges)
        self.assertTrue(("CS201912131_39", "CS201912131_160") in edges)
        self.assertTrue(("CS201912131_38", "CS201912131_162") in edges)

    def test_nomenclature_nodes_edges_multi_inheritance(self):
        tree = nomenclature_2_nodes_n_edges(PATH_NOMENCLATURE_CSV_MOUSE)
        nodes = tree['nodes']

        self.assertEqual(257, len(nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_13' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_14' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_15' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_16' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_137' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_140' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_240' for node in nodes))

        edges = tree['edges']
        self.assertTrue(("CS202002013_13", "CS202002013_137") in edges)
        self.assertTrue(("CS202002013_14", "CS202002013_137") in edges)
        self.assertTrue(("CS202002013_15", "CS202002013_140") in edges)
        self.assertTrue(("CS202002013_16", "CS202002013_140") in edges)

        # multi-inheritance
        self.assertTrue(("CS202002013_14", "CS202002013_240") in edges)
        self.assertTrue(("CS202002013_16", "CS202002013_240") in edges)

    def test_nomenclature_nodes_edges_multi_inheritance2(self):
        tree = nomenclature_2_nodes_n_edges(PATH_NOMENCLATURE_CSV_MOUSE)
        nodes = tree['nodes']

        self.assertEqual(257, len(nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_35' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_36' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_38' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_39' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_40' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_41' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_159' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_161' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_163' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_164' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_162' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_245' for node in nodes))

        edges = tree['edges']
        self.assertTrue(("CS202002013_34", "CS202002013_159") in edges)
        self.assertTrue(("CS202002013_35", "CS202002013_159") in edges)
        self.assertTrue(("CS202002013_36", "CS202002013_161") in edges)
        self.assertTrue(("CS202002013_37", "CS202002013_161") in edges)
        self.assertTrue(("CS202002013_38", "CS202002013_163") in edges)
        self.assertTrue(("CS202002013_39", "CS202002013_164") in edges)
        self.assertTrue(("CS202002013_40", "CS202002013_164") in edges)
        self.assertTrue(("CS202002013_41", "CS202002013_162") in edges)
        self.assertTrue(("CS202002013_162", "CS202002013_160") in edges)

        # multi-inheritance
        self.assertTrue(("CS202002013_35", "CS202002013_245") in edges)
        self.assertTrue(("CS202002013_36", "CS202002013_245") in edges)
        # parent of 38 39 40 41
        self.assertTrue(("CS202002013_162", "CS202002013_245") in edges)
        self.assertFalse(("CS202002013_38", "CS202002013_245") in edges)
        self.assertFalse(("CS202002013_163", "CS202002013_245") in edges)

    def test_nomenclature_nodes_edges_multi_inheritance3(self):
        tree = nomenclature_2_nodes_n_edges(PATH_NOMENCLATURE_CSV_MOUSE)
        nodes = tree['nodes']

        self.assertEqual(257, len(nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_114' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_115' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_116' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_237' for node in nodes))
        self.assertTrue(any(node['cell_set_accession'] == 'CS202002013_231' for node in nodes))

        edges = tree['edges']

        self.assertTrue(("CS202002013_116", "CS202002013_237") in edges)
        # multi-inheritance, 114 115 relations
        self.assertTrue(("CS202002013_231", "CS202002013_237") in edges)

    # not test
    # def report_missing_alias(self):
    #     dend_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/CCN202002013.json")
    #     dend = dend_json_2_nodes_n_edges(dend_path)
    #     dend_tree = read_dendrogram_tree(dend_path)
    #
    #     subtrees = get_subtrees(dend_tree, read_taxonomy_config("CCN202002013"))
    # 
    #     path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/alias_report.tsv")
    #
    #     with open(path, mode='w') as out:
    #         writer = csv.writer(out, delimiter="\t", quotechar='"')
    #         writer.writerow(["ID", "cell_set_additional_alias", "cell_set_aligned_alias"])
    #         for o in dend['nodes']:
    #             if o['cell_set_accession'] in set.union(*subtrees) and not o['cell_set_preferred_alias']:
    #                 if o['cell_set_additional_aliases'] or o['cell_set_aligned_alias']:
    #                     additional_alias = o['cell_set_additional_aliases'] if 'cell_set_additional_aliases' in o.keys() else ''
    #                     aligned_alias = o['cell_set_aligned_alias'] if 'cell_set_aligned_alias' in o.keys() else ''
    #                     writer.writerow([o['cell_set_accession'], additional_alias, aligned_alias])

    def test_find_direct_paths(self):
        dend = cas_json_2_nodes_n_edges(PATH_MOUSE_CAS)
        dend_tree = generate_dendrogram_tree(dend)
        node_index = {node['cell_set_accession']: node for node in dend['nodes']}

        cas = read_json_file(PATH_MOUSE_CAS)
        labelsets = { labelset["name"]: labelset["rank"] for labelset in cas['labelsets'] if "rank" in labelset}

        chains = find_singleton_chains(dend_tree)
        # longer chains and then by "higher rank first" sorting
        chains.sort(key=lambda chain: (-len(chain), -1 * labelsets[node_index[chain[0]]["labelset"]]))

        label_chain = set()
        for chain in chains:
            chain_srt = "Chain: " + " -> ".join([node_index[n]["cell_label"] for n in chain])
            # print(chain_srt)
            label_chain.add(chain_srt)


        self.assertEqual(248, len(chains))
        # self.compare_with_old_results(label_chain)
        self.write_chains_to_tsv(chains, node_index, labelsets, PATH_MOUSE_REPORT_TSV)

    def write_chains_to_tsv(self, chains, node_index, labelsets, output_filepath):
        # Sort labelsets by rank (higher rank to lower rank)
        sorted_labelsets = sorted(labelsets, key=labelsets.get, reverse=True)
        sorted_labelsets.append("preferred_name")

        with open(output_filepath, mode='w') as out:
            writer = csv.writer(out, delimiter="\t", quotechar='"')
            writer.writerow(sorted_labelsets)

            for chain in chains:
                row = [''] * len(sorted_labelsets)
                for item in chain:
                    labelset = node_index[item]["labelset"]
                    column_index = sorted_labelsets.index(labelset)
                    row[column_index] = node_index[item]["cell_label"]
                writer.writerow(row)

    def compare_with_old_results(self, label_chain):
        url = "https://gist.githubusercontent.com/dosumis/af5104483b5c26fdd382495d1b71bc5e/raw/0839b81e32ab479535e39d07f645a7c1f2bca47c/1_cell_set_multiple_levels.txt"
        response = requests.get(url)
        response.raise_for_status()
        lines = response.text.splitlines()
        rows_set = set(lines[1:])
        print(len(rows_set))
        print(len(label_chain))
        diff = rows_set.difference(label_chain)
        for item in diff:
            print(item)


if __name__ == '__main__':
    unittest.main()
