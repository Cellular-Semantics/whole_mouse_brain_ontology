# WMBv2-informed CL promotion for WMBO (draft plan)

## Context

WMBO is built from WMBv1 (CCN20230722, Yao 2023). By default its terms get PCL IDs (`PCL_01…`). A small curated subset is promoted to CL IDs (`CL_43…`); today that is 145 `Add_to_CL=TRUE` rows, which become 130 CL terms after singleton-chain collapse.

The promotion choices so far have been informal. The only record of them is free-text notes such as "Name holds true", "Major BG class" and "Adding all CB neurons to supertype level".

WMBv2 (CCN20251031) is a consensus of WMBv1 and the Broad/Macosko snRNA atlas. Its repo contains two things we can use:
- a v1→v2 mapping based on shared-cell F1;
- a per-node stability assessment that also checks each node against the Broad clustering, which is independent of v1.

**Goal:** use that evidence to choose, defensibly, which v1 types to promote to CL. For each promoted term:
1. make sure it is classified under a suitable, specific CL parent;
2. add its v2 name as a synonym.

The WMBO build otherwise stays as it is: same v1 source, same ID factories, same templates.

### Decisions already made
- **Already-promoted terms (130 CL IDs):** these are never demoted. Any that fail the stability criteria are listed in the report for curator review.
- **v2 name:** added as `oboInOwl:hasRelatedSynonym`, with an axiom-annotation `hasDbXref` pointing to the CCN20251031 accession. This needs one new column in the DOSDP pattern.
- **Scope:** a term must be both stable and CL-classifiable.
  - Subclass and supertype are the main targets.
  - Clusters are included only when triangulated, i.e. confirmed in Broad as well as v1 (tier S1 below).
  - Classes are excluded by default. A class is considered only if a curator marks it as easy to define and useful as a grouping class.
- **Conservative first pass:** only 1:1 matches count; splits and merges are ignored. Stability is judged on independent Broad reproduction, not v1→v2 F1 alone (see *Stability scoring*).
- **First release: clusters need a stable parent** (agreed 2026-09-29). A cluster stays in only if its v1 supertype or subclass is also in the promotion set.
  - This leaves **457 terms**: 88 subclasses, 210 supertypes and 159 clusters (158 kept by the rule, plus 1 already in CL that has no promoted parent).
  - Classification then needs about 169 anchors (88 subclasses, 81 supertypes). The 23 clusters whose supertype isn't promoted are classified directly under their promoted subclass.
- **Neurotransmitter consistency is handled in naming, not selection.** Terms aren't dropped for NT mismatches; unsupported NT mentions are removed from the final name instead. See `docs/wmbo_cl_naming_plan.md`.
- **Naming happens after promotion and CL mapping, before release.** Every CL-promoted term gets a full `defined_class_name` override. See `docs/wmbo_cl_naming_plan.md`.
- **CL parents:** gaps are filled by searching CL through the OLS4 MCP; a curator approves each choice (Step 1b).

## Inputs (all present locally)

`<T>` = `WMBv2/target/whole_mouse_brain_consensus_taxonomy/`

| Input | Path | Use |
|---|---|---|
| v1→v2 best match per level | `<T>/v1_to_v2_mapping/{class,subclass,supertype,cluster}_map_full.csv` (`v1_acc, best_v2, best_v2_name, f1, recall, precision_shared, …`) | per-v1-node F1, and the v2 name for the synonym |
| v2 stability | `<T>/stability/{cluster,supertype,subclass}_stability.tsv` (cluster: `composite`, `tier`; roll-ups: `composite`, `frac_clusters_triangulated`, `frac_clusters_broad_confirmed`) | whether the v2 match is independently reproduced |
| v2 CL mappings | `<T>/cl_mapping/cl_transfer_applied.csv`, `<T>/curation_tables/annotation.tsv` (`cell_ontology_term_id`) | suggested CL parents, including any new ones assigned in v2 |
| v2 hierarchy | `WMBv2/WMB_v2_cas.json` (`parent_cell_set_accession`) | checking the hierarchy is preserved |
| v1 taxonomy + CL mappings | `whole_mouse_brain_ontology/src/dendrograms/CCN20230722.json` (sourced from the taxonomy repo's `curation_tables/annotation.tsv`) | the current CL parent of each node or its nearest ancestor |
| Current promotion list | `whole_mouse_brain_ontology/src/dendrograms/supplementary/version2/CL_ontology_subset.tsv` (`cell_set_accession, cell_label, Add_to_CL, Notes`) | baseline |

**Sheet sync:** the promotion list, `class_curation.tsv` and the taxonomy's `annotation.tsv` are all pulled from Google Sheet `1LkeHNxWd5eltpbbYzH2aocMpnZjpIS7PpwXFk9d5ggg` (`google_sheets_to_tsv.py`). Curation edits therefore have to go into the sheet, not the local TSVs. The assessment output is prepared for pasting or uploading into the sheet.

## Stability scoring: a conservative selection

**Approach.** For now we accept only 1:1 matches and don't model splits or merges. A v1 node qualifies on stability only if:
- its best v2 match reproduces it (the gate), and
- that v2 node is independently reproduced in the Broad/Macosko snRNA atlas.

v1→v2 F1 on its own is not enough. About 97% of **v1 cells** are carried into v2, and v2 kept the AIBS clustering strategy. The v1→v2 F1 is computed over those shared v1 cells only, so it mostly shows that integration didn't break the type. It is not independent evidence. Broad/Macosko snRNA nuclei are a large share of v2: `macosko_frac` has a median of about 0.46 per cluster. The Broad comparison is the independent evidence (different lab, assay and clustering pipeline), so it is what separates "stable" from "not contradicted".

### Gate (all levels)
- v1→v2 `f1` ≥ 0.8 (from `v1_to_v2_mapping/*_map_full.csv`).
- Reciprocal: the v2 node's own best-v1 F1 (`v1_f1` in `stability/*.tsv`) equals the v1→v2 F1 to within 0.01. In the current data this holds for every F1 ≥ 0.8 match. It stays in as a guard against future mapping revisions.
- The v1 parent's best v2 match is the v2 parent of `best_v2` (hierarchy preserved).

### Evidence tiers
Each gated node gets a tier.

**Clusters** (Broad is tested natively at cluster level):

| Tier | Rule | v1 clusters (of which already promoted) |
|---|---|---|
| **S1: promote** | `tier = A_triangulated` (Broad recall_loose ≥ 0.8 **and** strict F1 ≥ 0.8) **and** `broad_tested_cells` ≥ 50, so the Broad weight in `composite` is 1 | 210 (5) |
| S2: review | `A_triangulated_loose`, or `A_triangulated` with fewer than 50 Broad cells | 263 (3) |
| S3: not contradicted, untested | `C_v1_only_untestable` (< 20 Broad cells) | not promoted on stability alone |
| exclude | `B_partial_broad`, `D_broad_discordant`, `E_weak_v1` | |

An even stricter cut, `composite` ≥ 0.9 with ≥ 50 Broad cells, gives 136.

**Supertypes and subclasses.** Broad has no native levels here, so the evidence is rolled up from the node's v2 clusters.

The shipped roll-up columns can't be used as they are:
- `frac_clusters_broad_confirmed` isn't normalised to `n_broad_testable`. Converted to "confirmed ÷ testable" it exceeds 1 for many nodes (e.g. Microglia, OPC, Astro-NT). The "confirmed" and "testable" definitions evidently use different cell thresholds.
- The roll-up `composite` silently falls back to `v1_f1` when nothing is testable (56 subclasses, 336 supertypes).

So we **recompute the roll-up** from `cluster_stability.tsv`, using the v2 parent links in `WMB_v2_cas.json`. For each v2 supertype or subclass:
- `broad_coverage` = fraction of the node's **cells** in Broad-testable clusters (`broad_tested_cells` ≥ 20). Weighting by cells stops a few tiny untestable clusters from sinking a well-covered node.
- `broad_support` = cell-weighted mean of `broad_recall_loose` over the testable clusters.
- `broad_discordant_frac` = fraction of cells in clusters with `broad_recall_loose` < 0.5.

| Tier | Rule |
|---|---|
| **S1: promote** | gate passed, `broad_coverage` ≥ 0.5, `broad_support` ≥ 0.8, `broad_discordant_frac` ≤ 0.1 |
| S2: review | gate passed, `broad_coverage` ≥ 0.5, `broad_support` 0.6–0.8 |
| S3: not contradicted, untested | gate passed, `broad_coverage` < 0.5 |
| exclude | anything else |

**Rough size from the shipped roll-ups.** Using F1 ≥ 0.8, coverage ≥ 0.5 and confirmed-rate ≥ 0.8, a first pass gives about 177 supertypes (21 already promoted) and 67 subclasses (12 already promoted). The recomputed cell-weighted numbers will differ. They are expected to be more generous to large non-neuronal subclasses, whose many small v2 clusters pull down cluster counts.

**Known weakness.** A containment test built up from clusters under-rates coarse types that Broad itself splits differently (glia, ependymal, choroid plexus). Several already-promoted non-neuronal subclasses fail the current roll-up even though the types are well established: Astro-NT, OPC, Microglia, VLMC, ABC, Hypendymal, CHOR and OEC. Two things follow.
- **Optional native test (later).** Take the Broad cells in a v2 subclass or supertype and ask whether a *union* of Broad clusters covers the node with F1 ≥ 0.8. This needs the consensus cell-to-cluster membership from ABC, which isn't in the repo. The Broad metadata is local in `WMBv2/Macosco_data/`.
- **Curator review of S3 nodes.** Treat S3 as "stable but untested". They are promotable only with extra evidence: an established CL type, literature, or spatial evidence, recorded in `Notes`.

**Classes.** No stability file exists at class level. A class needs the gate plus its subclasses mostly at S1 or S2 (≥ 50% of cells). It is only a curator-nominated grouping candidate.

### Lineage rule
- A supertype promoted at S1 whose parent subclass is not promoted is flagged. We may want the subclass as a grouping class, or a direct CL parent.
- A cluster promoted without a promoted supertype or subclass above it is allowed. It must still pass the CL-classification check.

## Step 1: Assessment script (new, read-only analysis)

**Status (2026-09-29): implemented, stability part only.** The script lives in the WMBv2 consensus repo as `whole_mouse_brain_consensus_taxonomy/cl_promotion/build_promotion_set.py`, alongside `stability/` and `v1_to_v2_mapping/`. It writes `promotion_assessment.tsv`, `proposed_promotion_set.tsv`, `proposed_promotion_tree.md` and `summary.md`; see that folder's README. CL classifiability (item 5) and Step 1b come later. Their results will update the v1 `annotation` table and WMBO's `CL_ontology_subset.tsv`.

*Original design:* It uses pandas plus OAK/pronto against `cl.obo` (already available through the ODK imports or `mirror/`).

The script builds one row for each v1 node (class, subclass, supertype, cluster) with the following fields.

1. **Mapping.** `best_v2`, `best_v2_name`, `f1`, `recall`, `precision`, and the reverse `v1_f1` for the reciprocity check. Splits and merges are not modelled.
2. **Hierarchy preserved.** True if the v1 parent's `best_v2` equals the v2 parent of `best_v2`, using the parent links in the CAS json.
3. **Stability evidence.**
   - Clusters: `tier`, `composite`, `broad_tested_cells`, `broad_recall_loose`, `broad_f1_strict`, `macosko_frac`.
   - Supertypes and subclasses: the recomputed `broad_coverage`, `broad_support` and `broad_discordant_frac`, alongside the shipped roll-ups for comparison.
4. **`stability_tier`.** S1, S2, S3 or exclude, as defined in the section above. Thresholds are CLI flags, and the report includes a sensitivity table.
5. **CL classifiability (automated part).**
   - `cl_parent`: the nearest `cell_ontology_term_id` on the node or an ancestor. This mirrors `get_gross_cell_type()` in `src/scripts/template_generation_utils.py`, so the script should import that function rather than reimplement it.
   - `cl_parent_source`: `self` or `ancestor:<acc>`.
   - Generic parents are flagged. Examples: `CL:0000000`, `CL:0000540` neuron, `CL:0000617` GABAergic neuron, `CL:0000679` glutamatergic neuron, `CL:0000125` glial cell. The flag also fires when the depth in CL is below a threshold.
   - `v2_cl_suggestion`: the CL term assigned to `best_v2` in v2's `annotation.tsv` or `cl_transfer_applied.csv`, if it differs from the v1 term or is more specific.
   - Resulting `cl_status`:
     - `ok`: a specific parent exists.
     - `needs_mapping`: a suitable CL term exists but has to be added in the taxonomy sheet.
     - `needs_NTR`: no suitable CL term exists, so a new term request goes to the CL tracker.
6. **Current state.** Whether the node is already `Add_to_CL`, and the existing notes.
7. **`recommendation`.**
   - `promote`: S1 and `cl_status=ok`.
   - `promote_after_mapping`: S1, but the CL mapping or NTR has to happen first.
   - `review`: S2, or S3 with supporting evidence.
   - `keep_existing_flag_review`: already promoted but not S1.
   - `no`.
   - Collapsed singleton chains are resolved with the existing `get_collapsed_nodes()`, so each recommendation attaches to the node that will actually be minted. The chain's tier is its **weakest** member.

**Outputs:**
- `wmbv2_promotion_candidates.tsv`: every row above.
- `cl_lookup_queue.tsv`: the S1/S2 nodes whose `cl_status` is not `ok`. This is the input to Step 1b.
- `wmbv2_promotion_report.md`:
  - counts by level, tier and recommendation;
  - existing CL terms that fail the criteria;
  - new candidates;
  - the list of CL mappings and NTRs needed;
  - the threshold sensitivity table.

## Step 1b: Finding CL parents with the OLS4 MCP (agent-assisted, curator-approved)

For each row in `cl_lookup_queue.tsv`, use the OLS4 MCP tools, restricted to `ontology=cl`, to find the most specific existing CL term the type can go under.

1. **Build queries from the taxonomy.** Draw on:
   - the neurotransmitter (`Glut`, `GABA`, `Gly-Gaba`, `Chol`, `Dopa`, `Sero`, …);
   - region tokens (`STR`, `CB`, `HY`, `MB`, …), expanded to anatomy names;
   - marker genes in the v1 and v2 labels (e.g. `Sst`, `Pvalb`, `Car3`);
   - cell-class words (astrocyte, tanycyte, …).
2. **Search CL.** Match on labels and exact synonyms. For each hit, retrieve its ancestors, and its definition and logical axioms where available (e.g. `has soma location`, `capable of`, `has neurotransmitter`), so candidates can be checked for consistency with the type.
3. **Rank and filter candidates.**
   - Prefer terms with **mouse-applicable, transcriptomic or anatomical** definitions.
   - Reject species-restricted terms (e.g. human-only) and terms whose soma location or neurotransmitter disagrees with the type.
   - Record the depth in CL, and whether the candidate is a descendant of the current `cl_parent`. It should be more specific than the current parent, not a sibling.
   - Also look for **already-existing `CL:43…` WMBO terms** and `CL:40…` BICAN/CAP terms, to avoid duplicating a promotion.
4. **Output `cl_candidates.tsv`.** One row per node, with up to 3 candidates:
   - columns `CL_id, label, match_basis, ancestors_ok, species_ok, confidence`;
   - `match_basis` is one of `label | synonym | definition | axiom`;
   - `confidence` is high, medium or low.
   - A curator makes the final choice.
5. **Where accepted choices go.**
   - A mapping on the node itself goes in the taxonomy `annotation` sheet: `cell_ontology_term_id`, `rationale` (cite the OLS match basis), `rationale_dois`. Use this only where the node *is* that CL type.
   - Otherwise it goes in the WMBO `Classification` column (with `Classification_comment`), where the node is a *subtype* of the CL term. This avoids asserting equivalence in the published taxonomy.
   - Nodes with no acceptable candidate become `needs_NTR`. A short NTR draft (label, parent, definition, markers, location, v1 and v2 accessions) goes in `ntr_drafts.md`.

**Reproducibility.** The OLS queries and the returned term IDs are logged with the CL release version that OLS reports, so the lookup can be re-run and diffed against later CL releases.

## Step 2: Curation (in the Google Sheet)

1. Add these columns to the `WMBO_CL_ontology_subset` tab: `v2_accession, v2_label, f1, stability_tier, broad_support, cl_status, recommendation`.
   - `get_cl_subset_nodes()` in `src/scripts/template_generation_tools.py` reads only `Add_to_CL`, so extra columns are harmless.
2. A curator sets `Add_to_CL=TRUE` for the accepted candidates. The `Notes` column records the basis, e.g. `WMBv2 stable (F1=0.93, A_triangulated)`.
3. CL parents:
   - For `needs_mapping`, add `cell_ontology_term_id`, `rationale` and `rationale_dois` in the taxonomy `annotation` tab. The taxonomy CI then regenerates `CCN20230722.json`.
   - Use the class-curation `Classification` column only as an override.
   - `needs_NTR` terms go to the CL issue tracker. They wait for the new term before being promoted, or are promoted under the best available parent with a comment.
4. For each newly promoted term, fill `defined_class_name` and, where possible, `defined_class_definition` in `WMBO_CCN20230722_class_curation`, as was done for the existing promoted terms. Classes considered as grouping classes need a definition before they are accepted.

## Step 3: Pipeline changes (minimal)

1. **Mapping table for the build.** Commit `src/dendrograms/supplementary/version3/v1_v2_mapping.tsv` with columns `cell_set_accession, v2_accession, v2_label, f1`, taken from the Step 1 output.
2. **Base template.** In `generate_base_class_template` (`src/scripts/template_generation_tools.py`), load that table. For nodes in the CL subset only, emit two new columns:
   - `WMBv2_synonym` (the v2 label);
   - `WMBv2_xref` (`CCN20251031:CS20251031_…`, or whatever CURIE form the taxonomy RDF uses for accessions).
3. **DOSDP pattern.** In `src/patterns/dosdp-patterns/taxonomy_class.yaml`:
   - add a `hasRelatedSynonym: oboInOwl:hasRelatedSynonym` annotation property;
   - add the two new vars to `data_vars`;
   - add an annotation block that emits the related synonym with a nested `hasDbXref` axiom annotation. This follows the existing nested-annotation pattern used for `oboInOwl:evidence` on the `CL` subClassOf.
4. **Checks on the rest of the build.**
   - `wmbo-cl-comp` filters with `--select "annotations anonymous self"`, so the new annotations should carry through. This needs to be checked.
   - IDs are unaffected: the `CLIdFactory`/`PCLIdFactory` ranges depend only on v1 node counts, and new promotions get an obsolete PCL twin automatically.
   - The script should assert that newly minted `CL_43…` IDs don't collide with existing CL terms. `Claude_analysis_reports/cl_module_generation_critical_report.md` flags this as a risk.

## Step 4: Documentation

- This document is `docs/wmbv2_cl_promotion.md`. Once the plan is agreed, add it to the `mkdocs.yaml` nav.
- Update the `CL_ontology_subset` section of `docs/wmbo_workflow.md` with the formal criteria.

## Verification

1. Run the Step 1 script and check the report against the input files.
   - Row counts per level should be 34, 338, 1,201 and 5,322.
   - The F1 bands should reproduce the README counts: subclass 268/41/29, and so on.
   - Spot-check a few mappings, e.g. `CS20230722_SUBC_318` Astro-NT and `CS20230722_CLAS_28` CB GABA.
2. Rebuild with `cd src/dendrograms && make all` (skip `sheets` if working offline), then run the release in `src/ontology` via `sh run.sh make prepare_release`.
3. Checks on the new `wmbo-cl-comp.obo` against the current release:
   - Count of `CL:43` terms = 130 + the number of newly accepted terms.
   - No existing CL ID is missing.
   - Every CL term has an `is_a` to a CL term that is not in the generic list.
   - Every newly promoted term has `synonym: "<v2 label>" RELATED [CCN20251031:…]`.
   - Every new promotion has an obsolete PCL twin in `wmbo-base`.
4. Run `robot reason` / `robot report` on `wmbo-cl-comp.owl` to confirm there are no unsatisfiable classes and no new ERROR-level report items.

## Open points for review

### Stability criteria
1. **S1 thresholds.**
   - Clusters: `A_triangulated` with ≥ 50 Broad cells gives 210 clusters. Or the stricter `composite` ≥ 0.9, which gives 136?
   - Supertypes and subclasses: cell-weighted `broad_coverage` ≥ 0.5 and `broad_support` ≥ 0.8. Confirm these once the recomputed roll-up is available. The report will include a sensitivity table.
2. **Is the roll-up test fair to coarse types?** Rolling up containment from clusters under-rates types that Broad splits differently, such as glia, ependymal cells and choroid plexus. Should we run the native union-of-Broad-clusters test? It needs the consensus cell-to-cluster membership downloaded from ABC.
3. **S3 (not contradicted, untested in Broad).** 362 clusters, plus supertypes and subclasses with low snRNA coverage. Should they be excluded outright for this release, or promotable with recorded external evidence?
4. **Broad-discordant nodes** (`D_broad_discordant`, n = 79 clusters). These are excluded. Should an already-promoted term in this tier get anything stronger than a review flag?
5. **Splits and merges.** Out of scope for this conservative pass. Revisit later, e.g. a v1 type that splits cleanly into several S1 v2 types could be a grouping class.
6. **Hierarchy preservation.** It is currently part of the gate, so a term fails if its v1 parent maps to a different v2 parent. Keep it as a hard requirement or relax it to a flag?
7. **Classes.** No class-level stability file exists. The draft rule is the gate plus ≥ 50% of cells in S1/S2 subclasses, then curator nomination. Which classes are the candidate grouping classes?
8. **Collapsed singleton chains.** The draft takes the weakest member's tier. Agree?
9. **Already promoted terms that fail.** From the shipped roll-ups, about 5 of 76 promoted clusters, 20 of 37 supertypes and 10 of 26 subclasses meet the strictest cut. Most of the failures are glial or cerebellar types that were promoted on prior-knowledge grounds. Keeping them as they are and adding a review flag is the current decision. Should the `Notes` column also record why each is retained?

### CL classification
10. **Generic parents.** Which CL terms count as "too generic"? The draft list is `CL:0000000`, neuron, GABAergic neuron, glutamatergic neuron and glial cell, plus a minimum depth in CL. Should a region-plus-neurotransmitter parent such as `cerebellar neuron` count as suitable?
11. **No suitable CL term.** Should the promotion wait for a new CL term request (NTR) to be accepted, or go ahead under the best available parent with a comment? Who submits the NTRs, and should they be batched?
12. **Parents suggested by v2.** Where the v2 CL mapping is more specific than or different from v1, adopt it automatically (added to the v1 annotation sheet with the same rationale) or only after curator review?
13. **Where CL mappings are written.** The draft (Step 1b) splits them. When the node *is* the CL type, the mapping goes in the taxonomy `annotation` sheet, which changes the published CCN20230722. When the node is a subtype, it goes in the WMBO `Classification` column, which changes only the ontology. Is that split right?
14. **Names and definitions.** Existing promoted terms have curated `defined_class_name` values, but only 4 have a curated definition. Should a curated definition be required for every new promotion, or is the auto-generated one ("A … of the … brain") acceptable?

### v2 synonym
15. **Synonym format.** v2 labels carry a numeric prefix and underscores, e.g. `0141 CLA-EPd-CTX_Car3_Glut 3`. Keep the label verbatim, strip the number, or both?
16. **Which terms get the synonym.** Only promoted terms, as in the draft, or every WMBO term that has a good v2 match (F1 ≥ 0.8)? The second is cheap and would help users navigate from v2, but it touches the PCL content.
17. **Cross-reference form.** Which CURIE should point to the v2 node: `CCN20251031:CS20251031_…`, or the accession IRI used in the taxonomy RDF? Check the prefix is registered in the ontology's prefix map.
18. **Several v1 terms, one v2 node.** When more than one v1 term matches the same v2 node, the same related synonym lands on each of them. Is that acceptable, or should the synonym be added only for 1:1 matches?

### Process and build
19. **Sheet workflow.** Should the assessment columns go into the existing `WMBO_CL_ontology_subset` tab or a separate read-only tab? The first is convenient, but a sheet sync could overwrite script output.
20. **Where the mapping table is kept.** The draft commits a static `v1_v2_mapping.tsv` copy into WMBO. The alternative is to fetch it from the WMBv2 repo at build time. A static copy is reproducible; fetching stays current if the v2 mapping is revised.
21. **ID collisions and stability.** New `CL_43…` IDs depend on the `CLIdFactory` block layout. Check that no new ID collides with an existing CL term, and that none of the existing 130 IDs shift.
22. **Downstream.** Should the new CL terms and synonyms be coordinated with the CL editors before release (for example, a CL PR importing `wmbo-cl-comp`), and with PCL/CAP so that both versions resolve consistently?
23. **WMBv2 in WMBO.** Out of scope here, but should a later WMBO release be built from CCN20251031 directly? If so, promotions chosen now should stay compatible with that route.
