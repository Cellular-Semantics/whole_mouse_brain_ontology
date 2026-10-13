# Naming CL-promoted WMBO terms (draft plan)

## Context

The next WMBO release will promote about 457 WMBv1 cell sets to CL. `docs/wmbv2_cl_promotion.md` describes how they are chosen. Their names go into CL, so they must be accurate.

Today a promoted term's label comes from the DOSDP template `"%s %s (%s)"`: taxonomy label + `Gross_cell_type` (the nearest CL term on the node or an ancestor) + taxon. This goes wrong in three ways:
- **Redundancy.** Taxonomy tokens repeat what the CL head term says:
  - `STR D1 Gaba direct pathway medium spiny neuron (Mmus)`
  - `CBX MLI Megf11 Gaba molecular layer interneuron (Mmus)`
  - `VLMC NN vascular leptomeningeal cell (Mmus)`
  - `Astro-TE NN_3 astrocyte (Mmus)`
- **Misleading neurotransmitters.** The neurotransmitter (NT) in the label is fixed at subclass level, or comes from the CL term, but not all clusters underneath carry it.
  - `CB PLI Gly-Gaba` has GABA-only clusters.
  - Every cluster of `MB-MY Tph2 Glut-Sero` is annotated either Sero or Glut, never both.
  - The curated name for `21 MB Dopa` (merged into `SUBC_215`) is "midbrain GABAergic neuron".
- **Locations fixed at subclass level.** Supertypes and clusters often have no cells in some of the regions their label names.

**Goal:** give every CL-promoted term a curated final name that is accurate and not redundant. Existing taxonomy labels stay as exact synonyms and are not changed.

**Sequencing:** promotion review and action → CL parent mapping → **naming** → release. The CL parent supplies the head noun of the name, so naming comes after mapping.

## Decisions

1. **The override replaces the whole name.** The final label comes verbatim from `defined_class_name` in the `WMBO_CCN20230722_class_curation` sheet, with no template parts appended. Every CL-promoted term gets one; no template-generated label ships in CL. The PCL terms are out of scope for now.
2. **Taxonomy labels are left alone.** They are already exact synonyms (`Synonyms_from_taxonomy`), and the v2 label is added as a related synonym.
3. **Neurotransmitters in the name:**
   - Drop any NT mention that isn't supported by *all* v1 clusters under the term, using `neurotransmitter_accession`.
   - This applies to taxonomy tokens (Glut, Gaba, Gly, Chol, Dopa, Sero, Nora, Hist) and to NT meaning carried by the CL head term (e.g. "GABAergic neuron").
   - **Combinations** (`Glut-Sero`, `Gly-Gaba`, `Gaba-Chol`, `Dopa-Gaba`, `Hist-Gaba`, …): keep the one NT that applies to all clusters. If none does, drop the NT.
   - **`NA`** (unannotated) clusters are ignored.
   - The already-promoted `CB PLI Gly-Gaba` terms are included.
   - This check changes names only; it doesn't remove terms from promotion.
4. **Redundancy.** Remove taxonomy tokens that the CL head term already expresses:
   - cell-class tokens such as `Astro`, `Oligo`, `OPC`, `VLMC`, `MLI` or `PLI` when the head says it;
   - `NN`, always;
   - `CB`/`CBX` when the head is "cerebellar …";
   - an NT when the head implies it.
5. **Locations.** Location acronyms stay as they are in names for now; expanded forms are far too long, especially with several regions. Checking and pruning them against regional summaries in Brain Cell KG is a later step.
6. **Numbers.** Supertype `_n` suffixes stay where no distinguishing marker is available. Clusters already have markers folded in. Leading taxonomy numbers (`0164 …`) are dropped from final names; they survive in the synonyms.

## Workflow

### Step 0: Make the override explicit and tested
- `defined_class_name` shows up in the released `wmbo-cl-comp.obo` (e.g. `CL:4300358 subcortical astrocyte (Mmus)`). But no code in the repo reads it apart from the seeding of the curation table (`src/scripts/template_generation_tools.py` ~l.629). The DOSDP `name` is hard-coded to `"%s %s (%s)"`.
- Find where the override is applied today; it may be an uncommitted or removed step.
- Then implement it explicitly: if `defined_class_name` is set, the label is exactly that value. Do the same for `defined_class_definition`. The released definitions appear to mix a curated first sentence with template clauses, so decide whether that is what we want.
- Add a build check that every `CL:43…` label equals its override.

### Step 1: Build the evidence table
Add a naming table to the `cl_promotion/` machinery in the WMBv2 consensus repo, next to the promotion set. One row per promoted term:
- the accession, level, v1 label, v2 label and merged singleton-chain members;
- the CL parent ID and label, from the mapping step;
- the current generated label;
- the parent's final name;
- the sibling v1 labels.
- **NT evidence:**
  - NT tokens in the v1 label;
  - NT implied by the CL head;
  - the distribution of cluster `neurotransmitter_accession` values, ignoring NA;
  - the set of NTs present in every cluster.
- **Location and markers:** location tokens, and cluster-level markers.
- **Existing override:** any current `defined_class_name`. All 40 existing overrides are re-checked; `SUBC_215` is already known to be wrong.

### Step 2: Deterministic pre-pass
Apply the mechanical rules to produce a draft name:
- drop the leading number and `NN`;
- reduce NT combinations to the NT supported by every cluster, or none;
- drop unsupported NTs;
- remove tokens duplicated by the CL head;
- attach the head noun. When the CL parent is generic ("neuron"), the head is the supported NT adjective + "neuron", e.g. `PVH-SO-PVa Otp glutamatergic neuron`;
- add `(Mmus)`.

### Step 3: Agent pass
The agent works on the draft only where the rules leave something awkward: word order, duplicated or clashing tokens, siblings that become indistinguishable.
- It may use only the evidence in the row; no new markers or regions.
- It returns `proposed_name`, `rationale`, `changes` (tokens removed or added, and why) and `confidence`.

### Step 4: Automated checks (re-run on the final values)
- **NT consistency** of the final name, including any NT implied by the head term, against all non-NA clusters.
- **Redundancy:** no token restates the head term.
- **Uniqueness** within WMBO, and against existing CL labels via the OLS4 MCP.
- **Siblings** under the same promoted parent have distinct names.
- **Format:** `(Mmus)` suffix, no leading numbers, no `NN`.

### Step 5: Curator review → sheet
- Curators review the proposals, sorted by confidence and by failed checks.
- Accepted names go into `defined_class_name` in the curation sheet. The sheet sync brings them into `CCN20230722_class_curation.tsv`.

### Step 6: Build and verify
Rebuild. Check that:
- every CL-promoted term's label equals its override;
- the taxonomy label is an exact synonym and the v2 label a related synonym;
- the Step 4 checks pass on the released `wmbo-cl-comp.obo`.

## Later: checking locations against Brain Cell KG
Location acronyms are inherited from the subclass label. Use the regional summaries in Brain Cell KG to find supertypes and clusters with few or no cells in a named region. Then prune those regions from names or definitions, and adjust the `Locations` axioms. This is a separate release.

## Open questions
- **`(Mmus)` suffix:** keep it on every CL-promoted name? The existing overrides mostly have it, but not all (e.g. `CB PLI GABA_3 Gpr101 Purkinje layer interneuron`).
- **NT form:** spell NTs out ("glutamatergic") or keep taxonomy abbreviations ("Glut")? Spelled out reads better in CL; abbreviations match the synonyms.
- **Definitions:** does this pass also write `defined_class_definition`, or leave the template definition?
- **Existing overrides:** do all 40 get the same rules, including the CB PLI terms whose labels change?
