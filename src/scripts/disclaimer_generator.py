"""
This script is used to analyse the data and generate a disclaimer for the inconsistent cases.
Following inconsistency checks are performed:
- Cell sets names include anatomical location unsupported by CCF
  Check: https://github.com/Cellular-Semantics/WMB_taxonomy_hacking/blob/location_experiments/Test_anat.ipynb for the original analysis
- Clusters where NT in name is not supported by marker analysis
"""
import os
import re
from typing import Optional

import pandas as pd
from rdflib import Graph

# manually applied closure over part_of using relation graph
MBAO_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/resources/mbao-base-materialized.owl")

# Singleton materialized graph
mba_ontology = None


def get_anatomical_location_inconsistencies(cluster_annotations_path: str) -> dict:
    """
    Returns the list of cell sets names that include anatomical location unsupported by CCF.
    """
    clusters = pd.read_csv(cluster_annotations_path).dropna(subset=['cluster_id_label'])
    inconsistencies = dict()
    inconsistencies.update(check_cluster_level_name_consistency(clusters))
    inconsistencies.update(check_supertype_level_name_consistency(clusters))
    return inconsistencies


def check_cluster_level_name_consistency(clusters: pd.DataFrame, log_inconsistencies: bool = False) -> dict:
    """
    For each cluster checks if location names are supported by CCF_acronyms.
    We are abandoning this approach since a siblings based (supertype level) analysis makes more sense
    """
    inconsistencies = dict()
    for index, row in clusters.iterrows():
        locations = get_location_symbols(row['cluster_id_label'])
        for location in locations:
            if location in ['OB', 'in', 'out', 'mi']:
                # ignore some values for now
                continue
            if get_mba_entity(location) and not pd.isna(row["CCF_acronym.freq"]):
                ccf_acronym_str = row["CCF_acronym.freq"]
                ccf_acronyms = [n.split(':')[0] for n in ccf_acronym_str.split(',') if (ccf_acronym_str and (re.match('^[A-Z].*', n)))]
                # print(row['cluster_id_label'] + "  " + location + "  " + str(ccf_acronyms))
                if ccf_acronyms and not is_location_supported(location, ccf_acronyms):
                    locations = inconsistencies.get(row['cluster_id_label'], [])
                    locations.append(location)
                    inconsistencies[row['cluster_id_label']] = locations
                    if log_inconsistencies:
                        print(f"{location} in '{row['cluster_id_label']}' is not supported by any of the ccf values {', '.join(ccf_acronyms)}")
    return inconsistencies


def check_supertype_level_name_consistency(clusters: pd.DataFrame, log_inconsistencies: bool = False) -> dict:
    """
    Checks if anatomical locations mentioned in the supertypes are supported by their child (cluster) CCF_acronyms.
    """
    inconsistencies = dict()
    last_supertype = None
    last_supertype_ccfs = set()
    for index, row in clusters.iterrows():
        current_supertype = row["supertype_id_label"]
        if last_supertype is None:
            last_supertype = current_supertype
        if current_supertype != last_supertype:
            # process name check
            locations = get_location_symbols(last_supertype)
            for location in locations:
                if get_mba_entity(location) and not pd.isna(row["CCF_acronym.freq"]):
                    if not is_location_supported(location, list(last_supertype_ccfs)):
                        locations = inconsistencies.get(last_supertype, [])
                        locations.append(location)
                        inconsistencies[last_supertype] = locations
                        if log_inconsistencies:
                            print(
                                f"{location} in '{last_supertype}' is not supported by any of the ccf values {', '.join(list(last_supertype_ccfs))}")
            last_supertype_ccfs = set()
            last_supertype = current_supertype

        # cumulatively collect CCF_acronym locations
        if not pd.isna(row["CCF_acronym.freq"]):
            ccf_acronym_str = row["CCF_acronym.freq"]
            ccf_acronyms = [n.split(':')[0] for n in ccf_acronym_str.split(',') if
                            (ccf_acronym_str and (re.match('^[A-Z].*', n)))]
            last_supertype_ccfs.update(ccf_acronyms)
    return inconsistencies

def get_mba_entity(symbol: str) -> Optional[str]:
    """
    Returns the IRI of the MBA class with the given symbol.
    """
    query = f"""
    PREFIX OBO: <http://purl.obolibrary.org/obo/>
    SELECT ?entity
    WHERE {{
        ?entity OBO:IAO_0000028 "{symbol}" .
    }}
    """

    results = get_mba_ontology().query(query)

    for row in results:
        return str(row.entity)

    return None


def is_location_supported(label_symbol: str, mba_symbols: list):
    """
    Checks if the symbol in the label is supported by any of the given mba_symbols.
    """
    if label_symbol in mba_symbols:
        return True
    location_class = get_mba_entity(label_symbol)
    if location_class:
        symbols_values = " ".join(f'"{symbol}"' for symbol in mba_symbols)

        query = f"""
        PREFIX OBO: <http://purl.obolibrary.org/obo/>
        SELECT ?subclass
        WHERE {{
            VALUES ?symbol {{ {symbols_values} }}

            ?class OBO:IAO_0000028 "{label_symbol}" .
            ?subclass OBO:BFO_0000050* ?class;
                      OBO:IAO_0000028 ?symbol .
        }}
        """
        results = get_mba_ontology().query(query)
        return any(results)
    else:
        print("Unknown mba_class: " + label_symbol)

    return True


def get_location_symbols(cell_label: str) -> list:
    """
    Extracts location symbols from the cell_label.
    Assumptions:
        - set of brain regions follows number + space
        - Multiple brain regions are separated by a '-'
    Parameters:
        cell_label: label of the cell
    Returns:
        List of anatomical location symbols (MBA), or empty list if no location exists in the name.
    """
    # remove the heading numbers
    m = re.match("^0*([1-9][0-9]*) (.+)$", cell_label)
    if m:
        formatted_name = m.group(2).strip()
    else:
        formatted_name = cell_label.strip()
    first_part = formatted_name.split(" ")[0]
    if "-" in first_part:
        locations = first_part.split("-")
    else:
        locations = [first_part]
    return locations


def get_mba_ontology():
    global mba_ontology
    if not mba_ontology:
        mba_ontology = Graph()
        mba_ontology.parse(MBAO_PATH, format="xml")
    return mba_ontology