"""
Responsible with allocating stable CLM IDs for the taxonomy nodes. Id ranges for taxonomies are allocated based on
taxonomies order in the 'taxonomy_details.yaml' configuration file.
Automatic ID range allocation starts from #ID_RANGE_BASE and allocates id spaces to entities based on their count in the taxonomy + some spare space.

5000000 - 6000000 id range is allocated for BICAN (shared by all BICAN ontologies).

ID range allocation logic is as follows:
    (annotation count = 6905)

    - 5000000 to 5007619    Marker set id range (%10 spare space)
    - 5007620 to 5015219    NS Forest marker set id range (%10 spare space)
    - 5015220 to 5022819    Within subclass marker set id range (%10 spare space)
    - 5022820 to 5030760    Evidence marker set id range (%10 spare space)

Total allocated id space: 5030760 - 5000000 = 30760 ids
"""

from base_id_factory import BaseIdFactory

# Allocate IDs starting from CLM_5000000
ID_RANGE_BASE = 5000000


class CLMIdFactory(BaseIdFactory):

    PREFIXES = [
        "http://purl.obolibrary.org/obo/CLM_", "CLM:", "CLM_",
        "http://purl.obolibrary.org/obo/clm/"
    ]

    LABELSET_SYMBOLS = {"CLAS": "class",
                        "SUBC": "subclass",
                        "SUPT": "supertype",
                        "CLUS": "cluster"}

    def __init__(self, taxonomy):
        self.taxonomies = self.read_taxonomy_details_yaml()
        ranked_labelsets = [labelset for labelset in taxonomy['labelsets'] if "rank" in labelset]
        self.labelsets = [labelset["name"] for labelset in sorted(ranked_labelsets, key=lambda x: x["rank"], reverse=True)]
        annotation_count = sum(1 for node in taxonomy['annotations'])

        self.ms_ranges = {}
        id_range = ID_RANGE_BASE
        for labelset in self.labelsets:
            self.ms_ranges[labelset] = id_range
            id_range = id_range + int(sum(1 for node in taxonomy['annotations'] if node['labelset'] == labelset) * 1.1)  # %10 more than the number of nodes
            id_range = self.round_up_to_nearest(id_range, 1)

        self.nsf_marker_set_start = id_range + 10
        self.ws_marker_set_id_start = self.round_up_to_nearest( int(self.nsf_marker_set_start + (annotation_count * 1.1)) , 1)
        self.evidence_marker_set_id_start = self.round_up_to_nearest( int(self.ws_marker_set_id_start + (annotation_count * 1.1)) , 1)

        print("Marker set id range: " + str(ID_RANGE_BASE) + " to " + str(self.nsf_marker_set_start - 1))
        print("NS Forest marker set id range: " + str(self.nsf_marker_set_start) + " to " + str(self.ws_marker_set_id_start - 1))
        print("Within subclass marker set id range: " + str(self.ws_marker_set_id_start) + " to " + str(self.evidence_marker_set_id_start - 1))
        evidence_marker_set_id_end = self.round_up_to_nearest( int(self.evidence_marker_set_id_start + (annotation_count * 1.15)) , 1)
        print("Evidence marker set id range: " + str(self.evidence_marker_set_id_start) + " to " + str(evidence_marker_set_id_end))


    def get_marker_gene_set_id(self, accession_id):
        """
        Generates a CLM id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
        in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a CLM id displaced by the
        node_id in the marker gene set range.
        Args:
            accession_id: cell set accession id

        Returns: seven digit CLM id as string
        """
        node_id, labelset = self.parse_accession_id(accession_id)
        clm_id = self.ms_ranges[labelset] + node_id
        return str(clm_id).zfill(7)


    def get_ws_marker_gene_set_id(self, accession_id):
        """
        Generates a CLM id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
        in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a CLM id displaced by the
        node_id in the within subclass marker gene set range.
        Args:
            accession_id: cell set accession id

        Returns: seven digit CLM id as string
        """
        node_id, labelset = self.parse_accession_id(accession_id)
        markerset_id = self.ms_ranges[labelset] + node_id
        ws_marker_set_id_displacement = self.ws_marker_set_id_start - ID_RANGE_BASE
        clm_id = markerset_id + ws_marker_set_id_displacement

        return str(clm_id).zfill(7)

    def get_nsf_marker_gene_set_id(self, accession_id):
        """
        Generates a CLM id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
        in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a CLM id displaced by the
        node_id in the NS Forest marker gene set range.
        Args:
            accession_id: cell set accession id

        Returns: seven digit CLM id as string
        """
        node_id, labelset = self.parse_accession_id(accession_id)
        markerset_id = self.ms_ranges[labelset] + node_id
        nsf_marker_set_id_displacement = self.nsf_marker_set_start - ID_RANGE_BASE
        clm_id = markerset_id + nsf_marker_set_id_displacement

        return str(clm_id).zfill(7)


    def get_evidence_marker_gene_set_id(self, accession_id):
        """
        Generates a CLM id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
        in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a CLM id displaced by the
        node_id in the evidence marker gene set range.
        Args:
            accession_id: cell set accession id

        Returns: seven digit CLM id as string
        """
        node_id, labelset = self.parse_accession_id(accession_id)
        markerset_id = self.ms_ranges[labelset] + node_id
        evidence_marker_set_id_displacement = self.evidence_marker_set_id_start - ID_RANGE_BASE
        clm_id = markerset_id + evidence_marker_set_id_displacement

        return str(clm_id).zfill(7)
