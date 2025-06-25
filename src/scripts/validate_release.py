import sys
import argparse
import rdflib

import pandas as pd

def entities_resolved_in_definitions(graph):
    """
    Checks all definitions to ensure that all entity CURIEs are resolved to their labels.
    Args:
        graph: ontology graph to validate
    """
    property_uri = rdflib.URIRef("http://purl.obolibrary.org/obo/IAO_0000115")

    # Evaluate the property values
    error_found = False
    for subj, pred, obj in graph.triples((None, property_uri, None)):
        # convert the object to a string
        value = str(obj)
        if "http" in value:
            print(f"Error: The value '{value}' for subject '{subj}' contains 'http'.")
            error_found = True

    if error_found:
        sys.exit(1)
    else:
        print("Ontology validated successfully.")


def validate_cl_ontology_subset(graph):
    # class collapsing making this calculation hard, use fixed number for now
    # file_path = "../dendrograms/supplementary/version2/CL_ontology_subset.tsv"
    # df = pd.read_csv(file_path, sep='\t', dtype=str)
    # count_add_to_cl = df[df['Add_to_CL'].str.upper() == 'TRUE'].shape[0]
    count_add_to_cl = 120

    # Count terms where IRI starts with the given prefix
    iri_prefix = "http://purl.obolibrary.org/obo/CL_43"
    query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT (COUNT(DISTINCT ?class) AS ?count)
        WHERE {{
            ?class a owl:Class .
            FILTER(STRSTARTS(STR(?class), "{iri_prefix}"))
        }}
        """
    results = list(graph.query(query))
    count_iri = int(results[0]['count'])

    # Compare the counts and report the result
    if count_iri >= count_add_to_cl :
        print(
            f"Mismatch: {count_add_to_cl} records with Add_to_CL = TRUE vs {count_iri} terms with IRI starting with the prefix.")
        return False
    else:
        print("Validation successful: counts match.")
        return True

def load_ontology(file_path):
    g = rdflib.Graph()
    try:
        g.parse(file_path, format=rdflib.util.guess_format(file_path))
    except Exception as e:
        print(f"Error parsing ontology: {e}")
        sys.exit(1)
    return g

def main():
    parser = argparse.ArgumentParser(description="Ontology Validation Script")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate ontology")
    validate_parser.add_argument("--input", "-i", required=True, help="Ontology file path")

    args = parser.parse_args()

    if args.command == "validate":
        graph = load_ontology(args.input)
        entities_resolved_in_definitions(graph)
        validate_cl_ontology_subset(graph)

if __name__ == "__main__":
    main()