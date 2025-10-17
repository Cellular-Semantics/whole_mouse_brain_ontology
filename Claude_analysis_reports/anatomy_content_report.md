# Anatomy Content Report - WMBO

## Overview

The Whole Mouse Brain Ontology (WMBO) integrates anatomical location information to spatially characterize brain cell types using the Allen Mouse Brain Atlas Common Coordinate Framework (CCF). This report details how anatomical data is sourced, validated, and incorporated into the final ontology with quality control measures.

## Data Sources

### Primary Anatomical Framework
- **Allen Mouse Brain Atlas (MBA)**: Allen Common Coordinate Framework reference
- **Namespace**: MBA: prefix for anatomical regions (e.g., MBA:997 for whole brain)
- **Integration**: Uberon Ontology for standard anatomical terminology
- **Reference**: https://atlas.brain-map.org/ - Allen Brain Atlas spatial reference

### Spatial Data Sources
- **Cell type locations**: Derived from scRNA-seq spatial mapping
- **CCF coordinates**: Allen Common Coordinate Framework spatial assignments
- **Broad regions**: High-level anatomical divisions
- **Acronym regions**: Detailed anatomical subregions

### Anatomical Validation Sources
- **Mouse Brain Atlas Ontology (MBAO)**: `src/dendrograms/resources/mbao-base-materialized.owl`
- **Uberon integration**: Standard anatomical ontology terms
- **Manual curation**: Expert review of location assignments

## Processing Scripts

### 1. Anatomical Disclaimer Generation (`disclaimer_generator.py`)

**Function**: `get_anatomical_location_inconsistencies()`
- Analyzes cell type names against CCF spatial data
- Identifies anatomical inconsistencies in cell type naming
- Generates warnings for location assignment conflicts

**Code Extract**:
```python
def get_anatomical_location_inconsistencies(cluster_annotations_path: str) -> dict:
    """
    Returns cell sets names that include anatomical location unsupported by CCF.
    """
    clusters = pd.read_csv(cluster_annotations_path).dropna(subset=['cluster_id_label'])

    # Load materialized brain ontology
    mba_ontology = Graph()
    mba_ontology.parse(MBAO_PATH, format="xml")

    # Check cell type names against spatial assignments
    inconsistencies = validate_location_assignments(clusters, mba_ontology)

    return inconsistencies
```

**Processing Logic**:
1. Parse cell type cluster annotations
2. Load Allen Mouse Brain Atlas ontology (materialized)
3. Compare cell type names with spatial coordinate data
4. Flag inconsistencies between names and locations
5. Generate location disclaimer text

### 2. Location Symbol Processing
**Function**: `get_location_symbols()`
- Extracts anatomical abbreviations from cell type names
- Maps symbols to standard MBA identifiers
- Validates anatomical term usage

**Anatomical Abbreviations Used**:
- **HY**: Hypothalamus
- **CLA**: Claustrum
- **CTX**: Cortex
- **EPd**: Endopiriform nucleus
- **OB**: Olfactory bulb
- **CB**: Cerebellum
- **MY**: Medulla
- **P**: Pons
- **TH**: Thalamus
- **MB**: Midbrain

## Template Integration

### DOSDP Pattern: taxonomy_class.yaml

**Anatomical Variables**:
```yaml
classes:
  "regional part of brain": "UBERON:0002616"
  "layer of neocortex": "UBERON:0002301"

relations:
  part_of: "BFO:0000050"
  has_soma_location: "RO:0002100"

vars:
  Brain_region: "'regional part of brain'"

list_vars:
  Locations: "'layer of neocortex'"
  MBA: "'thing'"
  CCF_acronym_freq: "'thing'"

data_vars:
  Brain_region_abbv: "xsd:string"
  Location_disclaimer: "xsd:string"
  MBA_text: "xsd:string"
```

**Anatomical Relationships**:
```yaml
logical_axioms:
  - axiom_type: subClassOf
    text: "'has_soma_location' some %s"
    vars:
      - has_soma_location

annotations:
  - annotationProperty: rdfsComment
    text: "%s"
    vars:
      - Location_disclaimer
```

### Template Data Structure

**Anatomical Fields in CCN20230722_class_base.tsv**:
- **Brain_region**: Primary anatomical assignment (MBA:997)
- **Brain_region_abbv**: Abbreviated region name ("MOp")
- **has_soma_location**: Formal anatomical location (MBA identifier)
- **part_of**: Hierarchical anatomical relationships
- **MBA**: Multi-region assignments with percentages
- **MBA_text**: Human-readable location descriptions
- **Location_disclaimer**: Quality control warnings
- **MBA_1 through MBA_10**: Detailed regional distributions
- **CCF_acronym_freq**: Fine-grained anatomical assignments

### Sample Template Data
```tsv
defined_class	Brain_region	has_soma_location	MBA	MBA_text	Location_disclaimer	MBA_1	MBA_1_cell_percentage	MBA_1_comment
PCL_0110015	MBA:997	MBA:997	MBA:1097|MBA:698|MBA:803	hypothalamus (HY, 0.22), olfactory areas (OLF, 0.11), pallidum (PAL, 0.42)		MBA:1097	0.22	Location assignment based on CCF broad region.
```

## Anatomical Quality Control

### 1. Location Assignment Validation
**Validation Types**:
- **Name vs. Location**: Cell type names checked against spatial data
- **CCF Consistency**: Coordinate assignments validated
- **Hierarchical Validation**: Parent-child region relationships
- **Percentage Thresholds**: Minimum 10% cell presence for region assignment

**Example Quality Issues**:
```
Location_disclaimer: "Warning: Despite its name, OB Dopa-Gaba_1 AW551984 does not secrete the neurotransmitter Dopa, as assessed by expression of multiple marker genes."
```

### 2. Multi-Region Cell Types
**Spatial Distribution Analysis**:
- **Primary regions**: Regions with >50% cell presence
- **Secondary regions**: Regions with 10-50% cell presence
- **Trace regions**: Regions with <10% cell presence (excluded)

**Example Multi-Region Assignment**:
```
MBA_text: "hypothalamus (HY, 0.22), olfactory areas (OLF, 0.11), pallidum (PAL, 0.42), brain (NA, 0.14)"
```

### 3. CCF Integration Levels
**Hierarchical Mapping**:
- **Broad regions**: Major brain divisions (MBA:1097 = hypothalamus)
- **Acronym regions**: Detailed subregions (MBA:258 = specific nucleus)
- **Full brain fallback**: MBA:997 (whole brain) when location unclear

## Final OWL Output

### Anatomical Class Definitions
```owl
[Term]
id: PCL:0110015
name: HY Gnrh1 Glut
relationship: RO:0002100 MBA:1097  # has_soma_location hypothalamus
relationship: BFO:0000050 MBA:997  # part_of brain
property_value: IAO:0000115 "A glutamatergic neuron located in hypothalamus" xsd:string
```

### Anatomical Annotations
```owl
property_value: rdfsComment "Location assignment based on CCF broad region." xsd:string
property_value: IAO:0000115 "hypothalamus (HY, 0.22), olfactory areas (OLF, 0.11)" xsd:string
```

### Spatial Distribution Properties
```owl
# Detailed regional assignments
property_value: CLM:0010001 "MBA:1097" xsd:string  # some_soma_located_in
property_value: STATO:0000416 "0.22" xsd:float     # precision for region 1
property_value: STATO:0000416 "0.11" xsd:float     # precision for region 2
```

## Build Integration

### Makefile Processing
```makefile
# From src/dendrograms/Makefile - Location disclaimer generation
../patterns/data/default/%_class_base.tsv: %.json $(SUPPLEMENTARY)/version2/neurotransmitters.tsv
	python ../scripts/template_runner.py generator -cb -i $< -o $@
```

### Quality Control Pipeline
```makefile
# Anatomical validation through disclaimer generation
$(REPORTDIR)/location_validation.txt: $(EDIT_PREPROCESSED)
	python $(SCRIPTSDIR)/disclaimer_generator.py \
		--anatomical-validation \
		--input $< --output $@
```

## Anatomical Term Sources

### Allen Mouse Brain Atlas (MBA)
**Key Regions**:
- **MBA:997**: Brain (whole brain)
- **MBA:1097**: Hypothalamus
- **MBA:698**: Olfactory areas
- **MBA:803**: Pallidum
- **MBA:315**: Isocortex
- **MBA:258**: Specific hypothalamic nuclei
- **MBA:564**: Pallidum subregions

### Uberon Integration
**Standard Terms**:
- **UBERON:0002616**: Regional part of brain
- **UBERON:0002301**: Layer of neocortex
- **UBERON:0016405**: Anatomical junction

**Relationship Properties**:
- **RO:0002100**: has_soma_location
- **BFO:0000050**: part_of
- **RO:0002162**: in_taxon

## Spatial Validation Features

### 1. CCF Coordinate Validation
- **Source**: Allen Common Coordinate Framework
- **Method**: Cell type spatial coordinates vs. named locations
- **Threshold**: Minimum 10% cell presence for region assignment
- **Output**: Location disclaimer for inconsistencies

### 2. Hierarchical Consistency
- **Parent-Child**: Regional hierarchies must be consistent
- **Example**: Hypothalamic nucleus must be part_of hypothalamus
- **Validation**: Automated checking via MBAO ontology

### 3. Multi-Modal Validation
- **Molecular**: Gene expression patterns support location
- **Spatial**: Physical coordinates align with region assignments
- **Functional**: Cell type function consistent with location

## Location Assignment Workflow

### 1. Primary Assignment
```python
# Brain region assignment based on cell density
primary_region = assign_primary_location(cell_coordinates, ccf_regions)
if cell_percentage > 0.5:
    primary_assignment = primary_region
else:
    primary_assignment = "MBA:997"  # whole brain fallback
```

### 2. Secondary Assignments
```python
# Multi-region assignments for distributed cell types
secondary_regions = []
for region, percentage in region_distribution.items():
    if percentage > BRAIN_REGION_THRESHOLD:  # 0.1 = 10%
        secondary_regions.append((region, percentage))
```

### 3. Quality Control
```python
# Location disclaimer generation
if name_location != ccf_location:
    disclaimer = f"Location assignment based on CCF {assignment_level} region."
```

## Integration Points

### Allen Brain Atlas
- **Spatial coordinates**: CCF-based cell locations
- **Region ontology**: Hierarchical brain region definitions
- **Validation data**: Independent spatial expression data

### Uberon Ontology
- **Standard terms**: Cross-species anatomical vocabulary
- **Relationships**: Formal part_of hierarchies
- **Interoperability**: Links to other anatomical ontologies

### Brain Initiative
- **BICAN taxonomy**: Brain Initiative Cell Census Network spatial data
- **Multi-species**: Cross-species anatomical comparisons
- **Standards**: Community-approved anatomical vocabularies

## Summary

The WMBO anatomy content system provides:

1. **Spatial precision**: Allen CCF-based anatomical assignments
2. **Quality assurance**: Automated inconsistency detection and disclaimers
3. **Multi-scale integration**: From whole brain to specific nuclei
4. **Standard compliance**: Uberon and Allen ontology integration
5. **Hierarchical consistency**: Parent-child anatomical relationships
6. **Percentage-based assignments**: Quantitative regional distributions
7. **Cross-validation**: Multiple data sources confirm locations

This comprehensive anatomical framework ensures that cell type classifications are spatially accurate and consistent with established neuroanatomical knowledge while maintaining computational tractability for large-scale brain analyses.