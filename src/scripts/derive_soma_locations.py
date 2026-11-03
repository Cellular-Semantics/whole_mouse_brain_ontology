"""Derive the soma location of each CCN20230722 cell set from MERFISH cell counts.

Reads the Brain Cell KG cache written by kg_location_fetch.py (cell counts, CCF partonomy and
labels) and the CCF -> Uberon bridge in mbao, and writes the table the template build reads
(derived_soma_locations.tsv). The method is described in
../dendrograms/supplementary/version2/derived_soma_locations.md:

  python derive_soma_locations.py -c ../dendrograms/supplementary/version2/kg_location_cache \
      -o ../dendrograms/supplementary/version2/derived_soma_locations.tsv

Per MERFISH source, a cell set's own region is the most specific grey-matter region holding at
least THETA of its grey-matter cells; the two sources are combined by taking the most specific
region containing both picks. The restriction is inherited by every descendant term, so when a
descendant lies mostly outside that region the location moves up (location_for). Standard
library only.
"""
import argparse
import collections
import csv
import functools
import gzip
import os
import xml.etree.ElementTree as ET

THETA = 0.8
MIN_CELLS = 20  # sources with fewer grey-matter cells than this are skipped
MIN_FLAG = 50   # descendants with fewer cells than this don't move a location up
MIN_IN = 0.5    # a descendant fits a region holding at least this share of its cells
GREY = "MBA:8"  # Basic cell groups and regions: excludes fibre tracts and ventricles
UNINFORMATIVE = {"MBA:8", "MBA:997", None}  # grey matter, root
LEVELS = {"class": 0, "subclass": 1, "supertype": 2, "cluster": 3}
SOURCES = ("yao", "zhang")
MBAO = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/resources/mbao-base-materialized.owl")

# The CCF tree doesn't match Uberon at the top: its 'Brain stem' includes the interbrain and it
# has no forebrain. Drop 'Brain stem' and add the Uberon groupings as virtual (V:) regions, with
# counts summed from their parts.
EXCLUDE = {"MBA:343"}  # Brain stem
VIRTUAL = {  # region: (label, added, subtracted, Uberon)
    "V:forebrain": ("forebrain (Cerebrum + Interbrain)", ["MBA:567", "MBA:1129"], [],
                    ("UBERON:0001890", "forebrain")),
    # Brain stem - Interbrain rather than Midbrain + Hindbrain: some cells are only registered at
    # Brain stem level
    "V:brainstem": ("brainstem (Midbrain + Hindbrain)", ["MBA:343"], ["MBA:1129"],
                    ("UBERON:0002298", "brainstem")),
    "V:hindbrain": ("hindbrain (Hindbrain + Cerebellum)", ["MBA:1065", "MBA:512"], [],
                    ("UBERON:0002028", "hindbrain")),
}
# MBA regions whose mbao bridge is wrong for this use
UBERON_OVERRIDE = {
    "MBA:698": ("UBERON:0005366", "olfactory lobe"),  # Olfactory areas includes MOB/AOB; 'olfactory cortex' doesn't
}
# Cell sets (and their descendants) whose soma location shouldn't come from registered MERFISH cells
NO_LOCATION = {"WMB:CS20230722_CLAS_25": "pinealocytes: location from spatial registration is unreliable"}


def read_tsv(cache, fn):
    path = os.path.join(cache, fn)
    with (gzip.open(path, "rt") if fn.endswith(".gz") else open(path)) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_mbao_bridge(path):
    """{MBA region: (Uberon ID, label)} from mbao's bridge axioms,
    MBA_n EquivalentTo UBERON_m and (part_of some NCBITaxon_10090).

    Read from the axioms rather than from the reasoned hierarchy (e.g. the KG's SUBCLASSOF
    edges), where regions also get generic Uberon superclasses such as 'brainstem nucleus'."""
    ns = {"owl": "http://www.w3.org/2002/07/owl#", "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
          "rdfs": "http://www.w3.org/2000/01/rdf-schema#", "skos": "http://www.w3.org/2004/02/skos/core#"}
    about = f"{{{ns['rdf']}}}about"
    curie = lambda iri: iri.rsplit("/", 1)[-1].replace("_", ":", 1)
    labels, bridge = {}, {}
    for c in ET.parse(path).getroot().findall("owl:Class", ns):
        iri = c.get(about, "")
        if "/obo/UBERON_" in iri:
            label = c.find("rdfs:label", ns)
            label = c.find("skos:prefLabel", ns) if label is None else label
            if label is not None:
                labels[curie(iri)] = label.text
        elif "/mbao/MBA_" in iri:
            us = [d.get(about) for d in c.findall("owl:equivalentClass/owl:Class/owl:intersectionOf/rdf:Description", ns)
                  if "/obo/UBERON_" in d.get(about, "")]
            if len(us) > 1:
                raise SystemExit(f"{curie(iri)} has more than one Uberon bridge: {us}")
            if us:
                bridge[curie(iri)] = curie(us[0])
    return {m: (u, labels.get(u, "")) for m, u in bridge.items()}


class Derivation:
    def __init__(self, cache, theta, mbao=MBAO):
        self.theta = theta
        self.lab = {r["region"]: r["label"] for r in read_tsv(cache, "mba_labels.tsv")}
        parent = {}
        for r in read_tsv(cache, "mba_part_of.tsv"):
            if parent.setdefault(r["region"], r["parent"]) != r["parent"]:
                raise SystemExit(f"{r['region']} has more than one CCF parent")
        self.uberon = read_mbao_bridge(mbao)

        children = collections.defaultdict(set)
        for a, b in parent.items():
            children[b].add(a)

        def below(r):
            out = {r}
            for k in children[r]:
                out |= below(k)
            return out
        self.comp = {r: frozenset(below(r)) for r in self.lab}
        for v, (label, plus, minus, uberon) in VIRTUAL.items():
            self.lab[v] = label
            self.uberon[v] = uberon
            self.comp[v] = (frozenset().union(*(self.comp[p] for p in plus))
                            - frozenset().union(*(self.comp[m] for m in minus)))
        self.regions = sorted((r for r in self.comp if r not in EXCLUDE), key=lambda a: len(self.comp[a]))

        self.nodes, self.kids = {}, collections.defaultdict(set)
        for r in read_tsv(cache, "nodes.tsv"):
            self.nodes[r["cell_set"]] = dict(label=r["label"], parent=r["parent"],
                                             level=r["labelset"].split(":")[-1])
            if r["parent"]:
                self.kids[r["parent"]].add(r["cell_set"])
        # Counts in the KB are already rolled up the CCF tree
        self.counts = collections.defaultdict(lambda: collections.defaultdict(dict))
        for r in read_tsv(cache, "cell_counts.tsv.gz"):
            for s in SOURCES:
                if r[s]:
                    self.counts[r["cell_set"]][s][r["region"]] = int(r[s])
        for c in list(self.nodes):
            self._fill(c)
        for c in list(self.nodes):
            for regs in self.counts[c].values():
                for v, (_, plus, minus, _) in VIRTUAL.items():
                    regs[v] = sum(regs.get(p, 0) for p in plus) - sum(regs.get(m, 0) for m in minus)
        self.own = {c: self._direct(c) for c in self.nodes}
        self.cells = {c: sum(regs.get(GREY, 0) for regs in self.counts[c].values()) for c in self.nodes}

    def _fill(self, c):
        """Counts of a cell set without its own, summed from its children."""
        if self.counts.get(c):
            return self.counts[c]
        agg = collections.defaultdict(lambda: collections.defaultdict(int))
        for k in self.kids[c]:
            for src, regs in self._fill(k).items():
                for r, n in regs.items():
                    agg[src][r] += n
        self.counts[c] = agg
        return agg

    @functools.lru_cache(maxsize=None)
    def chain(self, r):
        """r and the regions containing it, most specific first."""
        return [a for a in self.regions if self.comp[r] <= self.comp[a]]

    def mrca(self, rs):
        rs = [r for r in rs if r]
        if not rs:
            return None
        common = set(self.chain(rs[0]))
        for r in rs[1:]:
            common &= set(self.chain(r))
        return min(common, key=lambda x: len(self.comp[x])) if common else None

    def _direct(self, c):
        """The cell set's own region: per source, the most specific grey-matter region holding at
        least theta of its grey-matter cells; sources combined by MRCA."""
        picks = []
        for regs in self.counts[c].values():
            d = regs.get(GREY, 0)
            if d < MIN_CELLS:
                continue
            ok = [r for r, n in regs.items()
                  if r in self.comp and r not in EXCLUDE and GREY in self.chain(r) and n / d >= self.theta]
            if ok:
                picks.append(min(ok, key=lambda r: len(self.comp[r])))
        return self.mrca(picks)

    def frac_in(self, d, r):
        return sum(regs.get(r, 0) for regs in self.counts[d].values()) / self.cells[d] if self.cells[d] else 0

    def anc(self, c):
        p = self.nodes[c]["parent"]
        return [p] + self.anc(p) if p in self.nodes else []

    def desc(self, c):
        return [d for k in self.kids[c] for d in [k] + self.desc(k)]

    def outside(self, c):
        """Highest descendants (>= MIN_FLAG cells) with under MIN_IN of their cells in c's own region."""
        o = self.own[c]
        if o in UNINFORMATIVE:
            return []
        out = [d for d in self.desc(c) if self.cells[d] >= MIN_FLAG and self.frac_in(d, o) < MIN_IN]
        s = set(out)
        return [d for d in out if not any(a in s for a in self.anc(d))]

    def to_uberon(self, r):
        if r in UBERON_OVERRIDE:
            return UBERON_OVERRIDE[r]
        # Walk up the CCF tree if the region has no Uberon mapping of its own
        return next((self.uberon[a] for a in (self.chain(r) if r else []) if a in self.uberon), None)

    def location_for(self, c):
        """(uberon, label, note, region) for a cell set's soma location. uberon is empty when the
        location is withheld, and note says why; region is the (CCF or virtual) region used. When a
        descendant lies mostly outside the cell set's own region, the location moves up to the most
        specific region that holds at least MIN_IN of every such descendant's cells."""
        o = self.own[c]
        if o in UNINFORMATIVE:
            return "", "", "", ""
        if GREY not in self.chain(o):
            return "", "", f"{self.lab.get(o)} is not grey matter", ""
        note = ""
        out = self.outside(c)
        if out:
            up = next((a for a in self.chain(o) if all(self.frac_in(d, a) >= MIN_IN for d in out)), None)
            if up is None or up in UNINFORMATIVE:
                return "", "", f"descendant(s) mostly outside {self.lab.get(o)}, no region below grey matter holds them", ""
            note = f"moved up from {self.lab.get(o)}: descendant(s) mostly outside it"
            o = up
        m = self.to_uberon(o)
        if not m:
            return "", "", f"no Uberon mapping for {self.lab.get(o)}", ""
        return m[0], m[1], note, o

    def no_location(self, c):
        return next((why for a in [c] + self.anc(c) for x, why in NO_LOCATION.items() if a == x), "")

    def comment(self, c, used):
        region = self.lab.get(used) + ("" if used.startswith("V:") else f" ({used})")
        share = f"At least {self.theta:.0%} of this cell set's MERFISH cells in grey matter"
        refs = "(Yao et al. 2023; Zhang et al. 2023)"
        if used == self.own[c]:
            return f"{share} {refs} are in {region}."
        return (f"{share} {refs} are in {self.lab.get(self.own[c])}; the broader {region} is used because it "
                f"also holds at least half of the cells of each of its descendant cell sets.")

    def rows(self, theta_label):
        rows = []
        for c, n in self.nodes.items():
            if n["level"] not in LEVELS:
                continue
            o = self.own[c]
            u, ul, note, used = self.location_for(c)
            if self.no_location(c):
                u, ul, note, used = "", "", self.no_location(c), ""
            region = used or (o if o not in UNINFORMATIVE else "")
            rows.append(dict(
                cell_set_accession=c.split(":", 1)[1], cell_label=n["label"].split(" CS2023")[0],
                labelset=n["level"], location=u, location_label=ul,
                ccf_region=region, ccf_region_label=self.lab.get(region, "") if region else "",
                note=note, theta=theta_label, merfish_cells=self.cells[c],
                comment=self.comment(c, used) if u else ""))
        rows.sort(key=lambda r: (LEVELS[r["labelset"]], r["cell_set_accession"]))
        return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-c", "--cache", required=True, help="directory written by kg_location_fetch.py")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--mbao", default=MBAO, help="mbao OWL (RDF/XML) holding the CCF -> Uberon bridge")
    ap.add_argument("--theta", default=str(THETA))
    args = ap.parse_args()

    rows = Derivation(args.cache, float(args.theta), args.mbao).rows(args.theta)
    with open(args.output, "w") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {args.output}: {len(rows)} rows, {sum(bool(r['location']) for r in rows)} with a location, "
          f"{sum(bool(r['note']) and not r['location'] for r in rows)} withheld, "
          f"{sum(bool(r['note']) and bool(r['location']) for r in rows)} moved up")


if __name__ == "__main__":
    main()
