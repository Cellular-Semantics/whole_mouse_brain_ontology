import unittest
from pcl_id_factory import PCLIdFactory
from cl_id_factory import CLIdFactory
from clm_id_factory import CLMIdFactory

class PCLIdFactoryTestCase(unittest.TestCase):

    def setUp(self):
        # Initialize the PCLIdFactory with a mock taxonomy
        self.taxonomy = {
            'labelsets': [
                {'name': 'class', 'rank': 3},
                {'name': 'subclass', 'rank': 2},
                {'name': 'supertype', 'rank': 1},
                {'name': 'cluster', 'rank': 0}
            ],
            'annotations': [{'labelset': 'class', 'cell_set_accession': 'CS20230722_CLAS_01'},
                            {'labelset': 'subclass', 'cell_set_accession': 'CS20230722_SUBC_001'},
                            {'labelset': 'subclass', 'cell_set_accession': 'CS20230722_SUBC_002'},
                            {'labelset': 'supertype', 'cell_set_accession': 'CS20230722_SUPT_0001'},
                            {'labelset': 'supertype', 'cell_set_accession': 'CS20230722_SUPT_0002'},
                            {'labelset': 'supertype', 'cell_set_accession': 'CS20230722_SUPT_0003'},
                            {'labelset': 'cluster', 'cell_set_accession': 'CS20230722_CLUS_0001'},
                            {'labelset': 'cluster', 'cell_set_accession': 'CS20230722_CLUS_0002'},
                            {'labelset': 'cluster', 'cell_set_accession': 'CS20230722_CLUS_0003'},
                            {'labelset': 'cluster', 'cell_set_accession': 'CS20230722_CLUS_0004'},
                            {'labelset': 'cluster', 'cell_set_accession': 'CS20230722_CLUS_0005'},
                            ]
        }

    def test_pcl_ids(self):
        self.pcl_id_factory = PCLIdFactory(self.taxonomy)

        self.assertEqual("0110001", self.pcl_id_factory.get_class_id("CS20230722_CLAS_01"))
        self.assertEqual("0110012", self.pcl_id_factory.get_class_id("CS20230722_SUBC_002"))
        self.assertEqual("0110023", self.pcl_id_factory.get_class_id("CS20230722_SUPT_0003"))
        self.assertEqual("0110034", self.pcl_id_factory.get_class_id("CS20230722_CLUS_0004"))

        self.assertEqual("0110112", self.pcl_id_factory.get_marker_gene_set_id("CS20230722_SUBC_002"))
        self.assertEqual("0110132", self.pcl_id_factory.get_nsf_marker_gene_set_id("CS20230722_SUBC_002"))
        self.assertEqual("0110152", self.pcl_id_factory.get_ws_marker_gene_set_id("CS20230722_SUBC_002"))
        self.assertEqual("0110172", self.pcl_id_factory.get_evidence_marker_gene_set_id("CS20230722_SUBC_002"))


    def test_cl_ids(self):
        self.cl_id_factory = CLIdFactory(self.taxonomy)

        self.assertEqual("0100201", self.cl_id_factory.get_class_id("CS20230722_CLAS_01"))
        self.assertEqual("0100212", self.cl_id_factory.get_class_id("CS20230722_SUBC_002"))
        self.assertEqual("0100223", self.cl_id_factory.get_class_id("CS20230722_SUPT_0003"))
        self.assertEqual("0100234", self.cl_id_factory.get_class_id("CS20230722_CLUS_0004"))

    def test_clm_ids(self):
        self.clm_id_factory = CLMIdFactory(self.taxonomy)

        self.assertEqual("5000012", self.clm_id_factory.get_marker_gene_set_id("CS20230722_SUBC_002"))
        self.assertEqual("5000062", self.clm_id_factory.get_nsf_marker_gene_set_id("CS20230722_SUBC_002"))
        self.assertEqual("5000082", self.clm_id_factory.get_ws_marker_gene_set_id("CS20230722_SUBC_002"))
        self.assertEqual("5000102", self.clm_id_factory.get_evidence_marker_gene_set_id("CS20230722_SUBC_002"))


if __name__ == '__main__':
    unittest.main()
