"""Release check: every WMBO-minted ID in the previous release must still be generated (live or
deprecated) by the new templates. Guards against IDs silently disappearing (issue #129).

WMBO-minted IDs are PCL:01xxxxx, CL:430xxxx and CLM:50xxxxx (the ranges allocated by the ID
factories; CL:431xxxx etc. are other CL terms referenced by WMBO). The previous release is read from an
OBO file (e.g. the committed wmbo-base.obo before it is regenerated); the new IDs are the
`defined_class` values of the class base, class obsolete and marker-set templates.

Usage:
    python check_release_ids.py --previous ../../wmbo-base.obo --templates ../patterns/data/default
Exit status 1 if any previously released ID is missing.
"""

import argparse
import csv
import glob
import os
import re
import sys

WMBO_ID = re.compile(r"^(PCL:01\d{5}|CL:430\d{4}|CLM:50\d{5})$")
OBO_PREFIX = "http://purl.obolibrary.org/obo/"


def previous_ids(obo_path):
    ids, current, obsolete = {}, None, set()
    with open(obo_path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line == "[Term]":
                current = None
            elif line.startswith("id: "):
                current = line[4:].strip()
                if WMBO_ID.match(current):
                    ids[current] = ""
            elif line.startswith("name: ") and current in ids:
                ids[current] = line[6:]
            elif line == "is_obsolete: true" and current in ids:
                obsolete.add(current)
    return ids, obsolete


def template_ids(template_dir):
    ids = {}
    for path in sorted(glob.glob(os.path.join(template_dir, "*.tsv"))):
        with open(path, newline="") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                iri = row.get("defined_class", "")
                if iri.startswith(OBO_PREFIX):
                    ids[iri[len(OBO_PREFIX):].replace("_", ":", 1)] = os.path.basename(path)
    return ids


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--previous", required=True, help="previous release OBO (e.g. wmbo-base.obo)")
    ap.add_argument("--templates", required=True, help="directory with the generated *_class_base.tsv etc.")
    args = ap.parse_args()

    prev, prev_obsolete = previous_ids(args.previous)
    new = template_ids(args.templates)
    missing = sorted(set(prev) - set(new))
    print(f"previous release: {len(prev)} WMBO IDs ({len(prev_obsolete)} obsolete); "
          f"new templates: {len(new)} IDs; missing: {len(missing)}")
    for i in missing:
        print(f"  MISSING {i} {'(obsolete) ' if i in prev_obsolete else ''}{prev[i]}")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
