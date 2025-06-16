import unittest
from ensembl import get_ncbi_gene_ids


class GenesTestCase(unittest.TestCase):

    def test_ensembl_to_ncbi_conversion_success(self):
        mapping, success, failure = get_ncbi_gene_ids(["ensembl:ENSMUSG00000051951"])
        print(mapping)
        self.assertEqual("NCBIGene:497097", mapping["ensembl:ENSMUSG00000051951"])

    def test_ensembl_to_ncbi_conversion_none(self):
        mapping, success, failure = get_ncbi_gene_ids(["ensembl:ENSMUSG00000100237"])
        print(mapping)
        self.assertEqual(1, failure)
        self.assertEqual(0, len(mapping))

    def test_ensembl_to_ncbi_conversion_not_found(self):
        mapping, success, failure = get_ncbi_gene_ids(["ensembl:ENSMUSG00000094791"])
        print(mapping)
        self.assertEqual(1, failure)
        self.assertEqual(0, len(mapping))



if __name__ == '__main__':
    unittest.main()
