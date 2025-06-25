import sys
import argparse
import rdflib

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

if __name__ == "__main__":
    main()