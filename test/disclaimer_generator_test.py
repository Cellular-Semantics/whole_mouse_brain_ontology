import unittest
from disclaimer_generator import get_mba_entity, is_location_supported, get_location_symbols

class DisclaimerGeneratorTestCase(unittest.TestCase):

    def test_get_mba_entity(self):
        self.assertEqual("https://purl.brain-bican.org/ontology/mbao/MBA_507", get_mba_entity("MOB"))

    def test_is_location_supported(self):
        self.assertTrue(is_location_supported("BMA", ["BMAp"]))
        self.assertTrue(is_location_supported("CTX", ["BMAp"]))
        self.assertFalse(is_location_supported("BMAp", ["BMA"]))

    def test_get_location_symbols(self):
        self.assertEqual(["LA", "BLA", "BMA", "PA"], get_location_symbols("0221 LA-BLA-BMA-PA Glut_1"))
        self.assertEqual(["ILC"], get_location_symbols("5320 ILC NN_2"))

if __name__ == '__main__':
    unittest.main()
