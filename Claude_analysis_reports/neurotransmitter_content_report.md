# Neurotransmitter Content Report - WMBO

## Overview

The Whole Mouse Brain Ontology (WMBO) integrates neurotransmitter information to classify brain cell types based on their chemical signaling properties. This report details how neurotransmitter data is sourced, processed, and incorporated into the final ontology.

## Data Sources

### Primary Source: Cluster Annotation Membership
- **File**: `src/dendrograms/supplementary/version2/cluster_to_cluster_annotation_membership.csv`
- **Source**: Brain Initiative Cell Census Network (BICAN) taxonomy project
- **Content**: Maps brain cell clusters to their neurotransmitter types

### Sample Source Data Structure
```csv
cluster_annotation_term_label,cluster_annotation_term_set_label,cluster_alias,cluster_annotation_term_name,cluster_annotation_term_set_name,number_of_cells,color_hex_triplet
CS20230722_CLUS_0001,CCN20230722_CLUS,128,0001 CLA-EPd-CTX Car3 Glut_1,cluster,4262,#00664E
CS20230722_NEUR_Glut,CCN20230722_NEUR,128,Glutamatergic,neurotransmitter,4262,#FF0000
```

### Neurotransmitter Types Identified
Based on analysis of the data:
- **Glutamatergic (Glut)**: Excitatory neurotransmitter
- **GABAergic (Gaba)**: Inhibitory neurotransmitter
- **Dopaminergic (Dopa)**: Modulatory neurotransmitter
- **Mixed types**: Some cells express multiple neurotransmitter systems

## Processing Scripts

### supplementary_data_processor.py
**Function**: `generate_neurotransmitter_data()`

**Processing Logic**:
1. Reads cluster annotation membership CSV
2. Filters records where `cluster_annotation_term_set_name == 'cluster'`
3. For each cluster, finds corresponding neurotransmitter annotations
4. Creates mapping between cluster labels and neurotransmitter labels
5. Outputs TSV file with cluster-to-neurotransmitter mappings

**Code Extract**:
```python
def generate_neurotransmitter_data(output_file: str):
    df = pd.read_csv(C2C_ANNOTATION_MEMBERSHIP)
    cluster_records = df[df['cluster_annotation_term_set_name'] == 'cluster']

    mapping = []
    for _, cluster_row in cluster_records.iterrows():
        cluster_alias = cluster_row['cluster_alias']
        neurotransmitter_record = df[(df['cluster_alias'] == cluster_alias) &
                                   (df['cluster_annotation_term_set_name'] == 'neurotransmitter')]
        if not neurotransmitter_record.empty:
            neurotransmitter_row = neurotransmitter_record.iloc[0]
            mapping.append({
                'cluster_label': cluster_row['cluster_annotation_term_label'],
                'neurotransmitter_label': neurotransmitter_row['cluster_annotation_term_label']
            })
```

**Output**: `src/dendrograms/supplementary/version2/neurotransmitters.tsv`

### Generated Neurotransmitter Mapping
```tsv
cluster_label	neurotransmitter_label
CS20230722_CLUS_0001	CS20230722_NEUR_Glut
CS20230722_CLUS_0002	CS20230722_NEUR_Glut
CS20230722_CLUS_0003	CS20230722_NEUR_Glut
CS20230722_CLUS_0004	CS20230722_NEUR_Glut
```

## Template Integration

### DOSDP Pattern: taxonomy_class.yaml
The neurotransmitter data is integrated through DOSDP pattern variables:

```yaml
list_vars:
  NT: "'thing'"
  NT_markers: "'sequence_feature'"
  NT_marker_1: "'thing'"
  NT_marker_2: "'thing'"
  NT_marker_3: "'thing'"
  NT_marker_4: "'thing'"
  NT_marker_5: "'thing'"
  NT_marker_6: "'thing'"
  NT_marker_7: "'thing'"
  NT_marker_8: "'thing'"
  NT_label: "xsd:string"
  NT_disclaimer: "xsd:string"

substitutions:
  - var_name: NT_cat
    input: NT
    apply:
      join:
        sep: ', '
  - var_name: NT_markers_cat
    input: NT_markers
    apply:
      join:
        sep: ', '
```

### Template Usage in Class Definitions
Neurotransmitter information appears in class annotations:

```yaml
annotations:
  - annotationProperty: rdfsComment
    text: >-
      multi_clause:
        sep: " "
        clauses:
          - text: 'Inferred to be %s based on expression of %s'
            vars:
              - NT_cat
              - NT_markers_cat
```

## Template Data Processing

### Integration in Class Base Template
In `src/patterns/data/default/CCN20230722_class_base.tsv`, neurotransmitter data appears in columns:

- **NT**: Neurotransmitter type (e.g., "GABAergic", "Glutamatergic")
- **NT_markers**: Gene markers for neurotransmitter synthesis/transport
- **NT_label**: Human-readable neurotransmitter label
- **NT_disclaimer**: Warning text about neurotransmitter classification accuracy
- **NT_marker_1** through **NT_marker_8**: Individual marker genes

### Sample Template Data
```tsv
defined_class	NT	NT_markers	NT_label	NT_disclaimer	NT_marker_1	NT_marker_2	NT_marker_3
PCL_0112963	GABAergic	Gad2|Gad1|Th|Slc32a1|Slc6a3|Slc18a2	GABAergic	Warning: Despite its name, OB Dopa-Gaba_1 AW551984 does not secrete the neurotransmitter Dopa, as assessed by expression of multiple marker genes.	NCBIGene:14417	NCBIGene:14415	NCBIGene:21823
```

## Final OWL Output

### Neurotransmitter Classification in Ontology
Neurotransmitter information is expressed through:

1. **Class Definitions**: Linking to Gene Ontology terms for neurotransmitter processes
2. **Annotations**: Human-readable descriptions of neurotransmitter properties
3. **Logical Axioms**: Formal relationships using the `capable_of` relation

### Sample OWL Output
```owl
[Term]
id: CL:4030027
name: GABAergic amacrine cell
def: "An amacrine cell that uses GABA as a neurotransmitter." [https://doi.org/10.1016/j.cell.2020.08.013]
synonym: "amacrine cell, GABAergic" EXACT []
is_a: CL:0000561
is_a: CL:0011005
intersection_of: CL:0000561
intersection_of: RO:0002215 GO:0061534
```

### Gene Ontology Integration
The ontology links to specific GO terms for neurotransmitter processes:
- **GO:0061534**: GABA neurotransmitter transport
- **GO:0015833**: peptide transport
- **GO:0019226**: transmission of nerve impulse

### Neurotransmitter Marker Genes
Key marker genes are encoded as individual assertions:
- **Gad1** (NCBIGene:14415): Glutamate decarboxylase 1
- **Gad2** (NCBIGene:14417): Glutamate decarboxylase 2
- **Slc32a1** (NCBIGene:22348): GABA transporter
- **Th** (NCBIGene:21823): Tyrosine hydroxylase (dopamine synthesis)
- **Slc6a3** (NCBIGene:13162): Dopamine transporter

## Quality Control Features

### Disclaimer Generation
The system includes quality control through disclaimer generation for ambiguous cases:

**Example**: "Warning: Despite its name, OB Dopa-Gaba_1 AW551984 does not secrete the neurotransmitter Dopa, as assessed by expression of multiple marker genes."

This indicates cases where:
1. Cell type names suggest one neurotransmitter type
2. Gene expression evidence contradicts the naming
3. Manual curation has identified discrepancies

### Validation Through Marker Expression
The system validates neurotransmitter classifications by:
1. Analyzing expression of neurotransmitter synthesis genes
2. Checking transport protein expression
3. Comparing naming conventions with molecular evidence
4. Generating warnings for inconsistencies

## Build Integration

### Makefile Dependencies
Neurotransmitter processing is integrated into the build system:

```makefile
# From src/dendrograms/Makefile
$(SUPPLEMENTARY)/version2/neurotransmitters.tsv:
	python ../scripts/supplementary_data_processor.py -nt -o $@

# Used in class base template generation
../patterns/data/default/%_class_base.tsv: %.json $(SUPPLEMENTARY)/version2/neurotransmitters.tsv
	python ../scripts/template_runner.py generator -cb -i $< -o $@
```

### Processing Flow
1. **Source data download**: CCN20230722.json contains cluster definitions
2. **Neurotransmitter mapping**: `supplementary_data_processor.py -nt` generates mappings
3. **Template generation**: Integrated into class base template creation
4. **DOSDP processing**: Pattern application creates logical axioms
5. **OWL assembly**: Final ontology includes neurotransmitter classifications

## Summary

The WMBO neurotransmitter content system provides:

1. **Data-driven classification**: Based on empirical cluster-to-neurotransmitter mappings
2. **Molecular validation**: Uses gene expression markers for verification
3. **Quality assurance**: Includes disclaimers for ambiguous cases
4. **Formal representation**: Expresses neurotransmitter properties as logical axioms
5. **Standards compliance**: Links to standard Gene Ontology terms

This approach ensures that neurotransmitter classifications in the ontology are grounded in experimental evidence while maintaining formal logical rigor appropriate for computational applications.