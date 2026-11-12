"""Select the CCF regions holding a large share of each CCN20230722 subclass and supertype's MERFISH
cells, for 'some soma located in' annotations on their classes.

Reads the Brain Cell KG cache written by kg_location_fetch.py and writes
../dendrograms/supplementary/version2/supertype_subclass_locations.tsv:

  python supertype_subclass_locations.py -c ../dendrograms/supplementary/version2/kg_location_cache \
      -o ../dendrograms/supplementary/version2/supertype_subclass_locations.tsv

A region is kept if it holds at least MIN_RATIO of the cell set's MERFISH cells, pooling Yao et al.
2023 and Zhang et al. 2023 (cells in the region over all cells of the type, so cells outside the
parcellation count against it). Then:
- 'brain', 'Basic cell groups and regions' and 'Brain stem' (which includes the interbrain) are
  dropped as uninformative or misleading;
- a region is dropped if a kept sub-region holds nearly as many cells (within NEAR), so a chain such
  as Cerebral cortex > Cortical plate > Isocortex is reduced to Isocortex;
- branches with no derived soma location (derive_soma_locations.NO_LOCATION) get none.
Cell sets the KG has no counts for get counts summed from their children (as in
derive_soma_locations.py), which slightly undercounts: the KG omits a cluster's minor regions.
Standard library only.
"""
import argparse
import csv

from derive_soma_locations import THETA, Derivation, read_tsv

MIN_RATIO = 0.2
NEAR = 0.05
DROP = {"MBA:997", "MBA:8", "MBA:343"}  # brain, Basic cell groups and regions, Brain stem
LEVELS = {"subclass": 0, "supertype": 1}
SOURCES = ("yao", "zhang")


class Selection:
    def __init__(self, cache):
        self.d = Derivation(cache, THETA)
        self.from_kg = {r["cell_set"] for r in read_tsv(cache, "cell_counts.tsv.gz")}
        self.totals = {r["cell_set"]: {s: int(r[s]) for s in SOURCES if r[s]}
                       for r in read_tsv(cache, "cell_totals.tsv")}

    def total(self, c):
        """Cells per source; summed from children when the KG has none for c."""
        if c in self.from_kg:
            return self.totals.get(c, {})
        t = {}
        for k in self.d.kids[c]:
            for s, n in self.total(k).items():
                t[s] = t.get(s, 0) + n
        return t

    def ratios(self, c):
        t = self.total(c)
        denom = sum(t.values())
        if not denom:
            return {}
        counts = self.d.counts[c]
        regions = {r for s in t for r in counts[s] if r.startswith("MBA:")}
        return {r: sum(counts[s].get(r, 0) for s in t) / denom for r in regions}

    def regions(self, c):
        ratio = self.ratios(c)
        comp = self.d.comp
        keep = {r: x for r, x in ratio.items() if x >= MIN_RATIO and r not in DROP and r in comp}
        return sorted(((r, x) for r, x in keep.items()
                       if not any(comp[b] < comp[r] and y >= x - NEAR for b, y in keep.items())),
                      key=lambda rx: -rx[1])

    def rows(self):
        rows = []
        for c, n in self.d.nodes.items():
            if n["level"] not in LEVELS or self.d.no_location(c):
                continue
            t = self.total(c)
            for r, x in self.regions(c):
                rows.append(dict(
                    cell_set_accession=c.split(":", 1)[1], cell_label=n["label"].split(" CS2023")[0],
                    labelset=n["level"], region=r, region_label=self.d.lab[r], cell_ratio=f"{x:.3f}",
                    **{f"{s}_cells": self.d.counts[c][s].get(r, 0) for s in SOURCES},
                    **{f"{s}_total": t.get(s, 0) for s in SOURCES},
                    counts_from="KG" if c in self.from_kg else "children"))
        rows.sort(key=lambda r: (LEVELS[r["labelset"]], r["cell_set_accession"], -float(r["cell_ratio"])))
        return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-c", "--cache", required=True, help="directory written by kg_location_fetch.py")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    rows = Selection(args.cache).rows()
    with open(args.output, "w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    sets = {(r["labelset"], r["cell_set_accession"]) for r in rows}
    print(f"wrote {args.output}: {len(rows)} rows for {len(sets)} cell sets "
          f"({sum(1 for s in sets if s[0] == 'subclass')} subclasses, {sum(1 for s in sets if s[0] == 'supertype')} supertypes)")


if __name__ == "__main__":
    main()
