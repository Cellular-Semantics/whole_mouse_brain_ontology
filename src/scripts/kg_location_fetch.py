"""Cache the inputs of derive_soma_locations.py from a Brain Cell KG Neo4j instance (all but the
CCF -> Uberon bridge, which it reads from mbao).

Brain Cell KG: https://github.com/Cellular-Semantics/Brain_Cell_KG. Run it locally
(docker compose) at a known commit and pass that commit with --kg-commit, so the cache records
which KG build it came from:

  python kg_location_fetch.py --kg-commit <sha> -o ../dendrograms/supplementary/version2/kg_location_cache

Writes one TSV per query (cell counts gzipped) plus provenance.json (KG commit, query time,
endpoint, the Cypher queries and row counts). Uses the Neo4j HTTP API; standard library only.
"""
import argparse
import csv
import datetime
import gzip
import io
import json
import os
import urllib.request

YAO = "https://doi.org/10.1038/s41586-023-06812-z"
ZHANG = "https://doi.org/10.1038/s41586-023-06808-9"

# name: (file, header, Cypher). Rows are written in the column order of the RETURN clause.
QUERIES = {
    "nodes": ("nodes.tsv", ["cell_set", "label", "parent", "labelset"], """
MATCH (i:Individual) WHERE i.curie STARTS WITH 'WMB:CS20230722_'
OPTIONAL MATCH (i)-[:subcluster_of]->(p)
OPTIONAL MATCH (i)-[:has_labelset]->(ls)
RETURN i.curie, i.label, p.curie, ls.curie ORDER BY i.curie"""),
    # MERFISH cell counts per cell set and CCF region, rolled up the CCF tree; one count per source
    "cell_counts": ("cell_counts.tsv.gz", ["cell_set", "region", "yao", "zhang"], """
MATCH (i:Individual)-[r:obsolete_some_soma_located_in]->(l) WHERE i.curie STARTS WITH 'WMB:CS20230722_'
RETURN i.curie, l.curie, r.source, r.cell_count ORDER BY i.curie, l.curie"""),
    "mba_part_of": ("mba_part_of.tsv", ["region", "parent"], """
MATCH (a)-[:part_of]->(b) WHERE a.curie STARTS WITH 'MBA:' AND b.curie STARTS WITH 'MBA:'
RETURN a.curie, b.curie ORDER BY a.curie, b.curie"""),
    "mba_labels": ("mba_labels.tsv", ["region", "label"], """
MATCH (a) WHERE a.curie STARTS WITH 'MBA:'
RETURN a.curie, a.label ORDER BY a.curie"""),
}


def cypher(endpoint, query):
    body = json.dumps({"statements": [{"statement": query}]}).encode()
    req = urllib.request.Request(endpoint, body, {"Content-Type": "application/json"})
    res = json.load(urllib.request.urlopen(req, timeout=600))
    if res["errors"]:
        raise SystemExit(res["errors"])
    return [d["row"] for d in res["results"][0]["data"]]


def to_row(name, row):
    if name == "cell_counts":
        cell_set, region, sources, counts = row
        by_source = dict(zip(sources, counts))
        unknown = set(by_source) - {YAO, ZHANG}
        if unknown:
            raise SystemExit(f"Unexpected cell count source(s): {unknown}")
        return [cell_set, region, by_source.get(YAO, ""), by_source.get(ZHANG, "")]
    return ["" if v is None else v for v in row]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kg-commit", required=True, help="Brain_Cell_KG commit the running KG was built from")
    ap.add_argument("--endpoint", default="http://localhost:7474/db/neo4j/tx/commit")
    ap.add_argument("-o", "--outdir", required=True)
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    provenance = {
        "source": "https://github.com/Cellular-Semantics/Brain_Cell_KG",
        "kg_commit": args.kg_commit,
        "queried_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endpoint": args.endpoint,
        "cell_count_sources": {"yao": YAO, "zhang": ZHANG},
        "queries": {},
    }
    for name, (fn, header, query) in QUERIES.items():
        rows = [to_row(name, r) for r in cypher(args.endpoint, query)]
        path = os.path.join(args.outdir, fn)
        # mtime=0 so an unchanged export gives an identical file
        f = (io.TextIOWrapper(gzip.GzipFile(path, "wb", mtime=0), newline="") if fn.endswith(".gz")
             else open(path, "w", newline=""))
        with f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(header)
            w.writerows(rows)
        provenance["queries"][name] = {"file": fn, "rows": len(rows), "cypher": query.strip()}
        print(f"{fn}: {len(rows)} rows")
    with open(os.path.join(args.outdir, "provenance.json"), "w") as f:
        json.dump(provenance, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
