# Markers Content Report - WMBO

## Overview

The Whole Mouse Brain Ontology (WMBO) incorporates extensive marker gene information to characterize brain cell types based on their molecular signatures. This report details how marker data is sourced, processed through multiple algorithms, and integrated into the final ontology through various template systems.

## Data Sources

### Primary Taxonomy Source
- **File**: `src/dendrograms/CCN20230722.json`
- **Source**: Brain Initiative Cell Census Network (BICAN) whole mouse brain taxonomy
- **Content**: Hierarchical cell type definitions with associated marker gene expressions

### Marker Types and Algorithms

#### 1. Standard Marker Sets
- **File**: `src/patterns/data/default/CCN20230722_marker_set.tsv` (1.9MB)
- **Description**: Primary marker genes for cell type identification
- **Algorithm**: Cell type signature analysis from scRNA-seq data

#### 2. Within-Subclass Marker Sets
- **File**: `src/patterns/data/default/CCN20230722_within_subclass_marker_set.tsv` (1.7MB)
- **Description**: Markers that distinguish subtypes within broader cell classes
- **Algorithm**: Differential expression within cell type hierarchies

#### 3. NS-Forest Marker Sets
- **File**: `src/patterns/data/default/CCN20230722_nsforest_marker_set.tsv` (107KB)
- **Description**: Machine learning-derived minimal marker sets
- **Algorithm**: NS-Forest (Nearest Shrunken Centroids Forest) algorithm

#### 4. Evidence Marker Sets
- **File**: `src/patterns/data/default/CCN20230722_evidence_marker_set.tsv` (1.3KB)
- **Description**: High-confidence markers with strong statistical evidence
- **Algorithm**: Evidence-based filtering with confidence thresholds

### Marker Validation Sources
- **Allen Brain Atlas**: Cross-reference marker expressions
- **Ensembl Gene Database**: Gene identifier validation and enrichment
- **Manual Curation**: Expert-reviewed marker assignments

## Processing Scripts

### 1. Core Marker Processing (`marker_tools.py`)

**Function**: `generate_denormalised_marker_template()`
- Creates enriched marker tables based on hierarchical inheritance
- Aggregates markers from parent cell types to children
- Removes redundant marker associations

**Code Extract**:
```python
def generate_denormalised_marker_template(taxonomy_file_path, output_marker_path):
    if str(taxonomy_file_path).endswith(".json"):
        dend = cas_json_2_nodes_n_edges(taxonomy_file_path)

    tree = generate_dendrogram_tree(dend_data)
    marker_expressions = read_marker_file(flat_marker_path)
    marker_extended_expressions = extend_expressions(tree, marker_expressions, root_terms)
    generate_marker_table(marker_extended_expressions, output_marker_path)
```

**Processing Logic**:
1. Parse hierarchical taxonomy from JSON
2. Read existing marker associations
3. Propagate markers down the taxonomy tree
4. Create non-redundant marker lists for each cell type
5. Generate enriched marker template files

### 2. Marker Validation (`marker_validator.py`)

**File Name Validation**:
- Ensures marker files follow naming convention: `CS{taxonomy_id}_markers.tsv`
- Validates correspondence with dendrogram files
- Checks file existence and consistency

**Content Validation Classes**:
```python
class FileNameChecker(StrictChecker):
    """Validates marker file naming conventions"""

class StrictChecker(BaseChecker):
    """Failures cause exceptions"""

class SoftChecker(BaseChecker):
    """Failures cause warnings"""
```

**Quality Checks**:
- File naming consistency
- Marker-taxonomy correspondence
- Expression data integrity
- Cross-reference validation

### 3. Template Generation (`template_generation_tools.py`)

**Marker Set Generation Functions**:
- `generate_marker_gene_set_template()`: Standard marker sets
- `generate_nsforest_marker_gene_set_template()`: NS-Forest markers
- `generate_within_subclass_marker_gene_set_template()`: Subclass markers
- `generate_evidence_marker_gene_set_template()`: Evidence-based markers

**Sample Processing Logic**:
```python
def generate_marker_gene_set_template(input_file, output_file):
    # Parse taxonomy JSON
    taxonomy_data = read_json_file(input_file)

    # Extract marker information
    marker_sets = extract_marker_sets(taxonomy_data)

    # Generate template with confidence scores
    template_data = process_marker_confidence(marker_sets)

    # Write DOSDP-compatible TSV
    write_template_file(template_data, output_file)
```

## Template Integration

### DOSDP Pattern: taxonomy_marker_set.yaml

**Pattern Structure**:
```yaml
pattern_name: brainCellCharacterizingMarkerSets
description: "Characterizing marker sets template for WMBO."

classes:
  "sequence_feature": "SO:0000110"
  "regional part of brain": "UBERON:0002616"

relations:
  has_part: "BFO:0000051"

vars:
  Brain_region: "'regional part of brain'"
  Parent: "'thing'"

list_vars:
  Markers: "'sequence_feature'"

data_vars:
  Marker_set_of: "xsd:string"
  FBeta_confidence_score: "xsd:float"
  precision: "xsd:float"
  recall: "xsd:float"
  Algorithm: "xsd:string"
  Markers_label: "xsd:string"
```

**Annotation Properties**:
```yaml
annotationProperties:
  fbetaConfidenceScore: "STATO:0000663"
  has_precision: "STATO:0000416"
  has_recall: "CLM:0010004"
  algorithm: "IAO:0000064"
```

### Template Data Structure

**Sample Marker Set Data**:
```tsv
defined_class	Marker_set_of	Markers	Markers_label	FBeta_confidence_score	Algorithm	precision	recall
CLM_5004314	HY Gnrh1 Glut	NCBIGene:14714	Gnrh1	0.95	scRNA-seq	0.87	0.92
PCL_0120775	MB Dopa	NCBIGene:13162|NCBIGene:18208	Slc6a3,Ntn1	0.88	NS-Forest	0.91	0.85
PCL_0120776	MB-HB Sero	NCBIGene:14462|NCBIGene:16917	Gata3,Lmx1b	0.92	Evidence	0.89	0.94
```

**Data Fields**:
- **defined_class**: Ontology term IRI (CLM: prefix for marker sets)
- **Marker_set_of**: Target cell type for the marker set
- **Markers**: Pipe-separated list of gene identifiers (NCBIGene:)
- **Markers_label**: Human-readable gene symbols
- **FBeta_confidence_score**: Statistical confidence measure
- **Algorithm**: Source algorithm (scRNA-seq, NS-Forest, Evidence)
- **precision/recall**: Performance metrics

## Integration in Cell Type Patterns

### Main Class Template Usage
In `taxonomy_class.yaml`, markers are integrated through multiple variables:

```yaml
list_vars:
  Minimal_markers: "'sequence_feature'"
  Allen_markers: "'sequence_feature'"

# Used in cell type definitions
annotations:
  - annotationProperty: 'has minimal marker'
    text: "%s"
    vars:
      - Minimal_markers

  - annotationProperty: has_marker_set
    text: "%s"
    vars:
      - marker_gene_set
```

### Marker Confidence Integration
```yaml
data_vars:
  marker_gene_set_confidence: "xsd:float"
  nsforest_marker_gene_set_1_confidence: "xsd:float"
  ws_marker_gene_set_confidence: "xsd:float"

# Confidence scores in annotations
annotations:
  - annotationProperty: fbetaConfidenceScore
    text: "%s"
    vars:
      - marker_gene_set_confidence
```

## Build Integration

### Makefile Workflow
```makefile
# From src/dendrograms/Makefile
../patterns/data/default/%_marker_set.tsv: %.json
	python ../scripts/template_runner.py generator -ms -i $< -o $@

../patterns/data/default/%_nsforest_marker_set.tsv: %.json
	python ../scripts/template_runner.py generator -nms -i $< -o $@

../patterns/data/default/%_within_subclass_marker_set.tsv: %.json
	python ../scripts/template_runner.py generator -wsms -i $< -o $@

../patterns/data/default/%_evidence_marker_set.tsv: %.json
	python ../scripts/template_runner.py generator -ems -i $< -o $@
```

### ODK Integration (`wmbo.Makefile`)
```makefile
# Marker set component generation
components/%_marker_set.owl: ../patterns/data/default/%_marker_set.tsv
	$(DOSDPT) generate --template=../patterns/dosdp-patterns/taxonomy_marker_set.yaml \
		--infile=$< --outfile=$@

# Integration into main ontology
$(PATTERNDIR)/definitions.owl: $(TSV_CLASS_FILES)
	$(ROBOT) merge $(addprefix -i , $^) \
		annotate --ontology-iri $(ONTBASE)/patterns/definitions.owl
```

## Final OWL Output

### Marker Set Classes (CLM: namespace)
```owl
[Term]
id: CLM:5004314
name: Gnrh1 (Yao)
def: "Marker set for HY Gnrh1 Glut cell type" []
property_value: STATO:0000663 "0.95" xsd:float
property_value: IAO:0000064 "scRNA-seq" xsd:string
relationship: BFO:0000051 NCBIGene:14714
relationship: CLM:0010003 PCL:0110015
```

### Cell Type-Marker Relationships
```owl
[Term]
id: PCL:0110015
name: HY Gnrh1 Glut
relationship: RO:0015004 CLM:5004314  # has_characterizing_marker_set
property_value: PCL:0010058 "NCBIGene:14714" xsd:string  # has nsforest marker
property_value: PCL:0010066 "Gnrh1" xsd:string  # has minimal marker
property_value: STATO:0000663 "0.95" xsd:float  # fbetaConfidenceScore
```

### Gene Annotations
```owl
[Term]
id: NCBIGene:14714
name: Gnrh1
def: "Gonadotropin releasing hormone 1" []
property_value: IAO:0000028 "Gnrh1" xsd:string  # symbol
relationship: RO:0002292 PCL:0110015  # expressed_in
```

## Quality Assurance Features

### Confidence Scoring
- **F-beta scores**: Statistical measure of marker reliability
- **Precision/Recall**: Performance metrics for marker sets
- **Algorithm attribution**: Tracks source of marker identification

### Cross-Validation
- **Allen Brain Atlas**: External validation of marker expression
- **Multiple algorithms**: NS-Forest, evidence-based, within-subclass analysis
- **Manual curation**: Expert review of high-impact markers

### Hierarchical Consistency
- **Inheritance validation**: Child types inherit appropriate parent markers
- **Redundancy removal**: Prevents duplicate marker associations
- **Confidence propagation**: Maintains statistical measures through hierarchy

## Marker Categories

### 1. Minimal Markers (`Minimal_markers`)
- Core genes sufficient for cell type identification
- High specificity and sensitivity
- Used for computational cell type annotation

### 2. Allen Markers (`Allen_markers`)
- Cross-referenced with Allen Brain Atlas
- Spatial expression validation
- Anatomical context integration

### 3. Neurotransmitter Markers (`NT_markers`)
- Genes related to neurotransmitter synthesis/transport
- Chemical signaling characterization
- Functional classification support

### 4. Confidence-Weighted Markers
- **High confidence**: FBeta > 0.9, precision > 0.85
- **Medium confidence**: FBeta 0.7-0.9
- **Supporting evidence**: Additional validation markers

## Integration Points

### Ensembl Gene Database
- **Gene ID validation**: NCBIGene: identifier verification
- **Symbol mapping**: Gene symbol standardization
- **Functional annotation**: GO term integration

### Cell Ontology (CL)
- **Cross-references**: Links to standard cell type definitions
- **Marker validation**: Consistency with established cell type markers
- **Hierarchical alignment**: Parent-child marker inheritance

### Brain Atlas Integration
- **Spatial validation**: Expression patterns in anatomical context
- **Interactive visualization**: Web-based marker expression browsers
- **Data provenance**: Links to source experimental data

## Summary

The WMBO marker content system provides:

1. **Multi-algorithmic approach**: NS-Forest, evidence-based, differential expression
2. **Statistical rigor**: F-beta confidence scores, precision/recall metrics
3. **Hierarchical consistency**: Marker inheritance and validation
4. **Quality assurance**: Multiple validation layers and cross-references
5. **Computational accessibility**: Structured data for automated analysis
6. **Biological relevance**: Functionally significant marker genes
7. **Standard compliance**: Integration with established gene and ontology databases

This comprehensive marker system enables both computational cell type annotation and biological interpretation, providing a robust foundation for mouse brain cell type classification.