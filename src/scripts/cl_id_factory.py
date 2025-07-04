"""
Responsible with allocating stable CL IDs for the taxonomy nodes. Id ranges for taxonomies are allocated based on
taxonomies order in the 'taxonomy_details.yaml' configuration file.
Automatic ID range allocation starts from #ID_RANGE_BASE and allocates id spaces to entities based on their count in the taxonomy + some spare space.

ID range allocation logic is as follows:
    (annotation count = 6905)

    - 0100000 to 0100200  custom classes and properties (manually managed)
    - 0100200 to 100239 'CLAS' labelset classes + (%15 spare space)
    - 0100240 to 100629 'SUBC' labelset classes + (%15 spare space)
    - 100630 to 102019 'SUPT' labelset classes + (%15 spare space)
    - 102020 to 108140 'CLUS' labelset classes (%15 spare space)
    - Markersets will use CLM id space

Total allocated id space: 108140 - 100200 = 7939 ids
"""
from base_id_factory import BaseIdFactory

# Allocate IDs starting from CL_4300000
ID_RANGE_BASE = 4300000


class CLIdFactory(BaseIdFactory):

    PREFIXES = [
        "http://purl.obolibrary.org/obo/CL_", "CL:", "CL_",
        "http://purl.obolibrary.org/obo/cl/"
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
            id_range = id_range + int(sum(1 for node in taxonomy['annotations'] if node['labelset'] == labelset) * 1.15)  # %15 more than the number of nodes
            id_range = self.round_up_to_nearest(id_range, 1)

        # print(self.class_ranges)


    def get_class_id(self, accession_id):
        """
        Generates a CL id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
        in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a CL id displaced by the
        node_id.
        Args:
            accession_id: cell set accession id

        Returns: seven digit CL id as string
        """
        node_id, labelset = self.parse_accession_id(accession_id)
        cl_id = self.class_ranges[labelset] + node_id

        return str(cl_id).zfill(7)


    def get_taxonomy_id(self, taxonomy_id):
        """
        DEPRECATED: now individuals use accession_id

        Generates a CL id for the given taxonomy. it is the first id of the taxonomy allocated id range (such as 0012000)
        Args:
            taxonomy_id: taxonomy id

        Returns: seven digit CL id as string
        """
        cl_id = ID_RANGE_BASE

        return str(cl_id).zfill(7)
