# Classifying CL-promoted WMBO types by soma location and neurotransmitter

*Plan written 2026-10-26; status updated 2026-11-12. Follows `wmbv2_cl_promotion.md` (selection) and `wmbo_cl_naming_plan.md` (naming).*

## Status (2026-11-12)

Done, on `main`:

- **#135**: the cl-comp build gives each CL term its CL parents before PCL classes are removed (step 4).
- **#134**: derived soma location and shared neurotransmitter for CL-subset terms (steps 1 to 3).
  - Locations come from Brain Cell KG MERFISH counts (`derived_soma_locations.tsv`, method in `derived_soma_locations.md`). They are rolled up in a CCF tree aligned with Uberon at the top, then mapped by the mbao bridge.
  - Neuronal terms get `has_soma_location`; non-neuronal terms get `part_of`. A curated `Locations` value replaces either.
  - A term gets an NT when every cluster under it with a call shares it (`Shared_NT`).
  - In the CL subset, 337 of 408 terms have a location (291 `has_soma_location`, 46 `part_of`).
  - Curated NTs: `145 MH Tac2 Glut` and `251 NTS Dbh Glut` get glutamate. `215 SNc-VTA-RAmb Foxa1 Dopa` and class `21 MB Dopa` get dopamine, and the term is renamed "SNc-VTA-RAmb Foxa1 dopaminergic neuron (Mmus)".
- **#136**: `some soma located in` (`CLM:0010001`) annotations on supertypes and subclasses, from the same MERFISH counts (`supertype_subclass_locations.tsv`).
- CL grouping classes are on CL master: region × NT (#3797), cerebellum-like structure (#3828; CL:0020087–89) and `cerebellum GABAergic neuron` (CL:0020116). The temporary `CL:99…` IDs in the sections below are the ones used while the plan was drafted.
- Taxonomy #28 maps classes `28 CB GABA` and `29 CB Glut` to CL:0020088 and CL:0020089.

Test build (WMBO `main` + #134 + #136, with CL #3841), checked with `cl-full`: no unsatisfiable classes, cycles or new equivalences. 292 of 298 neuronal terms reach a region × NT grouping class. The six misses are three serotonergic terms whose clusters carry mixed NTs (CL:4300256, CL:4301319, CL:4301322) and three with no location (CL:4301055, CL:4301151, CL:4301345).

Still open:

- `MB-MY Tph2 Glut-Sero` and its supertypes need NT curation.
- Taxonomy release: the export fails because CL:0020088/89 are not in a CL release yet (see `wmbo_cl_integration_test_plan.md`).
- CL #3841 (MGE/CGE-derived interneuron definitions) fails CL's `cl-plus` step. The released `pcl-base.owl` still carries the old definitions of these classes, so four classes become equivalent. It needs PCL re-released, or CL axioms stripped from PCL in the `cl-plus` recipe.

## Next round

1. **Location in textual definitions above cluster level.** The DOSDP pattern generates a location clause in cluster definitions, and could do the same for supertypes, subclasses and classes. Some terms may lack it because a curated `defined_class_definition` overrides the generated one; check these.
2. **MERFISH counts: Yao et al. 2023 only.** Consider using only the Yao counts, not Yao + Zhang pooled. Counts would then add up across one taxonomy level and match the ABC atlas. This affects `derive_soma_locations.py` and `supertype_subclass_locations.py` (`src/scripts/`).
3. **Naming.** Review `defined_class_name` again (see `wmbo_cl_naming_plan.md`). It is better than before but can be improved.
4. **More promotions.** Check for more stable WMBv2 types to promote to CL and review them together (see `wmbv2_cl_promotion.md`, "Next round").

## Original plan (2026-10-26)

### Context

Release `v2026-10-16` put 406 WMBv1 types in CL (`CL:430…`), up from 130. Two problems showed up in that release.

1. **86 of the 276 new CL terms have no parent in `wmbo-cl-comp`.** In `wmbo-base`, the only `is_a` these terms have is their taxonomy parent, which is a PCL class (e.g. `CL:4300041` → `PCL:0110001` "IT-ET Glut…"). Their CL `Gross_cell_type` parent is dropped as redundant, because it's implied through that PCL parent. The cl-comp recipe then removes every PCL axiom, so nothing is left.
2. **Selection is conservative**, mainly because of the hierarchy rules:
   - The gate's parent check compares only the *immediate* parent's v1→v2 mapping. 352 types pass F1 and reciprocity but fail this check. Ignoring it, 90 of them would be S1 and 93 S2. Most failures come from an unstable parent (59 of the 90 S1 have a parent with F1 < 0.8), not from the type itself.
   - The first-release rule drops clusters with no promoted supertype or subclass (about 80).

A promoted type only needs its taxonomy parent to be promoted if that parent is its sole route to a CL classification. If each promoted type instead carries **its own soma-location and neurotransmitter axioms**, the reasoner classifies it under general **region × NT grouping classes** (requested in obophenotype/cell-ontology#3788, drafted on CL branch `ai4c-agent-issue-3788-run1175`). That makes both hierarchy rules unnecessary.

### Proposal

For every CL-promoted WMBO type, add two kinds of logical axiom:
- **Soma location:** `has_soma_location some <Uberon region>`. This promotes today's `some_soma_located_in` (`CLM:0010001`) annotations, which give Allen atlas (MBA) regions with cell ratios, into an existential restriction to a single Uberon class.
- **Neurotransmitter:** `capable_of some <NT secretion GO process>`, for each NT that every cluster under the type carries.

The existing annotations and cell ratios stay as provenance.

#### Evidence that it works
In a spike (`cl_promotion/classification/` in the WMBv2 consensus repo), defined test classes of this shape were reasoned with ELK against CL 2026-06-08 plus the 26 grouping classes on the #3788 branch. **About 80% of neuronal types classify under a grouping class**, whichever selection rule is used:

| Selection | Neuronal types tested | Under a #3788 class |
|---|---|---|
| Current promotion set | 411 | 327 (80%) |
| S1, no parent rule | 459 | 368 (80%) |
| S1 + S2, no parent rule | 716 | 573 (80%) |

Clusters outside the current set weren't profiled yet, so the cluster share in the wider rows is under-tested.

### Steps

#### 1. Choose the soma-location region per type
- Use per-type MERFISH counts from Brain_Cell_KG (Yao 2023 and Zhuang 2023), renormalised to grey matter.
- Assert the **deepest region holding ≥ 80% of cells in both atlases**, not the common ancestor of *all* annotated regions. Registration noise scatters a few cells widely, which would push that ancestor up to "brain".
- **Map to Uberon first, then roll up in Uberon's partonomy, not the Allen atlas's.** The Allen-to-Uberon bridge equates groupings that differ:
  - Allen "cerebral cortex" includes the cortical subplate (claustrum, endopiriform nucleus, lateral/basolateral amygdala) and, via its olfactory areas, the olfactory bulb. Uberon `cerebral cortex` includes none of these, but does include the olfactory tubercle.
  - Allen "brain stem" includes the interbrain (thalamus, hypothalamus); Uberon `brainstem` does not.
  - Allen "hindbrain" excludes the cerebellum; Uberon `hindbrain` includes it.

  Rolling up in Allen terms is why 12 olfactory-bulb types are currently labelled "… cerebral cortex neuron", and why `250 CBN Neurod2 Pvalb Glut` (71% cerebellum, 20% medulla) gets no region at all. Within Uberon both resolve correctly: olfactory bulb, and hindbrain.
- **Fallback for types missing from the KG** (64 nodes): use the taxonomy's per-cluster `CCF_acronym.freq`. Fix its parser first: acronyms containing commas (e.g. cerebellar lobules `CUL4, 5`) are currently split, which sends some cerebellar granule types to "grey matter".
- Record the threshold, both atlas ratios and the source in a comment, since a type with a genuine 80/20 split is asserted at the 80% region.

#### 2. Neurotransmitter
- Use the expression-based cluster calls (`neurotransmitter_accession`, with evidence in `neurotransmitter_rationale`). Assert an NT only if every annotated cluster under the type carries it; NA is ignored.
- For co-transmitter types that genuinely share both NTs (e.g. GABA + glycine), assert both.
- Assert none for mixed types (e.g. `MB-MY Tph2 Glut-Sero`, `145 MH Tac2 Glut`). They classify by region only.
- GO terms are those used by CL's NT neuron classes: glutamate `GO:0061535`, GABA `GO:0061534`, glycine `GO:0061537`, acetylcholine `GO:0014055`, dopamine `GO:0061527`, serotonin `GO:0060096`, noradrenaline `GO:0061533`, histamine `GO:0061538`.

#### 3. WMBO templates and pattern
- The class base template already has a soma-location slot, currently whole brain (`MBA:997`) for every row. Fill it with the Uberon region from step 1, and add an NT slot.
- Generate both columns from the profiling step in the WMBv2 repo (`cl_promotion/classification/profile_nodes.py`, extended to emit Uberon IRIs).
- `taxonomy_class.yaml`: emit `SubClassOf(has_soma_location some ?region)` and `SubClassOf(capable_of some ?nt)`.
- **Check the RO property chain** `has_soma_location ∘ part_of → has_soma_location`, which ELK needs to classify a type in a sub-region under a coarser-region class. If RO doesn't provide it, also assert `part_of some ?region`, as the spike did.

#### 4. Fix the cl-comp build (needed regardless)
- Before `remove --select "<…PCL_*>"`, give each CL term its **nearest non-PCL ancestors from the reasoned hierarchy**, e.g. a SPARQL update over the reasoned `wmbo-pcl-comp`, then reduce.
- `robot remove --preserve-structure` is not enough. Tested on the released base, it parents most orphans to `BFO:0000002` and leaves 11 parentless.
- Release check: no `CL:430…` term in `wmbo-cl-comp` without a CL parent.

#### 5. Selection rules
Once types carry their own axioms:
- drop the gate's parent check, or apply it only against the nearest *stable* ancestor;
- drop the cluster-needs-promoted-parent rule.

Release sizes with no parent rule (including everything already in CL; the current release is 456):

| Promote | Subclass | Supertype | Cluster | Total | Change |
|---|---|---|---|---|---|
| S1 | 99 | 247 | 281 | 627 | +171 |
| S1 + S2 | 201 | 403 | 541 | 1,145 | +689 |
| S1 + S2 + S3 | 252 | 553 | 898 | 1,703 | +1,247 |

Recommendation:
- Start with **S1, no parent rule** (+171).
- Then add **S2 subclasses and supertypes**. These are mostly coarse types that the Macosko clusters split differently, including the glia.
- Add S3 only with independent evidence, such as a basal ganglia MapMyCells match or a curated CL mapping.

#### 6. Grouping classes in CL
- **#3788 branch (26 terms).** Before merge:
  - expand the definitions of the cerebral-cortex classes to state what's included;
  - add `neocortex GABAergic neuron` and `hippocampal formation GABAergic neuron` to match the glutamatergic pair;
  - note the olfactory-tubercle inclusion.
- **Cerebellar classes.** These were left out of the branch; see the next section.
- **Lineage and marker classes** (#3789, #3790) cover the telencephalic GABAergic types that region classes handle poorly.
- **Errors found** (#3791), notably the `thalamic excitatory neuron` location.

#### 7. Types that won't classify
About 20% of neuronal types have no single dominant region, or no NT shared by all clusters: MB-HB Glut/Sero mixes and extended-amygdala/preoptic types. They keep the nearest-non-PCL-ancestor parent from step 4, plus curator review. Lineage classes may cover some of them.

#### 8. Verification
- Reasoning over `wmbo-cl-comp` + CL + the grouping classes gives no unsatisfiable classes.
- Every `CL:430…` term has a CL parent.
- Report what share of terms sits under a region × NT class, overall and by level.
- Spot-check the Allen-vs-Uberon cases: olfactory-bulb types, claustrum/amygdala types, cerebellar nuclei.
- `make check_ids` still reports nothing missing other than the known marker-set gap (#129 follow-up).

### Cerebellar grouping classes (review, 2026-10-26)

**What CL has now:**

| Term | Definition / parents |
|---|---|
| `cerebellar neuron` CL:1001611 | neuron ⊓ soma in cerebellum |
| `cerebellum glutamatergic neuron` CL:2000028 | glutamatergic neuron ⊓ soma in cerebellum. Parent of `cerebellar granule cell` |
| `cerebellar inhibitory GABAergic interneuron` CL:4023057 | GABAergic interneuron ⊓ soma in **cerebellar cortex**. Parent of molecular layer interneuron (basket, stellate), Purkinje layer interneuron (Lugaro, candelabrum) and Golgi cell |
| `Purkinje cell` CL:0000121 | no logical definition. is_a GABAergic neuron and cerebellar neuron |
| `Lugaro cell` CL:0011006 | is_a **GABA-Gly neuron** and Purkinje layer interneuron |
| `cerebellar Golgi cell` CL:0000119 | is_a cerebellar inhibitory GABAergic interneuron. **Not** GABA-Gly, although WMB `310 CBX Golgi Gly-Gaba` is GABA + glycine in every cluster |
| `unipolar brush cell` CL:4023161 | glutamatergic interneuron, soma in **hindbrain**. That's appropriate: UBCs are in both the cerebellar granular layer and the dorsal cochlear nucleus, and WMB `315 DCO UBC Glut` is 42% cerebellum, 51% medulla |
| cerebellar nuclei neurons | **nothing**. No term has soma in `cerebellar nuclear complex` (UBERON:0002130) |

**Where WMB cerebellar types land now, with reasoning** (ELK, via the local Owlery, `owlery/`, `cl` and `wmbo` KBs). An earlier label- and template-based pass suggested CL needed several new classes. Reasoning shows it doesn't:
- Everything WMBO puts under `cerebellar neuron` is either GABAergic or glutamatergic (granule cells, UBCs).
- The GABAergic side already has a mouse-specific grouping, `cerebellar GABAergic neuron (Mmus)` CL:4300028 (WMB class `28 CB GABA`). It is asserted is_a GABAergic neuron and cerebellar neuron, with soma in MBA:512 (cerebellum). What's missing is a species-neutral parent.

**Proposed addition** (one class):
- [ ] **cerebellum GABAergic neuron** ≡ `GABAergic neuron` ⊓ `has soma location` some `cerebellum` (UBERON:0002037). The DL query for this expression returns:
  - **`cl` KB, 27 classes:** Purkinje cell; `cerebellar inhibitory GABAergic interneuron`, with Golgi, MLI (basket, stellate), PLI (Lugaro, candelabrum); and all the WMB-derived CL terms under CL:4300028.
  - **`wmbo` KB, 55 classes:** the same, plus their PCL clusters.
  - It mirrors the existing `cerebellum glutamatergic neuron` (CL:2000028).
- Golgi and Lugaro then sit under both this class and `GABA-Gly neuron`. A separate cerebellar GABA-Gly class isn't needed.

**Cerebellum-like grouping (added on the CL branch 2026-10-26, uncommitted; tested in Owlery):** The dorsal cochlear nucleus (DCN) shares the cerebellar circuit and cell types, and WMB places the DCO types in its cerebellar classes. Uberon has no term grouping the cerebellum with the DCN; a new term request is drafted in `docs/uberon_ntr_cerebellum_like_structure.md`. In the meantime the CL classes are populated by one GCI per structure, which ELK handles without unions:

| ID | Label | Populated by | Result (`cl` KB) |
|---|---|---|---|
| CL:9900027 | cerebellum-like structure neuron | GCIs: neuron ⊓ soma in cerebellum; neuron ⊓ soma in DCN | 40 subclasses |
| CL:9900028 | cerebellum-like structure GABAergic neuron | GCIs: GABAergic ⊓ soma in cerebellum / DCN | 29, incl. `cartwheel cell` |
| CL:9900029 | cerebellum-like structure glutamatergic neuron | GCIs: glutamatergic ⊓ soma in cerebellum / DCN; asserted parent of `unipolar brush cell`, whose soma location is `hindbrain` | 8 |
| CL:9900030 | cerebellum GABAergic neuron | ≡ GABAergic neuron ⊓ soma in cerebellum | 27: Purkinje cell, cerebellar inhibitory GABAergic interneuron, CL:4300028 |

- In the `wmbo` KB the counts are 76, 56, 17 and 54.
- No classes are unsatisfiable in `cl`.
- Once the WMBO DCO types get their own soma location (DCN rather than the inherited cerebellum), they will classify under CL:9900028 and CL:9900029, not `cerebellum GABAergic neuron`.

**Problems the query exposed (WMBO, not CL):**
- **The DCO types are cerebellar only by inheritance.** `308 DCO Il22 Gly-Gaba` has no soma axiom of its own (CL:4300348 and its supertypes). It inherits the cerebellum location from class `28 CB GABA`, but MERFISH puts it mostly in the medulla:

  | | Medulla | Cochlear nuclei | Cerebellum |
  |---|---|---|---|
  | Yao | 66% | 38% | 28% |
  | Zhuang | 71% | 64% | 29% |

  The type looks like the cochlear-nucleus cartwheel cell, so it shouldn't classify as cerebellar. The same applies to `315 DCO UBC Glut`: the cerebellum and medulla shares are close to even (42/51% in Yao, 53/38% in Zhuang). Its CL terms aren't classified as cerebellar today, but the PCL clusters under it are. Fix: give each node its own soma location, as Step 1 does, rather than inheriting the class's location.
- **The cerebellar-nuclei types classify only as `neuron`.**
  - `295 CBN Dmbx1 Gaba` (PCL:0111685) and `250 CBN Neurod2 Pvalb Glut` (PCL:0111573) carry no NT or soma axioms, and not even the `some soma located in` annotation.
  - Their MERFISH distributions: 295 is 92% cerebellum and 79% nuclei; 250 is 71–80% cerebellum, 59–62% nuclei and 16–20% medulla.
  - With Step 1 and Step 2 axioms, 295 lands under the new class. 250 lands under `cerebellum glutamatergic neuron` if the roll-up allows cerebellum (it is at 80% in Zhuang, 71% in Yao), and otherwise under hindbrain.
  - Cerebellar-nuclei classes (UBERON:0002130) could be added later, but aren't needed now.
- **Soma location in WMBO PCL terms is annotation-only.** 19,239 `some soma located in` annotations; 0 `RO:0002100` axioms. Only the CL product terms have the object property. Step 3 fixes this.

#### Cerebellar nuclei (CBN) nodes: justified axioms

**Mechanism.** Parent-node location and NT axioms come only from curation rows: the `Locations`, `Neurotransmitters` and `Neurotransmitters_comment` columns of `CCN20230722_class_curation`. That is how CL:4300028 got `MBA:512` and `GO:0061534`. Only 4 rows use these columns today. Clusters get NT axioms automatically, but location only as `some soma located in` annotations.

**Cluster evidence** (ratios from those annotations):
- "broad" values are broad regions; `brain` means the cell is outside grey matter, here almost entirely arbor vitae (cerebellar white matter).
- "nuclei" is the sum of the interposed, fastigial and dentate nuclei.

| Cluster | NT | Cerebellum (grey) | Arbor vitae | Medulla | Nuclei |
|---|---|---|---|---|---|
| 4521 CBN … Glut_1 Lmx1a (PCL:0116901) | Glut | 0.56 | 0.25 | — | 0.43 |
| 4522 … Prr16 (PCL:0116902) | Glut | 0.53 | 0.11 | 0.24 | 0.20 |
| 4523 … Pax5 (PCL:0116903) | Glut | 0.74 | — | 0.24 (superior vestibular nucleus 0.15) | 0.62 |
| 4524 … Evx2 (PCL:0116904) | Glut | 0.61 | 0.36 | — | 0.49 |
| 5000 CBN Dmbx1 Gaba_1 Foxp2 (PCL:0117380) | GABA | 0.69 | 0.24 | — | 0.58 |
| 5001 … Tfap2a (PCL:0117381) | GABA | 0.66 | 0.20 | — | 0.31 |

**Node-level KG MERFISH** (share of grey matter, Yao / Zhuang):
- `295`: cerebellum 92/92%; cerebellar nuclei 79/79%; medulla 8/6%.
- `250`: cerebellum 71/80%; cerebellar nuclei 59/62%; medulla 20/16%.

**Proposed curation:**
- **`295 CBN Dmbx1 Gaba` (PCL:0111685, = SUPT_1115).**
  - `Neurotransmitters` GO:0061534, with the comment "all clusters GABAergic (Gad1, Gad2, Slc32a1)".
  - `Locations` MBA:512 (cerebellum), justified: both clusters are ≥ 0.86 cerebellum including white matter, and the node is 92% in both atlases.
  - MBA:519 (cerebellar nuclei) is biologically right but borderline on the data (79%). It would be an optional refinement with a comment.
  - Result: `cerebellum GABAergic neuron` → `cerebellum-like structure GABAergic neuron`.
- **`250 CBN Neurod2 Pvalb Glut` (PCL:0111573, = SUPT_1003).**
  - `Neurotransmitters` GO:0061535, with the comment "all 4 clusters glutamatergic (Slc17a6)".
  - Location: cerebellum isn't defensible for the node as a whole. 2 of 4 clusters have 24% medulla (Pax5 partly in the superior vestibular nucleus), and Yao gives the node 71%. The options:
    - (a) `Locations` = Uberon hindbrain (UBERON:0002028) on the node, not MBA:1065: Allen's hindbrain excludes the cerebellum. This needs checking that the `Locations` column accepts Uberon IDs. plus cerebellum on clusters 4521 and 4524 (0.81 and 0.97 with white matter). Those two clusters reach `cerebellum-like structure glutamatergic neuron`; the node reaches the hindbrain glutamatergic class.
    - (b) Cerebellum on the node, with a comment recording the medullary/vestibular minority. This could be registration spill across the CN–vestibular boundary, or CN-like vestibular neurons.
- **Decision (2026-10-26): option (a).** The `CCN20230722_class_curation` rows are set on branch `cbn-location-nt` (uncommitted; the Google Sheet still needs the same edits):
  - SUPT_1003: UBERON:0002028 and GO:0061535;
  - SUPT_1115: MBA:512 and GO:0061534;
  - CLUS_4521 and CLUS_4524: MBA:512.

  Checked with ELK (current WMBO KB plus these axioms). Direct parents:

  | Node | Direct parent(s) |
  |---|---|
  | `250` | `hindbrain glutamatergic neuron` (CL:9900008) |
  | `295` | `cerebellum GABAergic neuron` (CL:9900030) |
  | 4521, 4524 | `cerebellum glutamatergic neuron` (and so cerebellum-like) |
  | 4522, 4523 | stay under `250` (hindbrain) |

- **Arbor vitae.** MBA_728 has no Uberon mapping in the bridge, so white-matter cells don't count toward cerebellum in the Allen roll-up. Count them in when choosing regions for deep-nuclei types.

### Open questions
1. **Thresholds.** Is 80% of cells, in both atlases, the right threshold for asserting a soma location? Should it be lower for coarse regions?
2. **Comment wording.** How should an existential soma-location axiom be documented when a minority of cells register elsewhere?
3. **Selection.** Go to S1 without the parent rule now, or wait until the cl-comp fix and the region/NT axioms are in?
4. **CL ticket.** Add `cerebellum GABAergic neuron` as an addendum on #3788, or edit it directly on the local CL branch?
5. **Non-neuronal types.** Should they get region axioms too (e.g. `astrocyte of the cerebellum`, already defined by part_of)?
