## Customize Makefile settings for wmbo
##
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

#IMPORTS += simple_human simple_marmoset

JOBS = CCN20230722
#GENE_LIST = ensmusg simple_human simple_marmoset
GENE_LIST = ensmusg
BDS_BASE = http://purl.obolibrary.org/obo/
ONTBASE=                    $(URIBASE)/pcl
BICANBASE=                    https://purl.brain-bican.org/taxonomy

TSV_CLASS_FILES = $(patsubst %, $(TMPDIR)/%_class.tsv, $(JOBS))
#TSV_CLASS_HOMOLOGOUS_FILES = $(patsubst %, ../patterns/data/default/%_class_homologous.tsv, $(JOBS))
#TSV_MARKER_SET_FILES = $(patsubst %, ../patterns/data/default/%_marker_set.tsv, $(JOBS))

OWL_FILES = $(patsubst %, components/%_indv.owl, $(JOBS))
OWL_CLASS_FILES = $(patsubst %, components/%_class.owl, $(JOBS))
OWL_CLASS_HOMOLOGOUS_FILES = $(patsubst %, components/%_class_homologous.owl, $(JOBS))
OWL_MARKER_SET_FILES = $(patsubst %, components/%_marker_set.owl, $(JOBS))
GENE_FILES = $(patsubst %, mirror/%.owl, $(GENE_LIST))
OWL_APP_SPECIFIC_FILES = $(patsubst %, components/%_app_specific.owl, $(JOBS))
OWL_DATASET_FILES = $(patsubst %, components/%_dataset.owl, $(JOBS))
OWL_TAXONOMY_FILE = components/taxonomies.owl
OWL_PROTEIN2GENE_FILE = components/Protein2GeneExpression.owl
PCL_LEGACY_FILE = components/pcl-legacy.owl

OWL_OBSOLETE_INDVS = $(patsubst %, components/%_obsolete_indvs.owl, $(JOBS))
OWL_OBSOLETE_TAXONOMY_FILE = components/taxonomies_obsolete.owl

CLEANFILES=$(MAIN_FILES) $(SRCMERGED) $(EDIT_PREPROCESSED) $(OWL_FILES) $(OWL_CLASS_FILES) $(COMPONENTSDIR)/wmb_taxonomy.owl

# overriding to add prefixes
$(PATTERNDIR)/pattern.owl: $(ALL_PATTERN_FILES)
	if [ $(PAT) = true ]; then $(DOSDPT) prototype --prefixes=template_prefixes.yaml --obo-prefixes true --template=$(PATTERNDIR)/dosdp-patterns --outfile=$@; fi

$(PATTERNDIR)/data/default/%.txt: $(PATTERNDIR)/dosdp-patterns/%.yaml $(PATTERNDIR)/data/default/%.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --prefixes=template_prefixes.yaml --infile=$(word 2, $^) --template=$< --obo-prefixes=true --outfile=$@; fi

# adding more imports (simple_human simple_marmoset) to process
#IMPORT_ROOTS = $(patsubst %, imports/%_import, $(IMPORTS))
#IMPORT_OWL_FILES = $(foreach n,$(IMPORT_ROOTS), $(n).owl)
#IMPORT_FILES = $(IMPORT_OWL_FILES)

#ALL_TERMS_COMBINED = $(patsubst %, imports/%_terms_combined.txt, $(IMPORTS))
#imports/merged_terms_combined.txt: $(ALL_TERMS_COMBINED)
#	if [ $(IMP) = true ]; then cat $^ | grep -v ^# | sort | uniq >  $@; fi

$(IMPORTDIR)/%_import.owl: $(MIRRORDIR)/merged.owl $(IMPORTDIR)/%_terms_combined.txt
	if [ $(IMP) = true ]; then $(ROBOT) query -i $< --update ../sparql/inject-version-info.ru --update ../sparql/preprocess-module.ru \
		extract -T $(IMPORTDIR)/$*_terms_combined.txt --force true --copy-ontology-annotations true --individuals exclude --method BOT \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru --update ../sparql/postprocess-module.ru \
		annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) --output $@.tmp.owl && mv $@.tmp.owl $@; fi

.PRECIOUS: $(IMPORTDIR)/%_import.owl

$(IMPORTDIR)/ensmusg_import.owl: mirror/ensmusg.owl imports/ensmusg_terms_combined.txt
	if [ $(IMP) = true ]; then $(ROBOT) query  -i $< --update ../sparql/inject-version-info.ru --update ../sparql/preprocess-module.ru \
		extract -T imports/ensmusg_terms_combined.txt --force true --copy-ontology-annotations true --individuals exclude --method BOT \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru --update ../sparql/postprocess-module.ru \
		annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) --output $@.tmp.owl && mv $@.tmp.owl $@; fi

.PRECIOUS: $(IMPORTDIR)/ensmusg_import.owl

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

#$(PATTERNDIR)/data/default/%_class_homologous.txt: $(PATTERNDIR)/data/default/%_class_homologous.tsv $(TSV_CLASS_FILES) .FORCE
#	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class_homologous.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi
#
#$(PATTERNDIR)/data/default/%_marker_set.txt: $(PATTERNDIR)/data/default/%_marker_set.tsv $(TSV_MARKER_SET_FILES) .FORCE
#	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi
#
#$(PATTERNDIR)/data/default/Protein2GeneExpression.txt: $(PATTERNDIR)/data/default/Protein2GeneExpression.tsv .FORCE
#	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/Protein2GeneExpression.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi


# merge class template data
$(TMPDIR)/%_class.tsv: ../patterns/data/default/%_class_base.tsv ../patterns/data/default/%_class_curation.tsv
	python ../scripts/template_runner.py modifier --merge -i=$< -i2=$(word 2, $^) -o=$@

# hard wiring for now.  Work on patsubst later
mirror/ensmusg.owl: ../templates/ensmusg.tsv .FORCE
	if [ $(MIR) = true ]; then $(ROBOT) template --input $(SRC) --template $< \
      --add-prefixes template_prefixes.json \
      annotate --ontology-iri ${BDS_BASE}$@ \
      convert --format ofn --output $@; fi
#	if [ $(MIR) = true ]; then $(ROBOT) template --input $(SRC) --template ../templates/simple_human.tsv \
#      --add-prefixes template_prefixes.json \
#      annotate --ontology-iri ${BDS_BASE}mirror/simple_human.owl \
#      convert --format ofn --output mirror/simple_human.owl; fi
#	if [ $(MIR) = true ]; then $(ROBOT) template --input $(SRC) --template ../templates/simple_marmoset.tsv \
#      --add-prefixes template_prefixes.json \
#      annotate --ontology-iri ${BDS_BASE}mirror/simple_marmoset.owl \
#      convert --format ofn --output mirror/simple_marmoset.owl; fi

#.PRECIOUS: mirror/simple_human.owl
#.PRECIOUS: imports/simple_human_import.owl
#.PRECIOUS: mirror/simple_marmoset.owl
#.PRECIOUS: imports/simple_marmoset_import.owl

$(COMPONENTSDIR)/wmb_taxonomy.owl:
	wget https://raw.githubusercontent.com/brain-bican/whole_mouse_brain_taxonomy/refs/heads/main/CCN20230722.rdf -O $(TMPDIR)/CCN20230722.rdf
	$(ROBOT) query --input $(TMPDIR)/CCN20230722.rdf --update ../sparql/delete_taxonomy_annotations.ru --update ../sparql/inject_fix_taxonomy_properties.ru --output $@

# merge all templates except application specific ones
.PHONY: $(COMPONENTSDIR)/all_templates.owl
$(COMPONENTSDIR)/all_templates.owl: $(OWL_FILES) $(OWL_CLASS_FILES) $(COMPONENTSDIR)/wmb_taxonomy.owl
	$(ROBOT) merge $(patsubst %, -i %, $(filter-out $(OWL_APP_SPECIFIC_FILES), $^)) \
	 --collapse-import-closure false \
	 annotate --ontology-iri ${BDS_BASE}$@  \
	 convert -f ofn	 -o $@

.PRECIOUS: $(COMPONENTSDIR)/all_templates.owl

$(COMPONENTSDIR)/%_indv.owl: ../templates/%.tsv $(SRC)
	$(ROBOT) template --input $(SRC) --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@

$(COMPONENTSDIR)/%_class.owl: $(TMPDIR)/%_class.tsv $(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml $(SRC)
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

#components/%_class_homologous.owl: $(PATTERNDIR)/data/default/%_class_homologous.tsv $(SRC) $(PATTERNDIR)/dosdp-patterns/taxonomy_class_homologous.yaml $(SRC) all_imports .FORCE
#	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
#        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class_homologous.yaml \
#        --ontology=$(SRC) --obo-prefixes=true --outfile=$@
#
#components/%_marker_set.owl: $(PATTERNDIR)/data/default/%_marker_set.tsv $(SRC) $(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml $(SRC) all_imports .FORCE
#	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
#        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml \
#        --ontology=$(SRC) --obo-prefixes=true --outfile=$@
#
#components/taxonomies.owl: ../templates/Taxonomies.tsv $(SRC)
#	$(ROBOT) template --input $(SRC) --template $< \
#    		--add-prefixes template_prefixes.json \
#    		annotate --ontology-iri ${BDS_BASE}$@ \
#    		convert --format ofn --output $@
#
#components/taxonomies_obsolete.owl: ../templates/Taxonomies_obsolete.tsv $(SRC)
#	$(ROBOT) template --input $(SRC) --template $< \
#    		--add-prefixes template_prefixes.json \
#    		annotate --ontology-iri ${BDS_BASE}$@ \
#    		convert --format ofn --output $@
#
#components/%_obsolete_indvs.owl: ../templates/%_obsolete_indvs.tsv $(SRC)
#	$(ROBOT) template --input $(SRC) --template $< \
#    		--add-prefixes template_prefixes.json \
#    		annotate --ontology-iri ${BDS_BASE}$@ \
#    		convert --format ofn --output $@ \
#
#components/Protein2GeneExpression.owl: $(PATTERNDIR)/data/default/Protein2GeneExpression.tsv $(PATTERNDIR)/dosdp-patterns/Protein2GeneExpression.yaml $(SRC) all_imports .FORCE
#	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
#        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/Protein2GeneExpression.yaml \
#        --ontology=$(SRC) --obo-prefixes=true --outfile=$@
#
## release a legacy ontology to support older versions of the PCL
#components/pcl-legacy.owl: ../resources/pCL_4.1.0.owl components/pCL_mapping.owl
#	$(ROBOT) query --input ../resources/pCL_4.1.0.owl --update ../sparql/delete-legacy-properties.ru \
#			query --update ../sparql/delete-non-pcl-terms.ru \
#			query --update ../sparql/postprocess-module.ru \
#			remove --select ontology \
#			merge --input components/pCL_mapping.owl \
#			annotate --ontology-iri $(ONTBASE)/pcl.owl  \
#			--link-annotation dc:license http://creativecommons.org/licenses/by/4.0/ \
#			--annotation owl:versionInfo $(VERSION) \
#			--annotation dc:title "Provisional Cell Ontology" \
#			--output $@
#
#components/pCL_mapping.owl: ../templates/pCL_mapping.tsv ../resources/pCL_4.1.0.owl
#	$(ROBOT) template --input ../resources/pCL_4.1.0.owl --template $< \
#    		--add-prefixes template_prefixes.json \
#    		convert --format ofn --output $@
#
#components/%_app_specific.owl: ../templates/%_app_specific.tsv allen_helper.owl
#	$(ROBOT) template --input allen_helper.owl --template $< \
#    		--add-prefixes template_prefixes.json \
#    		annotate --ontology-iri ${BDS_BASE}$@ \
#    		convert --format ofn --output $@ \
#
#components/%_dataset.owl: ../templates/%_dataset.tsv $(SRC)
#	$(ROBOT) template --input $(SRC) --template $< \
#    		--add-prefixes template_prefixes.json \
#    		annotate --ontology-iri ${BDS_BASE}$@ \
#    		convert --format ofn --output $@ \


## Release additional artifacts
#$(ONT).owl: $(ONT)-full.owl $(ONT)-allen.owl $(ONT)-pcl-comp.owl $(ONT)-pcl-comp.obo $(ONT)-pcl-comp.json
#	$(ROBOT) annotate --input $< --ontology-iri $(URIBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
#		convert -o $@.tmp.owl && mv $@.tmp.owl $@
#
## Allen app specific ontology (with color information etc.) (Used for Solr dump)
#$(ONT)-allen.owl: $(ONT)-full.owl allen_helper.owl
#	$(ROBOT) merge -i $< -i allen_helper.owl $(patsubst %, -i %, $(OWL_APP_SPECIFIC_FILES)) \
#			 annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
#		 	 --output $(RELEASEDIR)/$@
#
## Artifact that extends base with gene ontologies (used by PCL)
#$(ONT)-pcl-comp.owl:  $(ONT)-base.owl $(GENE_FILES)
#	$(ROBOT) merge -i $< $(patsubst %, -i %, $(GENE_FILES)) \
#	query --update ../sparql/remove_preflabels.ru \
#			 annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
#		 	 --output $(RELEASEDIR)/$@
#$(ONT)-pcl-comp.obo: $(RELEASEDIR)/$(ONT)-pcl-comp.owl
#	$(ROBOT) convert --input $< --check false -f obo $(OBO_FORMAT_OPTIONS) -o $@.tmp.obo && grep -v ^owl-axioms $@.tmp.obo > $(RELEASEDIR)/$@ && rm $@.tmp.obo
#$(ONT)-pcl-comp.json: $(RELEASEDIR)/$(ONT)-pcl-comp.owl
#	$(ROBOT) annotate --input $< --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
#		convert --check false -f json -o $@.tmp.json &&\
#	jq -S 'walk(if type == "array" then sort else . end)' $@.tmp.json > $(RELEASEDIR)/$@ && rm $@.tmp.json


# skip schema checks for now, because odk using the wrong validator
#.PHONY: pattern_schema_checks
#pattern_schema_checks: update_patterns
#	if [ $(PAT) = "skip" ]; then $(PATTERN_TESTER) $(PATTERNDIR)/dosdp-patterns/  ; fi

## ONTOLOGY: ro (remove [material entity](http://purl.obolibrary.org/obo/BFO_0000040) DisjointWith [part_of](http://purl.obolibrary.org/obo/BFO_0000050) some [immaterial entity](http://purl.obolibrary.org/obo/BFO_0000141))
## ONTOLOGY: ro
#.PHONY: mirror-ro
#.PRECIOUS: $(MIRRORDIR)/ro.owl
#mirror-ro: | $(TMPDIR)
#	curl -L $(OBOBASE)/ro/ro-base.owl --create-dirs -o $(TMPDIR)/ro-download.owl --retry 4 --max-time 400 && \
#	$(ROBOT) convert -i $(TMPDIR)/ro-download.owl -o $(TMPDIR)/$@.owl && \
#	$(ROBOT) query -i $(TMPDIR)/$@.owl --update ../sparql/remove_material_disjoint.ru -o $(TMPDIR)/$@.owl

# temporarily remove --exclude-tautologies structural
.PHONY: reason_test
reason_test: $(EDIT_PREPROCESSED)
	#$(ROBOT) explain --input $< --reasoner ELK -M unsatisfiability --unsatisfiable all --explanation explain.md --output explain.ofn
	#$(ROBOT) reason --input $< --reasoner ELK --equivalent-classes-allowed asserted-only \
#			--output test.owl && rm test.owl
	$(ROBOT) --add-prefixes template_prefixes.json merge --input $< remove --term https://purl.brain-bican.org/ontology/mbao/MBA_967 --term https://purl.brain-bican.org/ontology/mbao/MBA_901 --term https://purl.brain-bican.org/ontology/mbao/MBA_813 --term https://purl.brain-bican.org/ontology/mbao/MBA_717 --term https://purl.brain-bican.org/ontology/mbao/MBA_808 --term https://purl.brain-bican.org/ontology/mbao/MBA_917  --term https://purl.brain-bican.org/ontology/mbao/MBA_997 --term https://purl.brain-bican.org/ontology/mbao/MBA_632 \
		reason --reasoner ELK \
		--output test.owl && rm test.owl

#TODO: removing unsat MBA classes and removing asserted equivalent classes restriction
# 'remove --base-iri' constraint relaxed
# pcl id validator added
$(ONT)-base.owl: $(EDIT_PREPROCESSED) $(OTHER_SRC) $(IMPORT_FILES)
	$(ROBOT_RELEASE_IMPORT_MODE) \
	remove --term https://purl.brain-bican.org/ontology/mbao/MBA_967 --term https://purl.brain-bican.org/ontology/mbao/MBA_901 --term https://purl.brain-bican.org/ontology/mbao/MBA_813 --term https://purl.brain-bican.org/ontology/mbao/MBA_717 --term https://purl.brain-bican.org/ontology/mbao/MBA_808 --term https://purl.brain-bican.org/ontology/mbao/MBA_917  --term https://purl.brain-bican.org/ontology/mbao/MBA_997 \
	reason --reasoner ELK --exclude-tautologies structural --annotate-inferred-axioms False \
	relax \
	reduce -r ELK \
	remove --base-iri $(URIBASE)/WMBO --base-iri $(URIBASE)/PCL --base-iri $(URIBASE)/pcl/CS20230722 --base-iri $(BICANBASE)/CCN20230722 --axioms external --preserve-structure false --trim false \
	$(SHARED_ROBOT_COMMANDS) \
	annotate --link-annotation http://purl.org/dc/elements/1.1/type http://purl.obolibrary.org/obo/IAO_8000001 \
		--ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		--output $@.tmp.owl && mv $@.tmp.owl $@
	python ../scripts/pcl_id_validator.py

# Full: The full artefacts with imports merged, reasoned.
$(ONT)-full.owl: $(EDIT_PREPROCESSED) $(OTHER_SRC) $(IMPORT_FILES)
	$(ROBOT_RELEASE_IMPORT_MODE) \
		remove --term https://purl.brain-bican.org/ontology/mbao/MBA_967 --term https://purl.brain-bican.org/ontology/mbao/MBA_901 --term https://purl.brain-bican.org/ontology/mbao/MBA_813 --term https://purl.brain-bican.org/ontology/mbao/MBA_717 --term https://purl.brain-bican.org/ontology/mbao/MBA_808 --term https://purl.brain-bican.org/ontology/mbao/MBA_917  --term https://purl.brain-bican.org/ontology/mbao/MBA_997 \
		reason --reasoner ELK --exclude-tautologies structural \
		relax \
		reduce -r ELK \
		$(SHARED_ROBOT_COMMANDS) annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) --output $@.tmp.owl && mv $@.tmp.owl $@
# foo-simple: (edit->reason,relax,reduce,drop imports, drop every axiom which contains an entity outside the "namespaces of interest")
# drop every axiom: filter --term-file keep_terms.txt --trim true
#	remove --select imports --trim false
$(ONT)-simple.owl: $(EDIT_PREPROCESSED) $(OTHER_SRC) $(SIMPLESEED) $(IMPORT_FILES)
	$(ROBOT_RELEASE_IMPORT_MODE) \
		remove --term https://purl.brain-bican.org/ontology/mbao/MBA_967 --term https://purl.brain-bican.org/ontology/mbao/MBA_901 --term https://purl.brain-bican.org/ontology/mbao/MBA_813 --term https://purl.brain-bican.org/ontology/mbao/MBA_717 --term https://purl.brain-bican.org/ontology/mbao/MBA_808 --term https://purl.brain-bican.org/ontology/mbao/MBA_917  --term https://purl.brain-bican.org/ontology/mbao/MBA_997 \
		reason --reasoner ELK --exclude-tautologies structural --annotate-inferred-axioms False \
		relax \
		remove --axioms equivalent \
		relax \
		filter --term-file $(SIMPLESEED) --select "annotations ontology anonymous self" --trim true --signature true \
		reduce -r ELK \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru \
		$(SHARED_ROBOT_COMMANDS) annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) --output $@.tmp.owl && mv $@.tmp.owl $@
