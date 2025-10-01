#!/usr/bin/env python3
import requests
from pathlib import Path
import os

SHEET_ID = "1LkeHNxWd5eltpbbYzH2aocMpnZjpIS7PpwXFk9d5ggg"

# Tabs (ORDER MATTERS) -> gids
TABS = [
    ("WMBO_CCN20230722_class_curation", "694360783"),
    ("WMBO_one_concept_one_name_curation", "378532656"),
    ("WMBO_CL_ontology_subset", "236037770"),
]

# Provided GitHub paths (same order as TABS)
# If a path ends with a filename, we use its parent folder.
TARGET_PATHS = [
    "src/patterns/data/default",
    "src/dendrograms/supplementary/version2/one_concept_one_name_curation.tsv",
    "src/dendrograms/supplementary/version2/one_concept_one_name_curation.tsv",
]

# Base: repo root (script is in src/, so parents[1] is repo root)
REPO_ROOT = Path(__file__).resolve().parents[1]


def strip_prefix(name: str, prefix: str) -> str:
    pref = prefix + "_"
    return name[len(pref):] if name.startswith(pref) else name


if len(TABS) != len(TARGET_PATHS):
    raise SystemExit("TABS and TARGET_PATHS must be the same length (order-aligned).")

script_dir = os.path.dirname(os.path.realpath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

for (tab_name, gid), rel_target in zip(TABS, TARGET_PATHS):
    # Resolve OUTDIR from repo root + provided path
    target = os.path.join(repo_root, rel_target)
    # If target includes a filename (has a suffix), use its parent dir
    p = Path(target)
    out_dir = p.parent if p.suffix else p
    out_dir.mkdir(parents=True, exist_ok=True)

    # Output filename from tab (strip prefix)
    out_name = strip_prefix(tab_name, "WMBO") or "sheet"
    out_file = out_dir / f"{out_name}.tsv"

    # Download TSV directly
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=tsv&gid={gid}"
    with requests.get(url, timeout=60) as r:
        r.raise_for_status()
        # Normalize line endings to LF
        # (Google often serves CRLF for Excel friendliness)
        text = r.content.decode("utf-8", errors="replace")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        with open(out_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    print(f"Saved {out_file}")
