# Testing the coordinated CL, WMB taxonomy and WMBO edits (plan)

Status as of 2026-11-03. Companion to `wmbo_location_nt_classification_plan.md`.

*2026-11-12: done. The test was run with WMBO #134 and #136 (both now merged) and CL #3841; results are in the status section of `wmbo_location_nt_classification_plan.md`. Kept as a record of the method. The taxonomy risk below was real: the export fails on CL:0020088/89 until a CL release containing them reaches SemSQL.*

## Goal

Test the combined effect of the open CL, taxonomy and WMBO changes on how
CL-promoted WMBO terms classify under CL's region × neurotransmitter grouping
classes, before anything else is merged or released.

## Where each repo is

### CL (obophenotype/cell-ontology)

Merged to master: the brain region × NT grouping classes (#3797, for #3788) and
the cerebellum-like structure grouping classes (#3828).

Open:

| PR | Change | State |
|---|---|---|
| #3801 | Region-free MGE/CGE/LGE-derived GABAergic neuron classes (#3789), with `has soma location some forebrain` | Master merged in on 2026-11-02; no conflicts; awaiting review |
| #3831 | `sst chodl GABAergic interneuron` soma location → telencephalon; parent → CL:4023063, so no longer inferred under cortical `sst` | No conflicts; awaiting review |
| #3832 | 12 more region × NT grouping classes: forebrain, telencephalon, diencephalon, thalamus, pallidum, amygdala, hindbrain GABA; 5-HT, NA, HA groupings | Conflicts with master and with #3801 (only `Declaration` ordering) |

Temporary IDs: #3801 uses CL_9900000–02 and #3832 uses CL_9900040–51, so they
don't clash with each other.

CL still imports `wmbo-cl-comp` from 2026-09-15 (130 terms). WMBO main
(v2026-10-16, 406 terms) is not in CL yet; that needs a CL import refresh.

Not blocking a test, but open: correcting the #3790 epic (sst chodl and
Lamp5 Lhx6 as siblings of sst and lamp5; no expression-only `EquivalentClasses`
on T-type classes) and #3739 / #2721 (Lamp5 Lhx6 inferred under lamp5 and CGE).

### WMB taxonomy (brain-bican/whole_mouse_brain_taxonomy)

- **#28** remaps classes 28 CB GABA and 29 CB Glut to `cerebellum-like
  structure GABAergic/glutamatergic neuron` (CL:0020088 / CL:0020089). No
  conflicts; not reviewed.
- Merging to `main` triggers `export_from_tsv.yml`, which regenerates
  `CCN20230722.json`.
- **Risk:** the export looks CL terms up in SemSQL `cl.db`, last built on
  2026-09-26, which predates CL:0020088/89. The export may fail or produce a JSON
  without labels for them. How `tdta` handles unknown IDs hasn't been checked.

### WMBO (Cellular-Semantics/whole_mouse_brain_ontology)

- **#134**: derived soma locations and shared neurotransmitters. 3 commits, no
  conflicts. A full `make` has not been run.
  - Withheld locations now move up a level: classes 28/29 and the DCO subclasses
    get hindbrain, and the cerebellar subclasses get cerebellum.
- **Classes 28/29 `Locations` removal** (curated MBA:512, which overrides the
  derived location and puts cerebellum on the DCO subclasses) is uncommitted in
  the `wmbo-derived-soma-location-nt` worktree.
- **Step 4 of the classification plan (fix the cl-comp build) is not started.**
  Without it, about 160 promoted neurons reach CL with no CL parent.
- `docs/wmbo_location_nt_classification_plan.md` and
  `docs/uberon_ntr_cerebellum_like_structure.md` are untracked in the main
  checkout.
- The Google Sheet curation route is deprecated; `CCN20230722_class_curation.tsv`
  in the repo is the source of truth.

## Current evidence

The coverage figures in #3832 come from modelling the template tables against
CL with ELK, not from a built ontology. Of 337 promoted neuronal terms, the
number reaching a grouping class:

| | Count |
|---|---|
| Today | 83 |
| With WMBO #134, on CL master | 299 |
| With WMBO #134 and CL #3832 | 327 |

## Local end-to-end test

Nothing needs to be merged or released for this.

1. **Combined CL branch (small).** A local worktree with master + #3801 + #3831
   + #3832, with the `Declaration` conflicts resolved. Don't push it.
2. **Taxonomy change (small).** Either regenerate `CCN20230722.json` from the
   #28 branch with `tdta` / `cas-tools`, or patch the two class mappings into a
   local copy. Point the WMBO dendrogram build at that file instead of
   downloading it from `main`.
3. **WMBO build (medium; needs Docker).** In the #134 worktree, with the 28/29
   curation change: `src/dendrograms` `make all` (Python), then ODK `make` to
   produce `wmbo-cl-comp.owl`. Docker Desktop is installed but not running, and
   `dosdp-tools` isn't installed locally.
4. **cl-comp fix (medium; new work).** Implement plan step 4: before removing PCL
   classes, give each CL term its nearest non-PCL ancestors from the reasoned
   hierarchy (SPARQL update, then reduce). Do it in the WMBO Makefile, or as a
   test-only step first. Without it the test reports about 160 parentless
   promoted neurons and hides the real classification result.
5. **Swap and reason (small).** In the combined CL KB, remove axioms about
   CL-product terms from CL's old WMBO component, merge in the new
   `wmbo-cl-comp`, load into Owlery and run the plan's step 8 checks:
   - no unsatisfiable classes;
   - every `CL:430…` term has a CL parent;
   - share of terms under a region × NT class, overall and by level;
   - spot checks: olfactory bulb, claustrum/amygdala, cerebellar nuclei, DCO.

Steps 1, 2 and 5 can be done now, with the current WMBO main component as a
baseline. Step 3 needs Docker running. Step 4 changes the WMBO build and needs
agreement on the approach.

## Tooling

`owlery/` (`build.sh`, `start.sh`) plus a one-off component swap script, as used
for the earlier `cl-preview-wmbo-v2026-10-16` KB. `cl-uberon-workbench/` could
host this later, but it doesn't handle WMBO yet (it needs an `unmerge:` part
option).

## After the test

- Review and merge CL #3801, #3831, #3832 (renumber temporary IDs if needed).
- Merge taxonomy #28 once the CL release containing CL:0020088/89 is in SemSQL.
- Merge WMBO #134 with the 28/29 curation change and the cl-comp fix; release.
- CL import refresh to pull the new `wmbo-cl-comp`.
