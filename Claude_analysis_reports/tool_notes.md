# Whole Mouse Brain Ontology - Ontology Generation Report

## Overview

The Whole Mouse Brain Ontology (WMBO) project constructs a data-driven cell-type ontology of the whole mouse brain based on Yao et al. (2023) research. This report documents how the repository generates ontology content, covering inputs, templates, scripts, workflows, and final outputs.

## Architecture and Tool Stack

### Core Technologies
- **Ontology Development Kit (ODK)**: Provides the foundational framework for ontology management and builds
- **ROBOT**: Command-line tool for ontology processing, template conversion, and reasoning
- **DOSDP (Dead Simple OWL Design Patterns)**: Pattern-based ontology term generation using YAML templates
- **dosdp-tools**: Command-line utility for processing DOSDP patterns and generating ontology axioms

### Programming Languages
- **Python**: Custom processing scripts for data transformation and template generation
- **TypeScript**: Web interface components for ABC Atlas integration
- **Make**: Build automation and workflow orchestration

## Repository Structure

```
whole_mouse_brain_ontology/
├── src/
│   ├── ontology/           # Main ontology build directory (ODK standard)
│   ├── patterns/           # DOSDP pattern definitions and data
│   ├── templates/          # ROBOT template files
│   ├── scripts/            # Custom Python processing scripts
│   ├── dendrograms/        # Source data and build orchestration
│   ├── sparql/             # SPARQL queries for ontology processing
│   └── metadata/           # Configuration and metadata files
├── typescript/             # Web interface components
├── docs/                   # Documentation
└── [output files]          # Generated ontology products
```

## Data Sources and Inputs

### Primary Data Source
- **CCN20230722.json**: Main taxonomy JSON file downloaded from brain-bican/whole_mouse_brain_taxonomy repository
- Contains hierarchical cell type classifications with ~5000+ cell types

### Supplementary Data
- **Neurotransmitter data**: Generated via `supplementary_data_processor.py`
- **Curation tables**: Manual curator edits for cell type naming and CL ontology integration
- **Google Sheets**: External curation data imported via `google_sheets_to_tsv.py`

### External Ontology Imports
- **RO (Relations Ontology)**: Relationship definitions
- **BFO (Basic Formal Ontology)**: Upper-level ontological framework
- **PATO**: Quality and attribute ontology
- **Gene databases**: Ensembl gene information via custom `ensembl.py` script

## Workflow and Generation Process

### 1. Data Preparation Phase
Located in `src/dendrograms/`:

1. **Sheets Import**: `google_sheets_to_tsv.py` exports Google Sheets to TSV format
2. **Source Data Download**: Fetches `CCN20230722.json` from remote repository
3. **ABC Atlas URL Generation**: TypeScript components generate web interface links
4. **Supplementary Data**: Processes neurotransmitter and curation data

### 2. Template Generation Phase

#### DOSDP Pattern Templates
- **taxonomy_class.yaml**: Core cell type class pattern (18KB+ complex pattern)
- **taxonomy_marker_set.yaml**: Marker gene set associations
- **taxonomy_class_obsolete.yaml**: Obsolete term handling

#### Template Data Files Generated
- `CCN20230722_class_base.tsv`: Base cell type definitions (14.6MB)
- `CCN20230722_class_curation.tsv`: Curator modifications (601KB)
- `CCN20230722_marker_set.tsv`: Marker gene associations (1.9MB)
- `CCN20230722_within_subclass_marker_set.tsv`: Subclass-specific markers (1.7MB)
- `CCN20230722_nsforest_marker_set.tsv`: NS-Forest algorithm markers (107KB)
- `CCN20230722_evidence_marker_set.tsv`: Evidence-based markers (1.3KB)

#### Template Processing Tools
- **template_runner.py**: Main CLI for template generation with multiple modes:
  - Base class template generation (`-cb`)
  - Curation template generation (`-cc`)
  - Marker set template generation (`-ms`, `-nms`, `-wsms`, `-ems`)
  - Template merging (`modifier --merge`)

### 3. Ontology Building Phase
Located in `src/ontology/`:

#### Standard ODK Workflow (Makefile)
- **Robot Template Processing**: Converts TSV templates to OWL using ROBOT
- **DOSDP Pattern Application**: Uses dosdp-tools to generate ontology axioms
- **Import Processing**: Integrates external ontologies (RO, BFO, PATO)
- **Reasoning**: ELK reasoner for consistency checking and classification
- **Quality Assurance**: SPARQL validation queries and robot reports

#### Custom Extensions (wmbo.Makefile)
- **Gene Import Pipeline**: Custom processing for Ensembl gene data
- **Component Assembly**: Merges multiple OWL files into final products
- **Marker Set Integration**: Specialized handling for different marker types
- **Prefix Management**: Custom prefix handling via `template_prefixes.yaml`

### 4. Key Processing Scripts

#### Python Scripts (`src/scripts/`)
- **ensembl.py**: Gene database processing and import term generation
- **template_generation_tools.py**: Core template generation functions
- **marker_tools.py**: Marker gene processing and validation
- **cl_subset_terms.py**: Cell ontology integration
- **disclaimer_generator.py**: Legal/usage disclaimer generation

#### Build Orchestration
- **run.sh**: Docker-based build execution
- **wmbo.Makefile**: Custom make targets and processing rules
- **src/dendrograms/Makefile**: Data preparation and template generation

## Output Products

### Final Ontology Files
- **wmbo-base.obo/json**: Full ontology with all annotations (26.4MB OBO, 68.7MB JSON)
- **wmbo-cl-comp.owl/obo/json**: Cell ontology compatible subset
- **wmbo-full**: Complete ontology with imports (defined in ODK config)

### Intermediate Products
- **Pattern OWL files**: Generated from DOSDP patterns
- **Component OWL files**: Modular ontology components
- **Import modules**: Extracted relevant terms from external ontologies
- **Validation reports**: Quality assurance and consistency reports

## Key Design Patterns

### DOSDP Integration
The system heavily uses DOSDP for consistent term generation:
- **Pattern Templates**: YAML files defining logical structures
- **Data Tables**: TSV files with variable bindings
- **Automated Generation**: dosdp-tools processes patterns + data → OWL axioms

### Modular Architecture
- **Components**: Separate OWL files for different aspects (individuals, classes, marker sets)
- **Imports**: External ontology integration via ODK import pipeline
- **Templates**: ROBOT templates for structured data conversion

### Data-Driven Approach
- **JSON Source**: Hierarchical taxonomy data drives ontology structure
- **Marker Integration**: Multiple marker gene algorithms integrated
- **Curation Layer**: Human curator input overlays automated generation

## Build Commands and Usage

### Full Build
```bash
sh run.sh make all_odk    # Complete ontology build
```

### Selective Builds
```bash
make test                 # Run validation and tests
make reason_test         # Reasoning validation
make custom_reports      # Generate quality reports
```

### Data Regeneration
```bash
cd src/dendrograms && make  # Regenerate templates from source data
```

## Dependencies and Requirements

### External Tools (via Docker)
- ROBOT ontology toolkit
- dosdp-tools
- ELK reasoner
- SPARQL processors

### Python Dependencies
- pandas, requests (data processing)
- Custom modules for brain data processing

### TypeScript Dependencies
- React components for web interface
- Apollo client for GraphQL integration
- Kiwi schema for data validation

## Quality Assurance

### Automated Validation
- **SPARQL queries**: 7+ validation checks including IRI validation, label consistency
- **Reasoning tests**: ELK reasoner validation
- **Robot reports**: Automated quality reports
- **Profile validation**: OWL2 DL compliance checking

### Manual Curation Points
- **Nomenclature curation**: `nomenclature_formatter.py`
- **Marker validation**: `marker_validator.py`
- **Cell type naming**: Curator-provided naming tables

## Integration Points

### Web Interface (ABC Atlas)
- TypeScript components generate URLs for brain atlas visualization
- Kiwi-based payload generation for interactive exploration
- Atlas links embedded in ontology annotations

### External Ontologies
- **Cell Ontology (CL)**: Integration via `cl_subset_terms.py`
- **Uberon**: Anatomical location integration
- **Gene Ontology**: Via Ensembl gene processing

## Conclusion

The WMBO repository implements a sophisticated, multi-layered ontology generation pipeline that:

1. **Transforms** hierarchical brain cell taxonomy data into formal ontological structures
2. **Integrates** multiple data sources (genes, markers, anatomy, external ontologies)
3. **Applies** consistent design patterns via DOSDP for term generation
4. **Produces** multiple ontology products for different use cases
5. **Maintains** quality through extensive validation and reasoning

The system successfully bridges the gap between computational biology data and formal ontological representation, creating a comprehensive, data-driven ontology of mouse brain cell types with over 5000 terms and extensive logical axiomatization.