import yaml
import os

from abc import ABC, abstractmethod


class BaseIdFactory(ABC):
    """
    Abstract base class for ID factories.
    Provides the rounding function and a method to verify if an id belongs to the factory.
    Subclasses must define the PREFIXES class attribute and implement their own __init__.
    """
    PREFIXES = []  # Subclasses must override
    LABELSET_SYMBOLS = {} # Subclasses must override

    @staticmethod
    def round_up_to_nearest(value, zeros=1):
        """
        Rounds up the given integer to the nearest integer ending with the specified number of zeros.

        Args:
            value (int): The number to be rounded.
            zeros (int): Number of trailing zeros.

        Returns:
            int: Rounded integer.

        round_up_to_nearest(123) -> 130
        round_up_to_nearest(123, 2) -> 200
        """
        factor = 10 ** zeros
        return ((value + factor - 1) // factor) * factor

    @staticmethod
    def read_taxonomy_details_yaml():
        config = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../dendrograms/taxonomy_details.yaml')
        with open(r'%s' % config) as file:
            documents = yaml.full_load(file)
        return documents

    @classmethod
    def is_own_id(cls, id_str):
        """
        Returns True if the given id_str starts with one of the prefixes defined in the subclass.

        Args:
            id_str (str): Identifier string.

        Returns:
            bool: True if id_str contains one of the PREFIXES.
        """
        for prefix in getattr(cls, "PREFIXES", []):
            if str(id_str).startswith(prefix):
                return True
        return False

    @classmethod
    def parse_accession_id(cls, accession_id):
        """
        Parses taxonomy id and node id from the accession id and returns node id and labelset name.
        Args:
            accession_id: cell set accession id (such as CS20230722_CLAS_01)

        Returns: tuple of node_id and labelset name.
        """
        accession_parts = str(accession_id).split("_")
        node_id = int(accession_parts[2].strip())
        labelset_abbr = accession_parts[1].strip()

        labelset_symbols = getattr(cls, "LABELSET_SYMBOLS", dict())
        return node_id, labelset_symbols[labelset_abbr]

    @abstractmethod
    def __init__(self, taxonomy):
        pass