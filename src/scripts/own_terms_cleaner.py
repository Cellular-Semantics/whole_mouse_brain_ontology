# python
#!/usr/bin/env python3

# This script removes lines from a DOSDPT-generated .txt file that match terms defined in the sibling .tsv file's "defined_class" column.
# The reason for this is ODK uses these txt files to generate import modules. Sometimes a CL term is declared in our dosdp tables (wmbo-cl-component), but we are accidentally importing these terms from CL as well.
import argparse
from pathlib import Path
import sys

import pandas as pd

INDV_URL = "https://purl.brain-bican.org/ontology/CCN20230722/"

CURRENT_DIR = Path(__file__).resolve().parent
OWN_CLASSES_TSV = (CURRENT_DIR.parent / "patterns" / "data" / "default" / "CCN20230722_class_base.tsv").resolve()
INDIVIDUALS_TSV = (CURRENT_DIR.parent / "templates" / "CCN20230722.tsv").resolve()

def load_own_terms(tsv_path: Path):
    if not tsv_path.exists():
        print(f"Error: TSV file not found: {tsv_path}", file=sys.stderr)
        sys.exit(1)
    try:
        df = pd.read_csv(tsv_path, sep="\t", dtype=str)
    except Exception as e:
        print(f"Error reading TSV {tsv_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine column name of the first column
    try:
        col_name = df.columns[0]
    except Exception:
        print(f"Error: TSV {tsv_path} does not have column index {0}", file=sys.stderr)
        sys.exit(1)

    terms = df[col_name].dropna().astype(str).unique().tolist()
    own_terms = set()
    for term in terms:
        own_term = term.strip()
        if own_term.startswith("BICAN_INDV:"):
            own_term = own_term.replace("BICAN_INDV:", INDV_URL)
        own_terms.add(own_term)
    return own_terms


def save_txt(txt_path: Path, own_terms: set):
    """Write the own_terms to txt_path, one term per line.

    - Ensures parent directories exist.
    - Writes terms in sorted order to make output deterministic.
    - Exits with an error message on failure.
    """
    if not isinstance(txt_path, Path):
        txt_path = Path(txt_path)

    try:
        txt_path.parent.mkdir(parents=True, exist_ok=True)
        with txt_path.open("w", encoding="utf-8") as fh:
            for term in sorted(own_terms):
                fh.write(f"{term}\n")
    except Exception as e:
        print(f"Error writing TXT {txt_path}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Saves this ontology sourced terms to the given file.")
    parser.add_argument("--output", "-o", required=True, help="Path to the .txt file to save")
    args = parser.parse_args()

    txt_path = Path(args.output)
    if txt_path.suffix.lower() != ".txt":
        print("Error: output must be a .txt file", file=sys.stderr)
        sys.exit(1)

    own_terms_class = load_own_terms(OWN_CLASSES_TSV)
    own_terms_individual = load_own_terms(INDIVIDUALS_TSV)
    own_terms = own_terms_class.union(own_terms_individual)

    save_txt(txt_path, own_terms)


if __name__ == "__main__":
    main()
