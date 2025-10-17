# Evidence Handling Content Report - WMBO

## Overview

The Whole Mouse Brain Ontology (WMBO) implements a comprehensive evidence handling system that tracks scientific rationale, supporting literature, and marker gene evidence for cell type classifications. This report details how evidence data is captured, processed, and integrated into the final ontology to ensure scientific transparency and reproducibility.

## Data Sources

### Primary Evidence Sources
- **Rationale Text**: Expert-authored scientific justifications for cell type mappings
- **DOI References**: Published literature supporting cell type classifications
- **Marker Gene Evidence**: Molecular evidence for cell type assignments
- **Neurotransmitter Evidence**: Gene expression evidence for neurotransmitter identity

### Evidence Types in Taxonomy Data

#### 1. Rationale Documentation
**Location**: `src/dendrograms/CCN20230722.json`
**Field**: `"rationale"`
**Purpose**: Human-readable scientific justification for cell type mapping

**Example Rationale**:
```json
"rationale": "Consistent with this cell set being composed of Pinealocytes, a combination of Pinealocyte markers Gngt1 and Crx can identify the cells in this cluster with a confidence (F-beta score) of 0.91 in the context of glutamatergic cells (Pinealocytes release glutamate) from the hippocampal formation dissection (which includes the pineal gland)."
```

#### 2. Literature References
**Field**: `"rationale_dois"`
**Purpose**: Published research supporting cell type classifications

**Example References**:
```json
"rationale_dois": [
  "https://doi.org/10.1111/j.1600-079x.1996.tb00284.x",
  "https://doi.org/10.3389/fendo.2019.00590"
]
```

#### 3. Marker Gene Evidence
**Field**: `"marker_gene_evidence"`
**Purpose**: Specific genes supporting cell type identity

**Example Evidence**:
```json
"marker_gene_evidence": [
  "Crx",
  "Gngt1",
  "Tph1",
  "Asmt",
  "Gngt2"
]
```

#### 4. Neurotransmitter Evidence
**Fields**:
- `"neurotransmitter_rationale"`: Expression levels supporting NT identity
- `"neurotransmitter_marker_gene_evidence"`: Specific NT-related genes

**Example NT Evidence**:
```json
"neurotransmitter_rationale": "Slc17a7:9.91,Slc17a6:4.87",
"neurotransmitter_marker_gene_evidence": [
  "Slc17a7",
  "Slc17a6"
]
```

## Processing Scripts

### 1. Evidence Marker Set Generation (`template_generation_tools.py`)

**Function**: `generate_evidence_marker_gene_set_template()`
- Extracts evidence-based markers from taxonomy data
- Creates formal marker set definitions with evidence tracking
- Links markers to scientific rationale and publications

**Code Extract**:
```python
def generate_evidence_marker_gene_set_template(taxonomy_file_path, output_filepath):
    dend = cas_json_2_nodes_n_edges(taxonomy_file_path)
    all_nodes = {node['cell_set_accession']: node for node in dend['nodes']}

    evidence_marker_sets = []
    for node in dend['nodes']:
        if node.get('marker_gene_evidence'):
            marker_set = create_evidence_marker_set(node)
            evidence_marker_sets.append(marker_set)

    # Generate template with evidence attribution
    generate_template_file(evidence_marker_sets, output_filepath)
```

**Processing Logic**:
1. Parse taxonomy JSON for evidence fields
2. Extract marker gene evidence for each cell type
3. Create formal marker set identifiers (CLM: namespace)
4. Associate markers with source rationale and DOIs
5. Generate DOSDP-compatible template files

### 2. Evidence Association (`associate_marker_sets()`)

**Function**: Links evidence markers to cell type definitions
- Associates evidence marker sets with cell type classes
- Maintains evidence provenance through the pipeline
- Creates cross-references between evidence and classifications

**Code Extract**:
```python
def associate_marker_sets(all_nodes, node, d, id_factory, id_prefix):
    """Associates evidence marker sets to cell type nodes"""

    if node.get('marker_gene_evidence'):
        d['evidence_marker_gene_set'] = (id_prefix +
            id_factory.get_evidence_marker_gene_set_id(
                node['cell_set_accession']))

    # Link to rationale and DOI evidence
    if node.get('rationale'):
        d['scientific_rationale'] = node['rationale']

    if node.get('rationale_dois'):
        d['supporting_literature'] = "|".join(node['rationale_dois'])
```

## Template Integration

### DOSDP Pattern: taxonomy_class.yaml

**Evidence Properties**:
```yaml
annotationProperties:
  evidence: "oboInOwl:evidence"
  seeAlso: "rdfs:seeAlso"
  hasDbXref: "oboInOwl:hasDbXref"

data_vars:
  evidence_marker_gene_set: "xsd:string"

logical_axioms:
  - axiom_type: subClassOf
    text: "%s"
    vars:
      - CL
    annotations:
      - annotationProperty: evidence
        text: "%s"
        vars:
          - evidence_marker_gene_set
```

**Evidence Marker Set Pattern**: `taxonomy_marker_set.yaml`
```yaml
pattern_name: brainCellCharacterizingMarkerSets
description: "Evidence-based marker sets with scientific rationale"

data_vars:
  Algorithm: "xsd:string"
  Source: "xsd:string"
  Reference: "xsd:anyURI"

name:
  text: "%s (%s)."
  vars:
    - Markers_label
    - Source

annotations:
  - annotationProperty: hasDbXref
    text: "%s"
    vars:
      - Reference
```

### Template Data Structure

**Evidence Marker Set Template**: `CCN20230722_evidence_marker_set.tsv`
```tsv
defined_class	Marker_set_of	Markers	Markers_label	Algorithm	Source	Reference
CLM_5029176	pinealocyte	NCBIGene:12951|NCBIGene:14699|NCBIGene:21990	Crx, Gngt1, Tph1	CAS evidence	https://doi.org/10.3389/fendo.2019.00590
CLM_5024421	COP NN_1	NCBIGene:574402|NCBIGene:12159|NCBIGene:241159	Gpr17, Bmp4, Neu4	CAS evidence	https://doi.org/10.1126/science.aaf6463
```

**Class Template Evidence Fields**:
- **evidence_marker_gene_set**: Link to evidence-based marker set (CLM ID)
- **Source citations**: Literature references supporting classifications
- **Algorithm**: Method used for evidence validation ("CAS evidence")

## Build Integration

### Makefile Processing
```makefile
# From src/dendrograms/Makefile - Evidence marker set generation
../patterns/data/default/%_evidence_marker_set.tsv: %.json
	python ../scripts/template_runner.py generator -ems -i $< -o $@

# Evidence marker set OWL generation
components/%_evidence_marker_set.owl: ../patterns/data/default/%_evidence_marker_set.tsv
	$(DOSDPT) generate --template=../patterns/dosdp-patterns/taxonomy_marker_set.yaml \
		--infile=$< --outfile=$@
```

### ODK Integration (`wmbo.Makefile`)
```makefile
# Evidence marker set integration
OWL_EVIDENCE_MARKER_SET_FILES = $(patsubst %, components/%_evidence_marker_set.owl, $(JOBS))

# Include evidence files in main ontology build
$(PATTERNDIR)/definitions.owl: $(OWL_EVIDENCE_MARKER_SET_FILES)
	$(ROBOT) merge $(addprefix -i , $^) \
		annotate --ontology-iri $(ONTBASE)/patterns/definitions.owl
```

## Final OWL Output

### Evidence-Based Class Assertions
```owl
[Term]
id: CL:4306426
name: pinealocyte
is_a: CL:0000652 {evidence="http://identifiers.org/ncbigene/13195", evidence="http://identifiers.org/ncbigene/140919", evidence="http://identifiers.org/ncbigene/72961"}
relationship: RO:0015004 CLM:5029176  # has_characterizing_marker_set
xref: "https://doi.org/10.3389/fendo.2019.00590"
xref: "https://doi.org/10.1111/j.1600-079x.1996.tb00284.x"
```

### Evidence Marker Set Classes
```owl
[Term]
id: CLM:5029176
name: Crx, Gngt1, Tph1, Asmt, Gngt2 (CAS evidence).
def: "Evidence-based marker set for pinealocyte identification" []
property_value: IAO:0000064 "CAS evidence" xsd:string
property_value: seeAlso "https://doi.org/10.3389/fendo.2019.00590" xsd:anyURI
relationship: BFO:0000051 NCBIGene:12951  # has_part Crx
relationship: BFO:0000051 NCBIGene:14699  # has_part Gngt1
relationship: BFO:0000051 NCBIGene:21990  # has_part Tph1
```

### Gene-Level Evidence Annotations
```owl
[Term]
id: NCBIGene:12951
name: Crx
property_value: rdfs:seeAlso "https://doi.org/10.3389/fendo.2019.00590" xsd:anyURI
property_value: IAO:0000115 "cone-rod homeobox, pinealocyte marker" xsd:string
```

### Neurotransmitter Evidence
```owl
relationship: RO:0002215 GO:0061535 {comment="Inferred to be glutamate secretion, neurotransmission based on expression of Ddc, Slc17a6, Slc17a7"}
```

## Evidence Categories and Quality Levels

### 1. Direct Literature Evidence
**High Confidence**: Published research directly supporting cell type identity
- **DOI tracking**: Direct links to supporting publications
- **Author rationale**: Expert interpretation of literature
- **Marker validation**: Independent experimental confirmation

### 2. Computational Evidence
**Medium Confidence**: Algorithm-derived evidence with statistical support
- **Algorithm attribution**: "CAS evidence", "NS-Forest", etc.
- **Confidence scores**: F-beta scores, precision/recall metrics
- **Cross-validation**: Multiple algorithmic approaches

### 3. Comparative Evidence
**Supporting**: Cross-species and cross-dataset validation
- **Homology**: Conserved markers across species
- **Consistency**: Agreement across multiple datasets
- **Atlas validation**: Allen Brain Atlas spatial confirmation

## Quality Assurance Features

### 1. Evidence Provenance
- **Source tracking**: Original publication and dataset references
- **Method documentation**: Algorithm and parameter recording
- **Expert attribution**: Curator and author identification
- **Version control**: Evidence update history

### 2. Evidence Validation
**Automated Checks**:
- DOI format validation
- Gene identifier verification
- Citation consistency checking
- Cross-reference validation

**Manual Curation**:
- Expert review of rationale text
- Literature relevance assessment
- Scientific accuracy verification
- Evidence strength evaluation

### 3. Conflict Resolution
**Evidence Conflicts**:
- Multiple competing evidence sources
- Contradictory literature findings
- Algorithm disagreements
- Expert opinion differences

**Resolution Strategies**:
- Evidence weighting based on quality
- Expert panel consensus
- Additional experimental validation
- Transparent documentation of uncertainties

## Evidence Integration Examples

### 1. Pinealocyte Classification
**Evidence Sources**:
- **Literature**: Pinealocyte biology and marker expression
- **Markers**: Crx, Gngt1, Tph1 (pineal-specific genes)
- **Rationale**: Expert interpretation of marker combination
- **Confidence**: F-beta score 0.91

**Integration**:
```owl
is_a: CL:0000652 {evidence="NCBIGene:12951", evidence="NCBIGene:14699", evidence="NCBIGene:21990"}
xref: "https://doi.org/10.3389/fendo.2019.00590"
```

### 2. Oligodendrocyte Lineage
**Evidence Sources**:
- **Literature**: Single-cell oligodendrocyte differentiation studies
- **Markers**: Stage-specific expression (Gpr17, Tcf7l2, Cldn11)
- **Spatial**: White matter tract localization
- **Algorithm**: CAS evidence classification

**Integration**:
```owl
# Committed oligodendrocyte precursor
relationship: RO:0015004 CLM:5024421
xref: "https://doi.org/10.1126/science.aaf6463"

# Evidence marker set
CLM:5024421: "Gpr17, Bmp4, Neu4, Fyn (CAS evidence)"
```

## Documentation and Transparency

### 1. Evidence Documentation
- **Rationale preservation**: Full text scientific justification
- **Literature links**: Direct access to supporting publications
- **Method transparency**: Algorithm and parameter documentation
- **Update tracking**: Evidence modification history

### 2. Reproducibility Support
- **Code availability**: Open source processing scripts
- **Data provenance**: Complete evidence source tracking
- **Version control**: Evidence evolution documentation
- **Quality metrics**: Confidence scores and validation results

### 3. Community Standards
- **FAIR principles**: Findable, Accessible, Interoperable, Reusable evidence
- **OBO standards**: Evidence annotation best practices
- **Scientific integrity**: Transparent uncertainty acknowledgment
- **Peer review**: Community validation and feedback

## Summary

The WMBO evidence handling system provides:

1. **Comprehensive evidence capture**: Rationale, literature, molecular evidence
2. **Formal representation**: OWL evidence annotations and provenance
3. **Quality assurance**: Validation, curation, and conflict resolution
4. **Transparency**: Full evidence documentation and accessibility
5. **Reproducibility**: Complete method and data provenance
6. **Community standards**: FAIR and OBO compliance
7. **Scientific rigor**: Expert curation and literature validation
8. **Computational accessibility**: Structured evidence for analysis

This evidence system ensures that every cell type classification in WMBO is scientifically grounded, transparently documented, and computationally accessible for validation and further research.