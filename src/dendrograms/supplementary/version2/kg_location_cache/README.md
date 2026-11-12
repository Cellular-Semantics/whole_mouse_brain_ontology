# Brain Cell KG cache for derived soma locations

Inputs of `src/scripts/derive_soma_locations.py`, exported from the
[Brain Cell KG](https://github.com/Cellular-Semantics/Brain_Cell_KG) Neo4j database by
`src/scripts/kg_location_fetch.py`. Caching them means the derivation can be rerun without the KG.
The CCF → Uberon mapping isn't cached: the derivation reads the bridge axioms
(`MBA_n ≡ UBERON_m ⊓ part_of some mouse`) from `src/dendrograms/resources/mbao-base-materialized.owl`.
The KG's `SUBCLASSOF` edges are the reasoned hierarchy, which also gives regions generic Uberon
superclasses (e.g. `brainstem nucleus` for thalamic nuclei, via the mbao bridge `Brain stem ≡ brainstem`).

Current export: Brain_Cell_KG `main` at commit
[9a224d1](https://github.com/Cellular-Semantics/Brain_Cell_KG/commit/9a224d1822a5f0e1d04c80db3049b715dd38ef81)
(2026-11-11), queried on 2026-11-11. `provenance.json` records the commit, query time,
endpoint, the Cypher query for each file and its row count.

The KG stores each edge's per-source values as lists with duplicates removed, so where Yao and
Zhang have the same count the list has one value; `kg_location_fetch.py` gives it to both sources.

| File | Content |
|---|---|
| `nodes.tsv` | CCN20230722 cell sets: accession, label, parent cell set, labelset |
| `cell_counts.tsv.gz` | MERFISH cells per cell set and CCF region (`MBA:`), rolled up the CCF tree; one column per source: `yao` (Yao et al. 2023, https://doi.org/10.1038/s41586-023-06812-z) and `zhang` (Zhang et al. 2023, https://doi.org/10.1038/s41586-023-06808-9) |
| `cell_totals.tsv` | MERFISH cells per cell set and source (from the `brain` row: count / cell ratio), the denominator for cell ratios |
| `mba_part_of.tsv` | CCF partonomy |
| `mba_labels.tsv` | CCF region labels |

To refresh: build and start the KG at a known commit (see its README), then, in `src/dendrograms`:

```
make kg_location_cache KG_COMMIT=<Brain_Cell_KG commit>
make derived_soma_locations
```

and regenerate the class_base template.
