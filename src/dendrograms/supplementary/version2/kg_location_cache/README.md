# Brain Cell KG cache for derived soma locations

Inputs of `src/scripts/derive_soma_locations.py`, exported from the
[Brain Cell KG](https://github.com/Cellular-Semantics/Brain_Cell_KG) Neo4j database by
`src/scripts/kg_location_fetch.py`. Caching them means the derivation can be rerun without the KG.

Current export: Brain_Cell_KG `main` at commit
[053320f](https://github.com/Cellular-Semantics/Brain_Cell_KG/commit/053320ff7c6d45f6904d12d9f83124e5cb3c6545)
(2026-10-27), queried on 2026-11-03. `provenance.json` records the commit, query time,
endpoint, the Cypher query for each file and its row count.

| File | Content |
|---|---|
| `nodes.tsv` | CCN20230722 cell sets: accession, label, parent cell set, labelset |
| `cell_counts.tsv.gz` | MERFISH cells per cell set and CCF region (`MBA:`), rolled up the CCF tree; one column per source: `yao` (Yao et al. 2023, https://doi.org/10.1038/s41586-023-06812-z) and `zhang` (Zhang et al. 2023, https://doi.org/10.1038/s41586-023-06808-9) |
| `mba_part_of.tsv` | CCF partonomy |
| `mba_uberon.tsv` | CCF region → Uberon superclasses in the KG (a region can have several, some generic) |
| `mba_labels.tsv` | CCF region labels |

To refresh: build and start the KG at a known commit (see its README), then, in `src/dendrograms`:

```
make kg_location_cache KG_COMMIT=<Brain_Cell_KG commit>
make derived_soma_locations
```

and regenerate the class_base template.
