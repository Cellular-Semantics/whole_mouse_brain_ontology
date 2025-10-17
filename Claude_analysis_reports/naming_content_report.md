# Naming/Label Generation Content Report - WMBO

## Overview

The Whole Mouse Brain Ontology (WMBO) implements a sophisticated naming and label generation system that creates human-readable labels while maintaining formal ontological structure. This report details how cell type names are generated, formatted, validated, and integrated into the final ontology with multiple naming schemes and quality controls.

## Data Sources

### Primary Naming Sources
- **BICAN Taxonomy**: Brain Initiative Cell Census Network official cell type names
- **Cluster IDs**: CS20230722_CLUS_XXXX format cluster identifiers
- **Preferred Aliases**: Human-curated cell type names from taxonomy
- **Marker-based Names**: Names incorporating characteristic gene markers

### Naming Hierarchies
- **Taxonomy Labels**: Original hierarchical names from source data
- **Preferred Labels**: Human-readable formatted names (prefLabel)
- **Synonyms**: Alternative names and historical aliases
- **Class Names**: Formal ontology class identifiers

### Curation Sources
- **One Concept One Name**: `src/dendrograms/supplementary/version2/one_concept_one_name_curation.tsv`
- **Nomenclature Tables**: Manual curator annotations
- **Cross-species Alignment**: Comparative naming across species

## Processing Scripts

### 1. Label Formatting (`template_generation_utils.py`)

**Function**: `format_cell_label()`
- Removes numeric prefixes from taxonomy names
- Ensures label uniqueness across the ontology
- Applies marker-based disambiguation
- Handles collapsed hierarchical chains

**Code Extract**:
```python
def format_cell_label(cell_label, node, all_labels, generated_labels,
                     is_collapsed=False, fail_on_duplicate=True):
    """
    Formats cell labels to remove heading numbers and make labels unique
    by applying markers for disambiguation.
    """
    # Remove numeric prefixes (e.g., "0001 Cell Type" -> "Cell Type")
    formatted_label = remove_numeric_prefix(cell_label)

    # Check for uniqueness
    if formatted_label in all_labels or formatted_label in generated_labels:
        # Apply marker-based disambiguation
        formatted_label = apply_marker_disambiguation(formatted_label, node)

    return formatted_label
```

**Processing Logic**:
1. Remove leading numeric codes (e.g., "0001 ", "142 ")
2. Check label uniqueness in existing label sets
3. Apply marker-based suffixes for disambiguation
4. Handle collapsed node chains in hierarchies
5. Validate against reserved terms and conflicts

### 2. Nomenclature Annotation (`annotate_nomenclature.py`)

**Function**: `align_nomenclatures()`
- Migrates annotations between nomenclature versions
- Maintains naming consistency across updates
- Transfers curator annotations to new taxonomies

**Code Extract**:
```python
def align_nomenclatures(old_nomenclature, new_nomenclature):
    old_data = read_csv_to_dict(old_nomenclature)
    new_data = read_csv_to_dict(new_nomenclature)

    for accession_id in new_data:
        label = new_data[accession_id]["cell_set_preferred_alias"]
        old_record = find_old_data_counterpart(label, old_data)

        if old_record:
            # Migrate annotations (MBA, NT, etc.)
            migrate_annotations(new_data[accession_id], old_record)
```

**Alignment Methods**:
- **Sequence matching**: Levenshtein distance for name similarity
- **Pattern matching**: Regular expressions for systematic naming
- **Manual curation**: Expert-reviewed name mappings

### 3. Nomenclature Formatting (`nomenclature_formatter.py`)

**Functions**:
- `convert_tsv_to_csv()`: Format conversion between naming tables
- `reformat_csv()`: Standardize nomenclature table formats
- `log_root_nodes()`: Generate configuration for hierarchical naming

**Processing Features**:
- Format standardization across nomenclature versions
- Quotation and delimiter handling
- Hierarchical relationship preservation

## Template Integration

### DOSDP Pattern: taxonomy_class.yaml

**Label Properties**:
```yaml
annotationProperties:
  skosPrefLabel: "skos:prefLabel"
  hasExactSynonym: "oboInOwl:hasExactSynonym"
  rdfsComment: "rdfs:comment"
  rdfsLabel: "rdfs:label"
  seeAlso: "rdfs:seeAlso"
  hasDbXref: "oboInOwl:hasDbXref"
  symbol: "IAO:0000028"

data_vars:
  prefLabel: "xsd:string"
  Taxonomy_label: "xsd:string"
  Synonyms_from_taxonomy: "xsd:string"
  Class_name: "xsd:string"
  Parent_label: "xsd:string"
```

**Label Generation Logic**:
```yaml
name:
  text: "%s"
  vars:
    - prefLabel

annotations:
  - annotationProperty: skosPrefLabel
    text: "%s"
    vars:
      - prefLabel

  - annotationProperty: hasExactSynonym
    text: "%s"
    vars:
      - Synonyms_from_taxonomy

  - annotationProperty: rdfsLabel
    text: "h5ad data file for %s"
    vars:
      - Class_name
```

### Template Data Structure

**Naming Fields in CCN20230722_class_base.tsv**:
- **defined_class**: Formal ontology IRI (e.g., PCL_0110001)
- **prefLabel**: Primary human-readable name ("IT-ET Glut")
- **Taxonomy_label**: Original taxonomy name ("01 IT-ET Glut")
- **Synonyms_from_taxonomy**: Alternative names from source
- **Class_name**: Standardized class identifier ("CS20230722_CLAS_01")
- **Parent_label**: Parent class name in hierarchy
- **aligned_alias**: Cross-reference aliases

### Sample Template Data
```tsv
defined_class	prefLabel	Taxonomy_label	Synonyms_from_taxonomy	Class_name	Parent_label
PCL_0110001	IT-ET Glut	01 IT-ET Glut	01 IT-ET Glut	CS20230722_CLAS_01	neuron
PCL_0110015	HY Gnrh1 Glut	2564 HY Gnrh1 Glut_1	0628 HY Gnrh1 Glut_1|142 HY Gnrh1 Glut|15 HY Gnrh1 Glut|2564 HY Gnrh1 Glut_1	CS20230722_CLAS_15	glutamatergic neuron
```

## Naming Conventions and Rules

### 1. Anatomical Abbreviations
**Standard Abbreviations**:
- **IT**: Intratelencephalic
- **ET**: Extratelencephalic
- **HY**: Hypothalamus
- **CLA**: Claustrum
- **CTX**: Cortex
- **OB**: Olfactory bulb
- **CB**: Cerebellum
- **MB**: Midbrain
- **TH**: Thalamus

### 2. Neurotransmitter Designation
**Neurotransmitter Naming**:
- **Glut**: Glutamatergic (excitatory)
- **GABA**: GABAergic (inhibitory)
- **Dopa**: Dopaminergic
- **Sero**: Serotonergic
- **Mixed types**: Multiple neurotransmitter systems

### 3. Marker-Based Naming
**Gene Marker Integration**:
- Primary markers in cell type names (e.g., "Gnrh1")
- Disambiguating suffixes for similar types
- Confidence-based marker selection

### 4. Hierarchical Naming
**Level-Based Conventions**:
- **Class**: Broad cell type categories (e.g., "IT-ET Glut")
- **Subclass**: Refined subcategories
- **Cluster**: Specific cell clusters with markers

## Label Validation and Quality Control

### 1. Uniqueness Validation
```python
def ensure_label_uniqueness(label, existing_labels):
    if label in existing_labels:
        # Apply disambiguation strategy
        label = apply_marker_suffix(label)

    if label in existing_labels:
        # Fallback to numeric suffix
        label = apply_numeric_suffix(label)

    return label
```

### 2. Format Validation
**Naming Pattern Checks**:
- No leading/trailing whitespace
- Proper capitalization conventions
- Valid character sets (alphanumeric, spaces, hyphens)
- Length constraints (readable but not excessive)

### 3. Cross-Reference Validation
**Consistency Checks**:
- Alignment with parent/child naming
- Consistency with anatomical location
- Neurotransmitter name validation
- Marker gene name accuracy

## Curation Integration

### One Concept One Name System
**File**: `one_concept_one_name_curation.tsv`
**Purpose**: Manual curator assignments for identical cell sets

**Processing Logic**:
```python
def apply_one_concept_one_name(cell_sets):
    curation_map = read_one_concept_one_name_tsv()

    for cell_set_group in curation_map:
        # Assign single name to identical cell sets
        canonical_name = cell_set_group['preferred_name']
        for cell_set in cell_set_group['members']:
            cell_set['curated_name'] = canonical_name
```

### Manual Nomenclature Curation
**Expert Review Process**:
1. Initial automated naming from taxonomy
2. Expert review for biological accuracy
3. Cross-species consistency checking
4. Final curator approval and annotation

## Final OWL Output

### Primary Labels
```owl
[Term]
id: PCL:0110015
name: HY Gnrh1 Glut
property_value: skos:prefLabel "HY Gnrh1 Glut" xsd:string
property_value: rdfs:label "HY Gnrh1 Glut" xsd:string
property_value: IAO:0000028 "HY Gnrh1 Glut" xsd:string
```

### Synonyms and Alternative Names
```owl
synonym: "15 HY Gnrh1 Glut" EXACT []
synonym: "2564 HY Gnrh1 Glut_1" EXACT []
synonym: "0628 HY Gnrh1 Glut_1" EXACT []
synonym: "142 HY Gnrh1 Glut" EXACT []
property_value: oboInOwl:hasExactSynonym "hypothalamic gonadotropin releasing hormone neuron" xsd:string
```

### Cross-References
```owl
xref: "CS20230722_CLAS_15"
xref: "https://purl.brain-bican.org/taxonomy/CCN20230722/CS20230722_CLAS_15"
property_value: seeAlso "https://knowledge.brain-map.org/abcatlas#..." xsd:anyURI
```

## Build Integration

### Makefile Processing
```makefile
# From src/dendrograms/Makefile
../patterns/data/default/%_class_curation.tsv: %.json
	python ../scripts/template_runner.py generator -cc -i $< -o $@

# Label formatting and validation
$(REPORTDIR)/naming_validation.txt: $(EDIT_PREPROCESSED)
	python $(SCRIPTSDIR)/nomenclature_validator.py \
		--input $< --output $@
```

### Template Generation Pipeline
```makefile
# Class template with formatted labels
../patterns/data/default/%_class_base.tsv: %.json $(SUPPLEMENTARY)/version2/neurotransmitters.tsv
	python ../scripts/template_runner.py generator -cb -i $< -o $@
```

## Naming System Features

### 1. Multi-Level Labeling
**Hierarchical Naming**:
- **Formal names**: Ontology class identifiers (PCL:0110015)
- **Preferred labels**: Human-readable primary names ("HY Gnrh1 Glut")
- **Taxonomy labels**: Source hierarchical names ("2564 HY Gnrh1 Glut_1")
- **Synonyms**: Alternative and historical names

### 2. Disambiguation Strategies
**Conflict Resolution**:
- **Marker-based**: Add gene markers to distinguish similar types
- **Location-based**: Add anatomical context for clarity
- **Numeric suffixes**: Last resort for remaining conflicts
- **Hierarchical context**: Use parent class information

### 3. Cross-Species Consistency
**Comparative Naming**:
- Alignment with human and other species taxonomies
- Consistent terminology across BRAIN Initiative projects
- Standard anatomical and molecular terminology

### 4. Provenance Tracking
**Name Source Documentation**:
- Original taxonomy source tracking
- Curator modification history
- Cross-reference maintenance
- Version migration documentation

## Quality Assurance

### 1. Automated Validation
- **Pattern matching**: Consistent naming conventions
- **Uniqueness checking**: No duplicate labels
- **Format validation**: Proper capitalization and formatting
- **Cross-reference validation**: Link consistency

### 2. Manual Curation
- **Expert review**: Biological accuracy verification
- **Naming consistency**: Systematic terminology usage
- **Documentation**: Rationale for naming decisions
- **Version control**: Change tracking and approval

### 3. Community Standards
- **FAIR principles**: Findable, Accessible, Interoperable, Reusable
- **OBO standards**: Open Biological Ontologies naming conventions
- **Brain Initiative**: Community-approved terminology
- **Allen Institute**: Atlas naming consistency

## Summary

The WMBO naming/label generation system provides:

1. **Multi-level naming**: Formal, preferred, and synonym labels
2. **Automated formatting**: Consistent naming conventions
3. **Quality validation**: Uniqueness and format checking
4. **Curation integration**: Expert review and manual annotation
5. **Provenance tracking**: Source and modification history
6. **Standards compliance**: OBO and community conventions
7. **Cross-reference maintenance**: Links to external resources
8. **Disambiguation strategies**: Conflict resolution mechanisms

This comprehensive naming system ensures that brain cell types have consistent, meaningful, and biologically accurate names while maintaining formal ontological structure and supporting computational applications.