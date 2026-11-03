# derived_soma_locations.tsv

Soma location of each CCN20230722 cell set, derived from MERFISH cell counts (Yao et al.
2023, https://doi.org/10.1038/s41586-023-06812-z; Zhang et al. 2023,
https://doi.org/10.1038/s41586-023-06808-9) registered to the Allen CCF and rolled up the
CCF partonomy. The build (`generate_base_class_template`) writes `location` for CL-subset
terms only:

- cell sets in a class flagged `Neuronal` in the taxonomy: `Derived_location` column, giving
  `SubClassOf has_soma_location some <location>`;
- other (non-neuronal) cell sets: `Derived_part_of` column, giving
  `SubClassOf part_of some <location>`, because `has_soma_location` has domain neuron.

A curated `Locations` value in the class curation table replaces either
(`merge_class_templates`).

How a location is chosen:

- Per MERFISH source, the most specific grey-matter region holding at least `theta` (0.8) of
  the cell set's cells in grey matter (`Basic cell groups and regions`, MBA:8). The two sources are
  combined by taking the most specific region containing both picks. Sources with fewer
  than 20 cells are skipped.
- The top of the CCF tree is aligned with Uberon. CCF `Brain stem` includes the interbrain,
  unlike Uberon `brainstem`, so it isn't used. Three regions are added, with counts summed
  from their parts: forebrain (Cerebrum + Interbrain), brainstem (Midbrain + Hindbrain, counted as
  Brain stem minus Interbrain because some cells are only registered at Brain stem level)
  and hindbrain (Hindbrain + Cerebellum), mapped to Uberon `forebrain`, `brainstem` and
  `hindbrain`. In the table (`ccf_region`) these virtual regions have IDs `V:forebrain`,
  `V:brainstem` and `V:hindbrain`.
- The region is mapped to Uberon. Where a region maps to several Uberon classes, the one whose
  label matches the region's is used, otherwise the most specific (the one fewest CCF regions
  map to), so thalamic and hypothalamic nuclei don't get generic classes such as `brainstem
  nucleus`. A region with no mapping takes its nearest mapped CCF ancestor's. Two CCF mappings
  are overridden: `Olfactory areas` → `olfactory lobe` (the CCF region includes the main
  olfactory bulb, which isn't part of `olfactory cortex`), and `Pallidum` → `pallidum`.
- The CL product asserts the taxonomy hierarchy, so a restriction is inherited by every
  descendant term. When a descendant cell set (at least 50 cells) has under half of its
  cells in the region, the location **moves up** to the most specific region that holds at
  least half of the cells of every such descendant (`note` says so). For example, class
  `28 CB GABA` gets hindbrain rather than cerebellum, because its `308 DCO Il22 Gly-Gaba`
  subclass is mostly in the cochlear nuclei. If only grey matter would do, or the region
  isn't grey matter, no location is given (`note` says why).
- The pineal cell set (class `25 Pineal Glut` and its chain) gets no location: spatial
  registration of pinealocytes isn't reliable.

The table is generated outside the main build by `src/scripts/derive_soma_locations.py`
(`make derived_soma_locations` in `src/dendrograms`) from a cached export of the
[Brain Cell KG](https://github.com/Cellular-Semantics/Brain_Cell_KG): cell counts per cell set
and CCF region, the CCF partonomy and CCF → Uberon mappings. The cache, the Cypher queries and
the KG commit they ran against are in `kg_location_cache/` (see its README). Regenerate the
table, and then the class_base template, when the method, the taxonomy or the cell counts
change.

Shared neurotransmitters (`Shared_NT`) need no table: the build computes them from the
cluster neurotransmitter calls in the taxonomy (the NT shared by every cluster with a call).
