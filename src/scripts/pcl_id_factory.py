"""
Responsible with allocating stable PCL IDs for taxonomy nodes. Id ranges for taxonomies are allocated based on
taxonomies order in the 'taxonomy_details.yaml' configuration file. Automatic ID range allocation starts from
#ID_RANGE_BASE and allocates 400 IDs for classes and 600 IDs for individuals

ID range allocation logic is as follows

    - 0010000 to 0010999  custom classes and properties (manually managed)
    - 0011000 taxonomy1 individual # idle: now individuals use accession_id
    - 0011001 to 0011499 taxonomy1 classes (500)
    - 0012451 to 0012500 taxonomy1 datasets (50)
    - 0012501 to 0012999 taxonomy1 marker gene sets (500)
    - 0013000 to 0014999 taxonomy1 spare id space (2000)
    - ...

"""

import yaml
import os


TAXONOMY_DETAILS_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     '../dendrograms/taxonomy_details.yaml')

# Allocate IDs starting from PCL_0011000
ID_RANGE_BASE = 110000

LABELSET_SYMBOLS = { "CLAS": "class",
                     "SUBC": "subclass",
                     "SUPT": "supertype",
                     "CLUS": "cluster" }


class PCLIdFactory:

    def __init__(self, taxonomy):
        self.taxonomies = read_taxonomy_details_yaml()
        self.taxonomy_ids = [taxon["Taxonomy_id"] for taxon in self.taxonomies]
        ranked_labelsets = [labelset for labelset in taxonomy['labelsets'] if "rank" in labelset]
        self.labelsets = [labelset["name"] for labelset in sorted(ranked_labelsets, key=lambda x: x["rank"], reverse=True)]

        # class ranges per labelset
        self.class_ranges = {}
        id_range = ID_RANGE_BASE
        for labelset in self.labelsets:
            self.class_ranges[labelset] = id_range
            id_range = id_range + int(sum(1 for node in taxonomy['annotations'] if node['labelset'] == labelset) * 1.5)  # %50 more than the number of nodes
            id_range = round_up_to_nearest(id_range, 1)
        self.dataset_id_start = id_range + 1
        self.marker_set_id_start = round_up_to_nearest(self.dataset_id_start + 50, 2)


    def get_class_id(self, accession_id):
        """
        Generates a PCL id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
        in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a PCL id displaced by the
        node_id.
        Args:
            accession_id: cell set accession id

        Returns: seven digit PCL id as string
        """
        node_id, labelset = parse_accession_id(accession_id)
        pcl_id = self.class_ranges[labelset] + node_id

        return str(pcl_id).zfill(7)


    def get_taxonomy_id(self, taxonomy_id):
        """
        DEPRECATED: now individuals use accession_id

        Generates a PCL id for the given taxonomy. it is the first id of the taxonomy allocated id range (such as 0012000)
        Args:
            taxonomy_id: taxonomy id

        Returns: seven digit PCL id as string
        """
        pcl_id = ID_RANGE_BASE

        return str(pcl_id).zfill(7)


    def get_dataset_id(self, taxonomy_id, dataset_index):
        """
        Generates a PCL id for the given dataset. Dataset id range is last 50 ids of the taxonomy id range.
        Args:
            taxonomy_id: taxonomy id
            dataset_index: index of the dataset (0 to 48)

        Returns: seven digit PCL id as string
        """
        pcl_id = self.dataset_id_start + dataset_index

        return str(pcl_id).zfill(7)


    def get_marker_gene_set_id(self, accession_id):
        """
        Generates a PCL id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
        in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a PCL id displaced by the
        node_id in the marker gene set range (taxonomy range + 400).
        Args:
            accession_id: cell set accession id

        Returns: seven digit PCL id as string
        """
        node_id, labelset = parse_accession_id(accession_id)
        class_id = self.class_ranges[labelset] + node_id
        marker_set_id_displacement = self.marker_set_id_start - ID_RANGE_BASE
        pcl_id = class_id + marker_set_id_displacement

        return str(pcl_id).zfill(7)

def read_taxonomy_details_yaml():
    with open(r'%s' % TAXONOMY_DETAILS_YAML) as file:
        documents = yaml.full_load(file)
    return documents

def parse_accession_id(accession_id):
    """
    Parses taxonomy id and node id from the accession id and returns node id and labelset name.
    Args:
        accession_id: cell set accession id (such as CS20230722_CLAS_01)

    Returns: tuple of node_id and labelset name.
    """
    accession_parts = str(accession_id).split("_")
    node_id = int(accession_parts[2].strip())
    labelset_abbr = accession_parts[1].strip()

    return node_id, LABELSET_SYMBOLS[labelset_abbr]


# def get_reverse_id(pcl_id_str):
#     """
#     Converts PCL id to cell cet accession id
#     Args:
#         pcl_id_str: PCL id
#     Returns: cell cet accession id
#     """
#     if str(pcl_id_str).startswith("http://purl.obolibrary.org/obo/pcl/") or str(pcl_id_str).startswith("PCL_INDV:"):
#         pcl_id_str = str(pcl_id_str).replace("http://purl.obolibrary.org/obo/pcl/", "")
#         pcl_id_str = str(pcl_id_str).replace("PCL_INDV:", "")
#         return pcl_id_str
#
#     pcl_id_str = str(pcl_id_str).replace("http://purl.obolibrary.org/obo/PCL_", "")
#     pcl_id_str = str(pcl_id_str).replace("PCL:", "")
#     pcl_id_str = str(pcl_id_str).replace("PCL_", "")
#
#     pcl_id = int(pcl_id_str)
#
#     taxonomy_index = int((pcl_id - ID_RANGE_BASE) / TAXONOMY_ID_RANGE)
#     taxonomy_id = taxonomy_ids[taxonomy_index].replace("CCN", "CS")
#
#     node_id = (pcl_id - ID_RANGE_BASE) - (TAXONOMY_ID_RANGE * taxonomy_index)
#     if node_id > INDV_ID_DISPLACEMENT:
#         node_id = node_id - INDV_ID_DISPLACEMENT
#
#     if taxonomy_id == "CS1908210":
#         accession_id = taxonomy_id + str(node_id).zfill(3)
#     else:
#         accession_id = taxonomy_id + "_" + str(node_id)
#
#     return accession_id


def is_pcl_id(id_str):
    """
    Returns 'True' if given id is PCL id.
    Args:
        id_str: ID string to check
    Returns: 'True' if given id is PCL id, 'False' otherwise
    """
    return str(id_str).startswith("http://purl.obolibrary.org/obo/PCL_") \
        or str(id_str).startswith("PCL:") or str(id_str).startswith("PCL_") \
        or str(id_str).startswith("http://purl.obolibrary.org/obo/pcl/") \
        or str(id_str).startswith("PCL_INDV:")


def round_up_to_nearest(value, zeros=1):
    """
    Rounds up the given integer to the nearest bigger integer ending with the specified number of zeros.

    Args:
        value (int): The integer to be rounded up.
        zeros (int): The number of trailing zeros for the rounding. Default is 1.

    Returns:
        int: The rounded integer.
        round_up_to_nearest(123) -> 130
        round_up_to_nearest(123, 2) -> 200
    """
    factor = 10 ** zeros
    return ((value + factor - 1) // factor) * factor
