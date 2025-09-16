## Customize Makefile settings for wmbo
##
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

JOBS = CCN20230722
GENE_LIST = genedb
BDS_BASE = http://purl.obolibrary.org/obo/
ONTBASE=                    $(URIBASE)/pcl
BICANBASE=                    https://purl.brain-bican.org/taxonomy

TSV_CLASS_FILES = $(patsubst %, $(TMPDIR)/%_class.tsv, $(JOBS))

OWL_FILES = $(patsubst %, components/%_indv.owl, $(JOBS))
OWL_CLASS_FILES = $(patsubst %, components/%_class.owl, $(JOBS))
OWL_OBSOLETE_CLASS_FILES = $(patsubst %, components/%_obsolete_class.owl, $(JOBS))
OWL_MARKER_SET_FILES = $(patsubst %, components/%_marker_set.owl, $(JOBS))
OWL_NSF_MARKER_SET_FILES = $(patsubst %, components/%_nsforest_marker_set.owl, $(JOBS))
OWL_WS_MARKER_SET_FILES = $(patsubst %, components/%_within_subclass_marker_set.owl, $(JOBS))
OWL_EVIDENCE_MARKER_SET_FILES = $(patsubst %, components/%_evidence_marker_set.owl, $(JOBS))
GENE_FILES = $(patsubst %, mirror/%.owl, $(GENE_LIST))
GENE_IMPORTS = $(patsubst %, $(IMPORTDIR)/%_import.owl, $(GENE_LIST))
OWL_INFERRED_HIERARCHY_FILES = $(patsubst %, components/%_inferred_hierarchy.owl, $(JOBS))

CLEANFILES=$(MAIN_FILES) $(SRCMERGED) $(EDIT_PREPROCESSED) $(OWL_FILES) $(OWL_CLASS_FILES) $(OWL_OBSOLETE_CLASS_FILES) $(OWL_MARKER_SET_FILES) $(OWL_NSF_MARKER_SET_FILES) $(OWL_WS_MARKER_SET_FILES) $(OWL_EVIDENCE_MARKER_SET_FILES) $(COMPONENTSDIR)/wmb_taxonomy.owl $(OWL_INFERRED_HIERARCHY_FILES)

# overriding to add prefixes
$(PATTERNDIR)/pattern.owl: $(ALL_PATTERN_FILES)
	if [ $(PAT) = true ]; then $(DOSDPT) prototype --prefixes=template_prefixes.yaml --obo-prefixes true --template=$(PATTERNDIR)/dosdp-patterns --outfile=$@; fi

$(PATTERNDIR)/data/default/%.txt: $(PATTERNDIR)/dosdp-patterns/%.yaml $(PATTERNDIR)/data/default/%.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --prefixes=template_prefixes.yaml --infile=$(word 2, $^) --template=$< --obo-prefixes=true --outfile=$@; fi


$(IMPORTDIR)/%_import.owl: $(MIRRORDIR)/merged.owl $(IMPORTDIR)/%_terms_combined.txt
	if [ $(IMP) = true ]; then $(ROBOT) query -i $< --update ../sparql/inject-version-info.ru --update ../sparql/preprocess-module.ru \
		extract -T $(IMPORTDIR)/$*_terms_combined.txt --force true --copy-ontology-annotations true --individuals exclude --method BOT \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru --update ../sparql/postprocess-module.ru \
		annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) --output $@.tmp.owl && mv $@.tmp.owl $@; fi

.PRECIOUS: $(IMPORTDIR)/%_import.owl

imports/genedb_terms_combined.txt: mirror/genedb.owl
	if [ $(IMP) = true ]; then python $(SCRIPTSDIR)/ensembl.py terms --patterns_dir $(PATTERNDIR)/data/default --out $@; fi

$(IMPORTDIR)/genedb_import.owl: mirror/genedb.owl imports/genedb_terms_combined.txt
	if [ $(IMP) = true ]; then $(ROBOT) query  -i $< --update ../sparql/inject-version-info.ru --update ../sparql/preprocess-module.ru \
		extract -T imports/genedb_terms_combined.txt --prefixes template_prefixes.json --force true --copy-ontology-annotations true --individuals exclude --method BOT \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru --update ../sparql/postprocess-module.ru \
		annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) --output $@.tmp.owl && mv $@.tmp.owl $@; fi

.PRECIOUS: $(IMPORTDIR)/genedb_import.owl

# DISABLE automatic DOSDP pattern management. Manually managed below
$(PATTERNDIR)/definitions.owl: $(TSV_CLASS_FILES)
	if [ $(PAT) = "skip" ] && [ "${DOSDP_PATTERN_NAMES_DEFAULT}" ]   && [ $(PAT) = true ]; then $(ROBOT) merge $(addprefix -i , $^) \
		annotate --ontology-iri $(ONTBASE)/patterns/definitions.owl  --version-iri $(ONTBASE)/releases/$(TODAY)/patterns/definitions.owl \
      --annotation owl:versionInfo $(VERSION) -o definitions.ofn && mv definitions.ofn $@; fi
$(DOSDP_OWL_FILES_DEFAULT):
	if [ $(PAT) = "skip" ] && [ "${DOSDP_PATTERN_NAMES_DEFAULT}" ]; then $(DOSDPT) generate --catalog=catalog-v001.xml \
    --infile=$(PATTERNDIR)/data/default/ --template=$(PATTERNDIR)/dosdp-patterns --batch-patterns="$(DOSDP_PATTERN_NAMES_DEFAULT)" \
    --ontology=$< --obo-prefixes=true --outfile=$(PATTERNDIR)/data/default; fi
update_patterns:
	if [ $(PAT) = "skip" ]; then cp -r $(TMPDIR)/dosdp/*.yaml $(PATTERNDIR)/dosdp-patterns; fi

# disable automatic term management and manually manage below
$(PATTERNDIR)/data/default/%.txt: $(PATTERNDIR)/dosdp-patterns/%.yaml $(PATTERNDIR)/data/default/%.tsv .FORCE
	if [ $(PAT) = 'skip' ]; then $(DOSDPT) terms --infile=$(word 2, $^) --template=$< --obo-prefixes=true --outfile=$@; fi

$(PATTERNDIR)/data/default/%_class_base.txt: $(PATTERNDIR)/data/default/%_class_base.tsv $(TSV_CLASS_FILES) .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

$(PATTERNDIR)/data/default/%_class_curation.txt: $(PATTERNDIR)/data/default/%_class_curation.tsv $(TSV_CLASS_FILES) .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

$(PATTERNDIR)/data/default/%_class_obsolete.txt: $(PATTERNDIR)/data/default/%_class_obsolete.tsv $(TSV_CLASS_FILES) .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class_obsolete.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

$(PATTERNDIR)/data/default/%_marker_set.txt: $(PATTERNDIR)/data/default/%_marker_set.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

$(PATTERNDIR)/data/default/%_nsforest_marker_set.txt: $(PATTERNDIR)/data/default/%_nsforest_marker_set.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

$(PATTERNDIR)/data/default/%_within_subclass_marker_set.txt: $(PATTERNDIR)/data/default/%_within_subclass_marker_set.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

$(PATTERNDIR)/data/default/%_evidence_marker_set.txt: $(PATTERNDIR)/data/default/%_evidence_marker_set.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

# merge class template data
$(TMPDIR)/%_class.tsv: ../patterns/data/default/%_class_base.tsv ../patterns/data/default/%_class_curation.tsv
	python ../scripts/template_runner.py modifier --merge -i=$< -i2=$(word 2, $^) -o=$@

# hard wiring for now.  Work on patsubst later
mirror/genedb.owl: ../templates/genedb.tsv .FORCE
	if [ $(MIR) = true ]; then $(ROBOT) template --input $(SRC) --template $< \
      --add-prefixes template_prefixes.json \
      annotate --ontology-iri ${BDS_BASE}$@ \
      convert --format ofn --output $@; fi

$(COMPONENTSDIR)/wmb_taxonomy.owl:
	wget https://raw.githubusercontent.com/brain-bican/whole_mouse_brain_taxonomy/refs/heads/main/CCN20230722.rdf -O $(TMPDIR)/CCN20230722.rdf
	$(ROBOT) query --input $(TMPDIR)/CCN20230722.rdf --update ../sparql/inject_fix_taxonomy_properties.ru --update ../sparql/delete_author_annotation_fields.ru --output $@
	#$(ROBOT) query --input $(TMPDIR)/CCN20230722.rdf --update ../sparql/delete_taxonomy_annotations.ru --update ../sparql/inject_fix_taxonomy_properties.ru --update ../sparql/delete_author_annotation_fields.ru --output $@

# merge all templates except application specific ones
.PHONY: $(COMPONENTSDIR)/all_templates.owl
$(COMPONENTSDIR)/all_templates.owl: $(OWL_FILES) $(OWL_CLASS_FILES) $(OWL_OBSOLETE_CLASS_FILES) $(OWL_MARKER_SET_FILES) $(OWL_NSF_MARKER_SET_FILES) $(OWL_WS_MARKER_SET_FILES) $(OWL_EVIDENCE_MARKER_SET_FILES) $(COMPONENTSDIR)/wmb_taxonomy.owl
		$(ROBOT) merge $(patsubst %, -i %, $^) \
	 --collapse-import-closure false \
	 annotate --ontology-iri ${BDS_BASE}$@  \
	 query --update ../sparql/replace_string_to_float.ru  \
	 query --update ../sparql/replace_string_to_boolean.ru  \
	 query --update ../sparql/unpack_subclass_of_intersection.ru  \
	 query --update ../sparql/unpack_equivalentclass_intersection.ru  \
	 convert -f ofn	 -o $@
	 #	 query --update ../sparql/delete_has_exemplar_data_rel.ru \

.PRECIOUS: $(COMPONENTSDIR)/all_templates.owl

$(COMPONENTSDIR)/%_indv.owl: ../templates/%.tsv $(SRC)
	$(ROBOT) template --input $(SRC) --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@

$(COMPONENTSDIR)/%_obsolete_class.owl: $(PATTERNDIR)/data/default/%_class_obsolete.tsv $(PATTERNDIR)/dosdp-patterns/taxonomy_class_obsolete.yaml $(SRC)
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class_obsolete.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

$(COMPONENTSDIR)/%_class.owl: $(TMPDIR)/%_class.tsv $(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml $(SRC)
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

components/%_marker_set.owl: $(PATTERNDIR)/data/default/%_marker_set.tsv $(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml $(SRC)
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

components/%_nsforest_marker_set.owl: $(PATTERNDIR)/data/default/%_nsforest_marker_set.tsv $(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml $(SRC)
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

components/%_within_subclass_marker_set.owl: $(PATTERNDIR)/data/default/%_within_subclass_marker_set.tsv $(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml $(SRC)
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

components/%_evidence_marker_set.owl: $(PATTERNDIR)/data/default/%_evidence_marker_set.tsv $(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml $(SRC)
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

components/%_inferred_hierarchy.owl: $(COMPONENTSDIR)/%_indv.owl $(COMPONENTSDIR)/%_class.owl $(IMPORT_FILES)
	$(ROBOT) merge $(patsubst %, -i %, $^) \
    		reason --reasoner ELK --create-new-ontology true \
    		remove --base-iri $(URIBASE)/WMBO --base-iri $(URIBASE)/PCL --base-iri $(URIBASE)/CL --axioms external --preserve-structure false --trim false --output $@

#TODO: removing unsat MBA classes and removing asserted equivalent classes restriction
# 'remove --base-iri' constraint relaxed
# reduce --preserve-annotated-axioms added
# pcl id validator added
$(ONT)-base.owl: $(EDIT_PREPROCESSED) $(OTHER_SRC) $(IMPORT_FILES) $(OWL_INFERRED_HIERARCHY_FILES)
	$(ROBOT_RELEASE_IMPORT_MODE) \
	merge $(patsubst %, -i %, $(OWL_INFERRED_HIERARCHY_FILES)) $(patsubst %, -i %, $(OWL_FILES)) \
	reason --reasoner ELK --exclude-tautologies structural --annotate-inferred-axioms False \
	relax \
	reduce -r ELK --preserve-annotated-axioms true \
	remove --base-iri $(URIBASE)/WMBO --base-iri $(URIBASE)/PCL --base-iri $(URIBASE)/pcl/CS20230722 --base-iri $(BICANBASE)/CCN20230722 --base-iri $(URIBASE)/CL_4 --base-iri $(URIBASE)/CLM_5 --axioms external --preserve-structure false --trim false \
	$(SHARED_ROBOT_COMMANDS) \
	annotate --link-annotation http://purl.org/dc/elements/1.1/type http://purl.obolibrary.org/obo/IAO_8000001 \
		--ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		--output $@.tmp.owl && mv $@.tmp.owl $@
	python ../scripts/validate_release.py validate -i $@
	#python ../scripts/pcl_id_validator.py

# Full: The full artefacts with imports merged, reasoned.
# -equivalent-classes-allowed asserted-only removed
# reduce --preserve-annotated-axioms added
$(ONT)-full.owl: $(EDIT_PREPROCESSED) $(OTHER_SRC) $(IMPORT_FILES) $(OWL_INFERRED_HIERARCHY_FILES)
	$(ROBOT_RELEASE_IMPORT_MODE) \
  		merge $(patsubst %, -i %, $(OWL_INFERRED_HIERARCHY_FILES)) \
  		reason --reasoner ELK --exclude-tautologies structural \
		relax \
		reduce -r ELK --preserve-annotated-axioms true \
		$(SHARED_ROBOT_COMMANDS) annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) --output $@.tmp.owl && mv $@.tmp.owl $@

# foo-simple: (edit->reason,relax,reduce,drop imports, drop every axiom which contains an entity outside the "namespaces of interest")
# drop every axiom: filter --term-file keep_terms.txt --trim true
#	remove --select imports --trim false
# reduce --preserve-annotated-axioms added
# filter selector self constraint relaxed
$(ONT)-simple.owl: $(EDIT_PREPROCESSED) $(OTHER_SRC) $(SIMPLESEED) $(IMPORT_FILES) $(OWL_INFERRED_HIERARCHY_FILES)
	$(ROBOT_RELEASE_IMPORT_MODE) \
		merge $(patsubst %, -i %, $(OWL_INFERRED_HIERARCHY_FILES)) \
		remove --term https://purl.brain-bican.org/ontology/mbao/MBA_967 --term https://purl.brain-bican.org/ontology/mbao/MBA_901 --term https://purl.brain-bican.org/ontology/mbao/MBA_813 --term https://purl.brain-bican.org/ontology/mbao/MBA_717 --term https://purl.brain-bican.org/ontology/mbao/MBA_808 --term https://purl.brain-bican.org/ontology/mbao/MBA_917  --term https://purl.brain-bican.org/ontology/mbao/MBA_997 \
		reason --reasoner ELK --exclude-tautologies structural --annotate-inferred-axioms False \
		relax \
		remove --axioms equivalent \
		relax \
		filter --term-file $(SIMPLESEED) --select "annotations ontology anonymous self <http://purl.obolibrary.org/obo/PCL_*>" --select "<https://purl.brain-bican.org/taxonomy/*>" --select "<http://purl.obolibrary.org/obo/CL_4*>" --select "<http://purl.obolibrary.org/obo/CLM_5*>" --trim true --signature true \
		reduce -r ELK --preserve-annotated-axioms true \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru \
		$(SHARED_ROBOT_COMMANDS) annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) --output $@.tmp.owl && mv $@.tmp.owl $@

## ONTOLOGY: uberon
## delete disjoint classes and properties, they are causing inconsistencies when merged with mba
.PHONY: mirror-uberon
.PRECIOUS: $(MIRRORDIR)/uberon.owl
mirror-uberon: | $(TMPDIR)
	curl -L $(OBOBASE)/uberon/uberon-base.owl --create-dirs -o $(TMPDIR)/uberon-download.owl --retry 4 --max-time 400 && \
	$(ROBOT) convert -i $(TMPDIR)/uberon-download.owl -o $(TMPDIR)/$@.owl
	$(ROBOT) query -i $(TMPDIR)/$@.owl --update ../sparql/delete_uberon_disjointness.ru -o $(TMPDIR)/$@.owl

# Release additional artifacts
$(ONT).owl: $(ONT)-full.owl $(ONT)-pcl-comp.owl $(ONT)-pcl-comp.obo $(ONT)-pcl-comp.json $(RELEASEDIR)/$(ONT)-cl-comp.owl $(RELEASEDIR)/$(ONT)-cl-comp.obo $(RELEASEDIR)/$(ONT)-cl-comp.json
	$(ROBOT) annotate --input $< --ontology-iri $(URIBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		convert -o $@.tmp.owl && mv $@.tmp.owl $@

# Artifact that extends base with gene ontologies (used by PCL)
$(ONT)-pcl-comp.owl:  $(ONT)-base.owl $(GENE_IMPORTS)
	$(ROBOT) merge -i $< $(patsubst %, -i %, $(GENE_IMPORTS)) \
	 	annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		--output $(RELEASEDIR)/$@
$(ONT)-pcl-comp.obo: $(RELEASEDIR)/$(ONT)-pcl-comp.owl
	$(ROBOT) convert --input $< --check false -f obo $(OBO_FORMAT_OPTIONS) -o $@.tmp.obo && grep -v ^owl-axioms $@.tmp.obo > $(RELEASEDIR)/$@ && rm $@.tmp.obo
$(ONT)-pcl-comp.json: $(RELEASEDIR)/$(ONT)-pcl-comp.owl
	$(ROBOT) annotate --input $< --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		convert --check false -f json -o $@.tmp.json &&\
	jq -S 'walk(if type == "array" then sort else . end)' $@.tmp.json > $(RELEASEDIR)/$@ && rm $@.tmp.json

$(TMPDIR)/cl_component_terms.txt: $(TMPDIR)/all_pattern_terms.txt
	python ../scripts/cl_subset_terms.py classes -o $@

$(TMPDIR)/cl_indv_terms.txt: $(OWL_CLASS_FILES) $(TMPDIR)/cl_component_terms.txt
	$(ROBOT) merge $(patsubst %, -i %, $(OWL_CLASS_FILES)) --output $(TMPDIR)/all_class.owl
	python ../scripts/cl_subset_terms.py individuals -i $(TMPDIR)/all_class.owl -c $(TMPDIR)/cl_component_terms.txt -o $@

$(TMPDIR)/cl_individuals.owl: $(OWL_FILES) $(TMPDIR)/cl_indv_terms.txt
	$(ROBOT) --prefixes template_prefixes.json merge $(patsubst %, -i %, $(OWL_FILES)) \
	filter --term-file $(TMPDIR)/cl_indv_terms.txt --select "self annotations" --trim false \
	query --update ../sparql/delete_namedindividuals_without_rdf_type.ru --output $@.tmp.owl
	python ../scripts/cl_subset_terms.py trim_indvs -i $@.tmp.owl -t $(TMPDIR)/cl_indv_terms.txt -o $@

# Artifact for CL that hosts only the validated component annotations (used by CL)
$(RELEASEDIR)/$(ONT)-cl-comp.owl: $(ONT)-pcl-comp.owl $(TMPDIR)/cl_component_terms.txt wmbo-cl-edit.owl $(TMPDIR)/cl_individuals.owl
	$(ROBOT) remove --input $(RELEASEDIR)/$(ONT)-pcl-comp.owl --select "<http://purl.obolibrary.org/obo/PCL_*>" --select "<https://purl.brain-bican.org/taxonomy/CCN20230722/*>" --signature true \
	filter --term-file $(TMPDIR)/cl_component_terms.txt --select "annotations anonymous self" --signature true --trim false  \
	remove --select "<http://purl.obolibrary.org/obo/PCL_01*>" --signature true \
	query --update ../sparql/delete_deprecated_pcl_terms.ru --update ../sparql/delete_multiple_gene_labels.ru \
	merge -i $(TMPDIR)/cl_individuals.owl \
	merge -i wmbo-cl-edit.owl --output $@
$(RELEASEDIR)/$(ONT)-cl-comp.obo: $(RELEASEDIR)/$(ONT)-cl-comp.owl
	$(ROBOT) convert --input $< --check false -f obo $(OBO_FORMAT_OPTIONS) -o $@.tmp.obo && grep -v ^owl-axioms $@.tmp.obo > $@ && rm $@.tmp.obo
$(RELEASEDIR)/$(ONT)-cl-comp.json: $(RELEASEDIR)/$(ONT)-cl-comp.owl
	$(ROBOT) annotate --input $< --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		convert --check false -f json -o $@.tmp.json &&\
	jq -S 'walk(if type == "array" then sort else . end)' $@.tmp.json > $@ && rm $@.tmp.json
