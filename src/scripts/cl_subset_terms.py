import argparse
import csv
import glob
import os
import yaml

from rdflib import Graph

PATTERNS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "patterns", "data", "default")

GENE_COLUMNS = ["NT_marker_1", "NT_marker_2", "NT_marker_3", "NT_marker_4", "NT_marker_5", "NT_marker_6", "NT_marker_7", "NT_marker_8", "Markers"]
PREFIXES_YAML = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ontology/template_prefixes.yaml")

def collect_classes(data_folder, collect_genes=False):
    """
    Collects terms from TSV files in the specified folder that match the cl subset prefixes.
    Args:
        data_folder: DOSDP patterns data folder path.
        collect_genes: If True, also collects gene terms from specified columns.

    Returns: The set of terms that match the cl subset prefixes.
    """
    prefixes = (
        "http://purl.obolibrary.org/obo/CL_",
        "http://purl.obolibrary.org/obo/CLM_",
    )
    tsv_files = glob.glob(os.path.join(data_folder, "*.tsv"))
    template_prefixes = get_template_prefixes(PREFIXES_YAML)

    terms = set()
    for file in tsv_files:
        try:
            with open(file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                if "defined_class" not in reader.fieldnames:
                    continue
                for row in reader:
                    defined_class = row.get("defined_class", "")
                    if any(defined_class.startswith(prefix) for prefix in prefixes):
                        terms.add(defined_class)
                        if collect_genes:
                            for col in GENE_COLUMNS:
                                #  collect gene terms and expand curies
                                for gene in row.get(col, "").split("|"):
                                    if ":" in gene:
                                        prefix, local_id = gene.split(":", 1)
                                        url = template_prefixes.get(prefix)
                                        if url:
                                            terms.add(f"{url}{local_id}")
                                        else:
                                            terms.add(gene)
                                    else:
                                        terms.add(gene)

        except Exception as e:
            print(f"Error reading '{file}': {e}")

    return terms

def get_template_prefixes(prefixes_yaml):
    with open(prefixes_yaml, 'r', encoding='utf-8') as f:
        prefix_dict = yaml.safe_load(f)
    return prefix_dict

def create_seed_file(output_path, terms):
    """
    Creates a seed file with the collected terms.
    Args:
        output_path: Path to the output file where terms will be written.
        terms: Seed terms

    Returns: None
    """
    try:
        with open(output_path, "w", encoding="utf-8") as out_file:
            for term in sorted(terms):
                out_file.write(f"{term}\n")
        print(f"Successfully wrote {len(terms)} terms to {output_path}")
    except Exception as e:
        print(f"Error writing to output file '{output_path}': {e}")


def collect_individuals(ontology_path, class_seed_path):
    """
    Collects individual terms from the ontology that are instances of classes in the class seed file.
    It uses a single SPARQL query with UNION to match patterns and restricts ?s
    to IRIs in the class seed terms.

    Args:
        ontology_path: Path to the ontology file.
        class_seed_path: Path to the class seed file.

    Returns:
        A sorted list of unique individual terms.
    """
    g = Graph()
    g.parse(ontology_path,)

    # Load class seed terms
    with open(class_seed_path, "r", encoding="utf-8") as f:
        class_terms = {line.strip() for line in f if line.strip()}

    values_clause = ""
    if class_terms:
        values_clause = "VALUES ?s { " + " ".join(f"<{term}>" for term in class_terms) + " }"

    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT ?value WHERE {{
      {values_clause}
      {{
        ?s rdfs:subClassOf ?restriction .
        ?restriction owl:onProperty <http://purl.obolibrary.org/obo/RO_0015001> ;
                     owl:hasValue ?value .
        FILTER(STRSTARTS(STR(?value), "https://purl.brain-bican.org/taxonomy/CCN20230722/"))
      }} UNION {{
        ?s owl:equivalentClass ?equiv .
        ?equiv owl:intersectionOf ?list .
        ?list rdf:rest*/rdf:first ?item .
        ?item owl:onProperty <http://purl.obolibrary.org/obo/RO_0015001> ;
               owl:hasValue ?value .
        FILTER(STRSTARTS(STR(?value), "https://purl.brain-bican.org/taxonomy/CCN20230722/"))
      }}
    }}
    """
    individuals_set = set()
    for row in g.query(query):
        individuals_set.add(str(row.value))

    individuals = sorted(individuals_set)
    return individuals


def trim_dangling_individuals(ontology_path, indv_seed_path, output_path):
    g = Graph()
    g.parse(ontology_path,)

    # Load class seed terms
    with open(indv_seed_path, "r", encoding="utf-8") as f:
        indv_terms = {line.strip() for line in f if line.strip()}

    filter_clause = ""
    if indv_terms:
        filter_clause =  ", ".join(f"<{term}>" for term in indv_terms)

    query = f"""
        PREFIX RO: <http://purl.obolibrary.org/obo/RO_>
        DELETE {{
          ?s RO:0015003 ?value .
          ?value ?p ?o .
        }}
        WHERE {{
          ?s RO:0015003 ?value .
          ?value ?p ?o .
          FILTER(STRSTARTS(STR(?value), "https://purl.brain-bican.org/taxonomy/CCN20230722/"))
          FILTER(?value NOT IN ({filter_clause}))
        }} ;
    
    """
    g.update(query)
    g.serialize(destination=output_path, format="xml")


def main():
    """
    This script processes TSV files in the dosdp patterns folder to create a CL subset seed file.
    """
    parser = argparse.ArgumentParser(
        description="Process TSV files to collect cl subset terms seed."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # class terms command
    classes_parser = subparsers.add_parser("classes", help="Extract class terms from TSV files")
    classes_parser.add_argument("-o", "--output", required=True, help="Path of the output file to write the terms.")
    # individual terms command
    individuals_parser = subparsers.add_parser("individuals", help="Extract individual terms from TSV files")
    individuals_parser.add_argument("-i", "--input", required=True, help="Input ontology path.")
    individuals_parser.add_argument("-c", "--classes", required=True, help="CL subset classes seed file path.")
    individuals_parser.add_argument("-o", "--output", required=True, help="Path of the output file to write the terms.")
    # individual trimming command
    individuals_parser = subparsers.add_parser("trim_indvs",
                                               help="Trim dandling subclusterOf relations where tha parent is not in the indv seed file.")
    individuals_parser.add_argument("-i", "--input", required=True, help="Input ontology path.")
    individuals_parser.add_argument("-t", "--terms", required=True,
                                    help="CL subset individual seed file path.")
    individuals_parser.add_argument("-o", "--output", required=True,
                                    help="Path of the output file to write the trimmed ontology.")


    args = parser.parse_args()

    if args.command == "classes":
        terms = collect_classes(PATTERNS_FOLDER, collect_genes=True)
        create_seed_file(args.output, terms)
    elif args.command == "individuals":
        terms = collect_individuals(args.input, args.classes)
        create_seed_file(args.output, terms)
    elif args.command == "trim_indvs":
        trim_dangling_individuals(args.input, args.terms, args.output)
    else:
        raise ValueError("Unknown command. Use 'classes' or 'individuals'.")


if __name__ == "__main__":
    main()