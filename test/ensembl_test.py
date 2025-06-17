import unittest
from ensembl import get_ncbi_gene_ids, mygene_convert_ensembl_to_ncbi, mygene_convert_ensembl_to_ncbi_by_symbol


class GenesTestCase(unittest.TestCase):

    def test_ensembl_to_ncbi_conversion_success(self):
        mapping, failures = get_ncbi_gene_ids(["ensembl:ENSMUSG00000051951"])
        print(mapping)
        self.assertEqual("NCBIGene:497097", mapping["ensembl:ENSMUSG00000051951"])

    def test_ensembl_to_ncbi_conversion_none(self):
        mapping, failures = get_ncbi_gene_ids(["ensembl:ENSMUSG00000100237"])
        print(mapping)
        self.assertEqual(1, len(failures))
        self.assertEqual(0, len(mapping))

    def test_ensembl_to_ncbi_conversion_not_found(self):
        mapping, failures = get_ncbi_gene_ids(["ensembl:ENSMUSG00000094791"])
        print(mapping)
        self.assertEqual(1, len(failures))
        self.assertEqual(0, len(mapping))

    def test_mygene_ensembl_to_ncbi_conversion(self):
        mappings = mygene_convert_ensembl_to_ncbi(["ensembl:ENSMUSG00000049336", "ensembl:ENSMUSG00000095041"])

        self.assertEqual(1, len(mappings))
        self.assertTrue("ensembl:ENSMUSG00000049336" in mappings)
        self.assertEqual("NCBIGene:23964", mappings["ensembl:ENSMUSG00000049336"])

    def test_mygene_ensembl_to_ncbi_conversion_by_symbol(self):
        self.assertEqual("NCBIGene:78634", mygene_convert_ensembl_to_ncbi_by_symbol("Spaca7"))
        self.assertEqual("NCBIGene:78634", mygene_convert_ensembl_to_ncbi_by_symbol("Efhd1os"))
        self.assertEqual(None, mygene_convert_ensembl_to_ncbi_by_symbol("NotExistsGene"))




if __name__ == '__main__':
    unittest.main()
