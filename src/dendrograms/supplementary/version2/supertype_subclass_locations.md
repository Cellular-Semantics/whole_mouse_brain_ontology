# Supertype and subclass soma locations (`supertype_subclass_locations.tsv`)

The CCF regions that hold a large share of each CCN20230722 subclass and supertype's MERFISH cells.
The class template turns each row into a `some soma located in` (`CLM:0010001`) annotation on the
cell set's class. The annotation carries `cell ratio` (`CLM:0010002`), a comment and the assay
(spatial transcriptomics, `EFO:0008992`). These annotations are the same kind clusters get
from the CCF frequencies in Yao et al.'s cluster annotation table. They are annotations, not
logical axioms, so they don't affect classification. The single logical soma location of
CL-subset terms comes from `derived_soma_locations.tsv` (see `derived_soma_locations.md`).

## Method

From the cached Brain Cell KG export (`kg_location_cache/`): MERFISH cells per cell set and CCF
region, including CCF regions that are only rollups of painted regions, from Yao et al. 2023
and Zhang et al. 2023.

- **Cell ratio:** cells in the region divided by all cells of the type, with the two datasets
  pooled. Cells outside the parcellation count in the denominator.
- **Threshold:** a region is kept if it holds at least 20% of the cells. Cells only near a region
  (the KG's 100 µm band) don't count.
- **Excluded regions:** `brain`, `Basic cell groups and regions` and `Brain stem` are dropped.
  The first two say nothing. CCF `Brain stem` includes the interbrain, and mbao maps it to Uberon
  `brainstem`, which doesn't.
- **Near-duplicate parents:** a region is dropped if a kept sub-region holds nearly as many cells
  (within 0.05). For example, a cell set with 99% of its cells in Isocortex isn't also annotated
  with Cerebral cortex and Cortical plate. A region that holds clearly more than any of its kept
  sub-regions stays: L2/3 IT CTX Glut gets Isocortex, Somatomotor areas and Somatosensory areas.
- **Skipped branches:** branches with no derived soma location get none. These are the pineal
  class, and the subclasses lining the ventricles (`derive_soma_locations.NO_LOCATION`).
- **Missing KG data:** the KG has no counts for some cell sets
  ([Brain_Cell_KG#14](https://github.com/Cellular-Semantics/Brain_Cell_KG/issues/14)). For these,
  counts and totals are summed from their child cell sets (`counts_from` = `children`). That
  slightly undercounts, because the KG omits each cluster's minor regions. Brain Cell KG 9a224d1
  fixed the missing counts, so no rows use this fallback now.

The result is 3 to 4 regions per cell set on average, at most 7.

## Which classes get them

- **Supertypes and subclasses:** each gets its own rows.
- **Collapsed chains:** a chain of single-child nodes becomes one class. When the chain ends in
  a cluster, the class keeps the cluster's annotations and these rows aren't used.

## Columns

- `cell_set_accession`, `cell_label`, `labelset`: the cell set.
- `region`, `region_label`: the CCF region.
- `cell_ratio`: pooled share of the cell set's cells in the region.
- `yao_cells`, `zhang_cells`, `yao_total`, `zhang_total`: the counts behind the ratio.
- `counts_from`: `KG`, or `children` when the counts were summed from child cell sets.

## Regenerating

The table is generated outside the main build, by `src/scripts/supertype_subclass_locations.py`.
`make derived_soma_locations` in `src/dendrograms` writes it together with
`derived_soma_locations.tsv`. Regenerate the class_base template afterwards.
