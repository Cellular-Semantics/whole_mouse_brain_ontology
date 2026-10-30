# derived_soma_locations.tsv

Soma location of each CCN20230722 cell set, derived from MERFISH cell counts (Yao et al.
2023, https://doi.org/10.1038/s41586-023-06812-z; Zhang et al. 2023,
https://doi.org/10.1038/s41586-023-06808-9) registered to the Allen CCF and rolled up the
CCF partonomy. The build (`generate_base_class_template`) writes `location` to the
`Derived_location` column for CL-subset terms only, giving
`SubClassOf has_soma_location some <location>`. A curated `Locations` value in the class
curation table replaces it (`merge_class_templates`).

How a location is chosen:

- Per MERFISH source, the deepest CCF region holding at least `theta` (0.8) of the cell
  set's cells in grey matter (`Basic cell groups and regions`, MBA:8). The two sources are
  combined by taking their nearest common CCF ancestor. Sources with fewer than 20 cells
  are skipped.
- The CCF region is mapped to Uberon. Two mappings are overridden: `Olfactory areas` →
  `olfactory lobe` (the CCF region includes the main olfactory bulb, which isn't part of
  `olfactory cortex`), and `Pallidum` → `pallidum`.
- The CL product asserts the taxonomy hierarchy, so a restriction is inherited by every
  descendant term. The location is therefore **withheld** (column `withheld`) when any
  descendant with at least 50 cells has under half of its cells in the region, e.g. class
  `28 CB GABA`, whose `308 DCO Il22 Gly-Gaba` subclass is mostly in the cochlear nuclei. It
  is also withheld when the region isn't grey matter.

The table is generated outside the build, from the knowledge-graph export of cell counts
per cell set and CCF region (`location_derivation/export_wmbo_locations.py` in the
Whole_mouse_brain_collection workspace). Regenerate it when the taxonomy or the cell counts
change.

Shared neurotransmitters (`Shared_NT`) need no table: the build computes them from the
cluster neurotransmitter calls in the taxonomy (the NT shared by every cluster with a call).
