"""
Responsible with allocating stable PCL IDs for taxonomy nodes. Id ranges for taxonomies are allocated based on
taxonomies order in the 'taxonomy_details.yaml' configuration file.
Automatic ID range allocation starts from #ID_RANGE_BASE and allocates id spaces to entities based on their count in the taxonomy + some spare space.

ID range allocation logic is as follows:
    (annotation count = 6905)

    - 110000 to 110059 'CLAS' labelset classes + (%50 spare space)
    - 110060 to 110569 'SUBC' labelset classes + (%50 spare space)
    - 110570 to 112379 'SUPT' labelset classes + (%50 spare space)
    - 112380 to 120370 'CLUS' labelset classes (%50 spare space)
    - 120371 to 120499 dataset classes (50 + round up to nearest 100)
    - 120500 to 130859 marker set (%50 spare space)
    - 130860 to 141219 NS Forest marker set (%50 spare space)
    - 141220 to 151579 Within subclass marker set (%50 spare space)
    - 151580 to 159520 Evidence marker set (%50 spare space)

Total allocated id space: 159520 - 110000 = 49520 ids
"""

from base_id_factory import BaseIdFactory

# Allocate IDs starting from PCL_0110000
ID_RANGE_BASE = 110000


class PCLIdFactory(BaseIdFactory):

    PREFIXES = [
        "http://purl.obolibrary.org/obo/PCL_", "PCL:", "PCL_",
        "http://purl.obolibrary.org/obo/pcl/", "PCL_INDV:"
    ]

    LABELSET_SYMBOLS = {"CLAS": "class",
                        "SUBC": "subclass",
                        "SUPT": "supertype",
                        "CLUS": "cluster"}

    def __init__(self, taxonomy):
        self.taxonomies = self.read_taxonomy_details_yaml()
        self.taxonomy_ids = [taxon["Taxonomy_id"] for taxon in self.taxonomies]
        ranked_labelsets = [labelset for labelset in taxonomy['labelsets'] if "rank" in labelset]
        self.labelsets = [labelset["name"] for labelset in sorted(ranked_labelsets, key=lambda x: x["rank"], reverse=True)]
        annotation_count = sum(1 for node in taxonomy['annotations'])

        # class ranges per labelset
        self.class_ranges = {}
        id_range = ID_RANGE_BASE
        for labelset in self.labelsets:
            self.class_ranges[labelset] = id_range
            id_range = id_range + int(sum(1 for node in taxonomy['annotations'] if node['labelset'] == labelset) * 1.5)  # %50 more than the number of nodes
            id_range = self.round_up_to_nearest(id_range, 1)
        self.dataset_id_start = id_range + 1
        self.marker_set_id_start = self.round_up_to_nearest(self.dataset_id_start + 50, 2)
        self.nsf_marker_set_start = self.round_up_to_nearest( int(self.marker_set_id_start + (annotation_count * 1.5)) , 1)
        self.ws_marker_set_id_start = self.round_up_to_nearest( int(self.nsf_marker_set_start + (annotation_count * 1.5)) , 1)
        self.evidence_marker_set_id_start = self.round_up_to_nearest( int(self.ws_marker_set_id_start + (annotation_count * 1.5)) , 1)

        # print(self.class_ranges)
        # print("Dataset id range: " + str(self.dataset_id_start) + " to " + str(self.marker_set_id_start - 1))
        # print("Marker set id range: " + str(self.marker_set_id_start) + " to " + str(self.nsf_marker_set_start - 1))
        # print("NS Forest marker set id range: " + str(self.nsf_marker_set_start) + " to " + str(self.ws_marker_set_id_start - 1))
        # print("Within subclass marker set id range: " + str(self.ws_marker_set_id_start) + " to " + str(self.evidence_marker_set_id_start - 1))
        # evidence_marker_set_id_end = self.round_up_to_nearest( int(self.evidence_marker_set_id_start + (annotation_count * 1.15)) , 1)
        # print("Evidence marker set id range: " + str(self.evidence_marker_set_id_start) + " to " + str(evidence_marker_set_id_end))


    def get_class_id(self, accession_id):
        """
        Generates a PCL id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
        in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a PCL id displaced by the
        node_id.
        Args:
            accession_id: cell set accession id

        Returns: seven digit PCL id as string
        """
        node_id, labelset = self.parse_accession_id(accession_id)
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
        node_id in the marker gene set range.
        Args:
            accession_id: cell set accession id

        Returns: seven digit PCL id as string
        """
        node_id, labelset = self.parse_accession_id(accession_id)
        class_id = self.class_ranges[labelset] + node_id
        marker_set_id_displacement = self.marker_set_id_start - ID_RANGE_BASE
        pcl_id = class_id + marker_set_id_displacement

        return str(pcl_id).zfill(7)


    def get_ws_marker_gene_set_id(self, accession_id):
        """
        Generates a PCL id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
        in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a PCL id displaced by the
        node_id in the within subclass marker gene set range.
        Args:
            accession_id: cell set accession id

        Returns: seven digit PCL id as string
        """
        node_id, labelset = self.parse_accession_id(accession_id)
        class_id = self.class_ranges[labelset] + node_id
        marker_set_id_displacement = self.ws_marker_set_id_start - ID_RANGE_BASE
        pcl_id = class_id + marker_set_id_displacement

        return str(pcl_id).zfill(7)

    def get_nsf_marker_gene_set_id(self, accession_id):
        """
        Generates a PCL id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
        in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a PCL id displaced by the
        node_id in the NS Forest marker gene set range.
        Args:
            accession_id: cell set accession id

        Returns: seven digit PCL id as string
        """
        node_id, labelset = self.parse_accession_id(accession_id)
        class_id = self.class_ranges[labelset] + node_id
        marker_set_id_displacement = self.nsf_marker_set_start - ID_RANGE_BASE
        pcl_id = class_id + marker_set_id_displacement

        return str(pcl_id).zfill(7)


    def get_evidence_marker_gene_set_id(self, accession_id):
        """
        Generates a PCL id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
        in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a PCL id displaced by the
        node_id in the evidence marker gene set range.
        Args:
            accession_id: cell set accession id

        Returns: seven digit PCL id as string
        """
        node_id, labelset = self.parse_accession_id(accession_id)
        class_id = self.class_ranges[labelset] + node_id
        marker_set_id_displacement = self.evidence_marker_set_id_start - ID_RANGE_BASE
        pcl_id = class_id + marker_set_id_displacement

        return str(pcl_id).zfill(7)


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
