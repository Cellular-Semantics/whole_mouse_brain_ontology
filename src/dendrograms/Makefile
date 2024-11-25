JOBS = CCN20230722

SUPPLEMENTARY = supplementary
TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
TEMPLATE_CLASS_BASE_FILES = $(patsubst %, ../patterns/data/default/%_class_base.tsv, $(JOBS))
TEMPLATE_CLASS_CURATION_FILES = $(patsubst %, ../patterns/data/default/%_class_curation.tsv, $(JOBS))

all: $(TEMPLATE_FILES) $(TEMPLATE_CLASS_BASE_FILES) $(TEMPLATE_CLASS_CURATION_FILES)

CCN20230722.json:
	wget https://purl.brain-bican.org/taxonomy/CCN20230722/CCN20230722.json -O $@

../templates/%.tsv: %.json
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


