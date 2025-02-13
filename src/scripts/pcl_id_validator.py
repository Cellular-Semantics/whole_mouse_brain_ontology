# This script ensures that current ontology doesn't have IDs clash with the existing ones.

import rdflib
import os


PCL_URL = "http://purl.obolibrary.org/obo/pcl/pcl-base.owl"
WMBO_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../wmbo-base.owl")

common_ids = [
    "http://purl.obolibrary.org/obo/PCL_0000000",
    "http://purl.obolibrary.org/obo/PCL_0010001",
    "http://purl.obolibrary.org/obo/PCL_0010002",
]

def check_pcl_id_conflicts(wmbo_file):
    """
    Checks for ID conflicts between wmbo-base.owl and pcl-base.owl.
    Args:
        wmbo_file: WMBO file path.
    """
    print("Checking for ID conflicts between wmbo-base.owl and pcl-base.owl...")
    wmbo_graph = rdflib.Graph()
    pcl_graph = rdflib.Graph()

    wmbo_graph.parse(wmbo_file, format='xml')
    print("Parsed wmbo-base.owl")
    pcl_graph.parse(PCL_URL, format='xml')
    print("Parsed pcl-base.owl")

    # Extract class and individual IRIs from wmbo-base.owl
    wmbo_iris = set()
    wmbo_classes = set()
    for s in wmbo_graph.subjects(rdflib.RDF.type, rdflib.OWL.Class):
        if str(s).startswith("http://purl.obolibrary.org/obo/PCL_") and str(s) not in common_ids:
            wmbo_iris.add(str(s))
            wmbo_classes.add(str(s))
    for s in wmbo_graph.subjects(rdflib.RDF.type, rdflib.OWL.NamedIndividual):
        if str(s).startswith("http://purl.obolibrary.org/obo/pcl/"):
            wmbo_iris.add(str(s))

    # Extract class and individual IRIs from pcl-base.owl
    pcl_iris = set()
    pcl_classes = set()
    for s in pcl_graph.subjects(rdflib.RDF.type, rdflib.OWL.Class):
        if str(s).startswith("http://purl.obolibrary.org/obo/PCL_") and str(s) not in common_ids:
            pcl_iris.add(str(s))
            pcl_classes.add(str(s))
    for s in pcl_graph.subjects(rdflib.RDF.type, rdflib.OWL.NamedIndividual):
        if str(s).startswith("http://purl.obolibrary.org/obo/pcl/"):
            pcl_iris.add(str(s))

    # Ensure none of the IDs in wmbo-base.owl exist in pcl-base.owl
    conflicting_iris = wmbo_iris.intersection(pcl_iris)
    if conflicting_iris:
        print("The following IRIs are present in both wmbo-base.owl and pcl-base.owl:")
        for iri in conflicting_iris:
            print(iri)
        raise Exception("{} ID conflict detected between wmbo-base.owl and pcl-base.owl.".format(len(conflicting_iris)))
    else:
        print("No common IRIs found between wmbo-base.owl and pcl-base.owl.")

    # Log ID ranges
    log_id_range(wmbo_classes, "WMBO")
    log_id_range(pcl_classes, "PCL")


def extract_id(iri):
    """Extracts the numeric part of the IRI."""
    return int(iri.split('_')[-1])


def log_id_range(iris, label):
    """Logs the smallest ID, biggest ID, and ID range."""
    ids = [extract_id(iri) for iri in iris]
    smallest_id = min(ids)
    biggest_id = max(ids)
    id_range = biggest_id - smallest_id
    print(f"{label} - Smallest ID: {smallest_id}, Biggest ID: {biggest_id}, ID Range: {id_range}")

if __name__ == "__main__":
    check_pcl_id_conflicts(WMBO_FILE)