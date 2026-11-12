# Uberon new term request: cerebellum-like structure (draft)

**Label:** cerebellum-like structure

**Definition:** A brain structure with a cerebellum-like circuit architecture. It has a molecular layer of parallel fibres, the axons of granule cells, which synapse onto the spiny apical dendrites of Purkinje-like principal cells and onto molecular-layer inhibitory interneurons. The principal cells also receive input from a deeper layer, carrying a primary sensory input. Examples include the cerebellum and, in mammals, the dorsal cochlear nucleus.
- doi:10.1146/annurev.neuro.30.051606.094225 (Bell, Han & Sawtell 2008, "Cerebellum-like structures and their implications for cerebellar function")
- doi:10.1016/j.tins.2003.12.001 (Oertel & Young 2004, "What's a cerebellar circuit doing in the auditory system?")

**Proposed parent:** `regional part of brain` (UBERON:0002616)

**Proposed children (is_a, not part_of):** the term groups structures by kind of architecture. It is not a containing region.
- cerebellum (UBERON:0002037)
- dorsal cochlear nucleus (UBERON:0002829)
- Candidates from Bell et al. 2008, for Uberon editors to judge:
  - electrosensory lateral line lobe (UBERON:2002105)
  - medial octavolateralis nucleus (UBERON:2000291)
  - torus longitudinalis (UBERON:2000449): with the marginal layer of the optic tectum, it forms the cerebellum-like structure of ray-finned fish

**Synonyms:**
- `cerebellum-like circuit` (related)
- `cerebellar-like structure` (exact)

**Use case:**
- CL grouping classes for neurons of the cerebellum and the dorsal cochlear nucleus, which share cell types: Purkinje-like principal cells (Purkinje and cartwheel cells), granule cells, unipolar brush cells, Golgi cells, and molecular-layer interneurons.
- Single-cell atlases (e.g. the Allen whole mouse brain taxonomy) group dorsal cochlear nucleus types with cerebellar types transcriptomically: `308 DCO Il22 Gly-Gaba` (cartwheel-like) and `315 DCO UBC Glut` are in the cerebellar classes.
- CL currently has no common parent below `hindbrain`, which is too broad. With this term, CL can define `cerebellum-like structure GABAergic neuron` ≡ GABAergic neuron ⊓ has soma location some cerebellum-like structure, and the reasoner (ELK) classifies cells from both structures without unions.

**Interim CL modelling (to be replaced once this term exists):** CL classes CL:9900027–9900029 on branch `ai4c-agent-issue-3788-run1175`, populated by one GCI per structure. For example:
`GABAergic neuron and (has soma location some dorsal cochlear nucleus) SubClassOf cerebellum-like structure GABAergic neuron`
