import argparse
import csv
import glob
import os

PATTERNS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "patterns", "data", "default")


def collect_terms(data_folder):
    """
    Collects terms from TSV files in the specified folder that match the cl subset prefixes.
    Args:
        data_folder: DOSDP patterns data folder path.

    Returns: The set of terms that match the cl subset prefixes.
    """
    prefixes = (
        "http://purl.obolibrary.org/obo/CL_",
        "http://purl.obolibrary.org/obo/CLM_",
    )
    tsv_files = glob.glob(os.path.join(data_folder, "*.tsv"))

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
        except Exception as e:
            print(f"Error reading '{file}': {e}")

    return terms


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


def main():
    """
    This script processes TSV files in the dosdp patterns folder to create a CL subset seed file.
    """
    parser = argparse.ArgumentParser(
        description="Process TSV files to collect cl subset terms seed."
    )
    parser.add_argument("-o", "--output", required=True, help="Path of the output file to write the terms.")
    args = parser.parse_args()

    terms = collect_terms(PATTERNS_FOLDER)
    create_seed_file(args.output, terms)


if __name__ == "__main__":
    main()