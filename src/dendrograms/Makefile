JOBS = CCN20230722

SUPPLEMENTARY = supplementary
TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
TEMPLATE_CLASS_BASE_FILES = $(patsubst %, ../patterns/data/default/%_class_base.tsv, $(JOBS))
TEMPLATE_CLASS_CURATION_FILES = $(patsubst %, ../patterns/data/default/%_class_curation.tsv, $(JOBS))
TEMPLATE_MARKER_SET_FILES = $(patsubst %, ../patterns/data/default/%_marker_set.tsv, $(JOBS))
TEMPLATE_WS_MARKER_SET_FILES = $(patsubst %, ../patterns/data/default/%_within_subclass_marker_set.tsv, $(JOBS))
TEMPLATE_NSFOREST_MARKER_SET_FILES = $(patsubst %, ../patterns/data/default/%_nsforest_marker_set.tsv, $(JOBS))
TEMPLATE_EVIDENCE_MARKER_SET_FILES = $(patsubst %, ../patterns/data/default/%_evidence_marker_set.tsv, $(JOBS))
ABC_URLS = $(patsubst %, ./%_abc_urls.json, $(JOBS))
ABC_URLS_MARKER_SET = $(patsubst %, ./%_abc_urls_marker_set.json, $(JOBS))
ABC_URLS_EVIDENCE_MARKER_SET = $(patsubst %, ./%_abc_urls_evidence_marker_set.json, $(JOBS))
ABC_URLS_NSFOREST_MARKER_SET = $(patsubst %, ./%_abc_urls_nsforest_marker_set.json, $(JOBS))
ABC_URLS_WS_MARKER_SET = $(patsubst %, ./%_abc_urls_ws_marker_set.json, $(JOBS))

SHEETS_SCRIPT := ../scripts/google_sheets_to_tsv.py

all: sheets $(TEMPLATE_FILES) $(TEMPLATE_CLASS_BASE_FILES) $(TEMPLATE_CLASS_CURATION_FILES) \
	$(TEMPLATE_MARKER_SET_FILES) $(TEMPLATE_NSFOREST_MARKER_SET_FILES) \
	$(TEMPLATE_WS_MARKER_SET_FILES) $(TEMPLATE_EVIDENCE_MARKER_SET_FILES) \
	$(ABC_URLS) $(ABC_URLS_MARKER_SET) $(ABC_URLS_EVIDENCE_MARKER_SET) \
	$(ABC_URLS_NSFOREST_MARKER_SET) $(ABC_URLS_WS_MARKER_SET)

.PHONY: sheets
sheets: $(SHEETS_SCRIPT)
	@echo "==> Exporting Google Sheets tabs to TSV..."
	@python $(SHEETS_SCRIPT)

CCN20230722.json:
	wget https://raw.githubusercontent.com/brain-bican/whole_mouse_brain_taxonomy/refs/heads/main/CCN20230722.json -O $@

../templates/%.tsv: %.json %_abc_urls.json ../patterns/data/default/%_class_curation.tsv
	python ../scripts/template_runner.py generator -i $< -o $@

#../markers/%_markers_denormalized.tsv: %.json nomenclature_table_%.csv
#	if [ $< = CS1908210.json ]; then python ../scripts/template_runner.py generator -md -i $< -o $@ ;\
#	else python ../scripts/template_runner.py generator -md -i $(word 2, $^) -o $@ ; fi

../patterns/data/default/%_class_base.tsv: %.json $(SUPPLEMENTARY)/version2/neurotransmitters.tsv
	python ../scripts/template_runner.py generator -cb -i $< -o $@

../patterns/data/default/%_class_curation.tsv: %.json
	python ../scripts/template_runner.py generator -cc -i $< -o $@

$(SUPPLEMENTARY)/version2/neurotransmitters.tsv:
	python ../scripts/supplementary_data_processor.py -nt -o $@

../patterns/data/default/%_marker_set.tsv: %.json
	python ../scripts/template_runner.py generator -ms -i $< -o $@

../patterns/data/default/%_within_subclass_marker_set.tsv: %.json
	python ../scripts/template_runner.py generator -wsms -i $< -o $@

../patterns/data/default/%_nsforest_marker_set.tsv: %.json
	python ../scripts/template_runner.py generator -nms -i $< -o $@

../patterns/data/default/%_evidence_marker_set.tsv: %.json
	python ../scripts/template_runner.py generator -ems -i $< -o $@

prepare_npm: ../../typescript/dist/index.js
	rm -rf ../../typescript/dist
	npm install typescript

../../typescript/dist/index.js: prepare_npm ../../typescript/tsconfig.json  ../../typescript/src/index.ts
	npm install --prefix ../../typescript typescript @types/node --save-dev
	npx tsc -p ../../typescript/tsconfig.json

CCN20230722_abc_urls.json: ../../typescript/dist/index.js
	node $< $@

CCN20230722_abc_urls_marker_set.json: ../../typescript/dist/index_genes.js ../patterns/data/default/CCN20230722_marker_set.tsv
	node $< $(word 2, $^) $@

CCN20230722_abc_urls_evidence_marker_set.json: ../../typescript/dist/index_genes.js ../patterns/data/default/CCN20230722_evidence_marker_set.tsv
	node $< $(word 2, $^) $@

CCN20230722_abc_urls_nsforest_marker_set.json: ../../typescript/dist/index_genes.js ../patterns/data/default/CCN20230722_nsforest_marker_set.tsv
	node $< $(word 2, $^) $@

CCN20230722_abc_urls_ws_marker_set.json: ../../typescript/dist/index_genes.js ../patterns/data/default/CCN20230722_within_subclass_marker_set.tsv
	node $< $(word 2, $^) $@


