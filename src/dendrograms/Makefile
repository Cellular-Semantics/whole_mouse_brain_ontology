JOBS = CCN20230722

SUPPLEMENTARY = supplementary
TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
TEMPLATE_CLASS_BASE_FILES = $(patsubst %, ../patterns/data/default/%_class_base.tsv, $(JOBS))
TEMPLATE_CLASS_CURATION_FILES = $(patsubst %, ../patterns/data/default/%_class_curation.tsv, $(JOBS))
TEMPLATE_MARKER_SET_FILES = $(patsubst %, ../patterns/data/default/%_marker_set.tsv, $(JOBS))
TEMPLATE_NSFOREST_MARKER_SET_FILES = $(patsubst %, ../patterns/data/default/%_nsforest_marker_set.tsv, $(JOBS))
ABC_URLS = $(patsubst %, ./%_abc_urls.json, $(JOBS))

all: $(TEMPLATE_FILES) $(TEMPLATE_CLASS_BASE_FILES) $(TEMPLATE_CLASS_CURATION_FILES) $(TEMPLATE_MARKER_SET_FILES) $(TEMPLATE_NSFOREST_MARKER_SET_FILES) $(ABC_URLS)

CCN20230722.json:
	wget https://purl.brain-bican.org/taxonomy/CCN20230722/CCN20230722.json -O $@

../templates/%.tsv: %.json %_abc_urls.json
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

../patterns/data/default/%_nsforest_marker_set.tsv: %.json
	python ../scripts/template_runner.py generator -nms -i $< -o $@

../../typescript/dist/index.js: ../../typescript/tsconfig.json  ../../typescript/src/index.ts
	rm -rf ../../typescript/dist
	npm install --prefix ../../typescript typescript @types/node --save-dev
	npx tsc -p ../../typescript/tsconfig.json

CCN20230722_abc_urls.json: ../../typescript/dist/index.js
	node $< $@


