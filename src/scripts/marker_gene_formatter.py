import csv

def convert_csv_to_template(input_csv, output_tsv):
    """
    Gene csv source: https://allen-brain-cell-atlas.s3.us-west-2.amazonaws.com/index.html#metadata/WMB-10X/20231215/
    Args:
        input_csv:
        output_tsv:

    Returns:

    """
    with open(input_csv, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        with open(output_tsv, mode='w', newline='') as tsv_file:
            tsv_writer = csv.writer(tsv_file, delimiter='\t')
            # Write the headers
            tsv_writer.writerow(['ID', 'TYPE', 'NAME', 'SYNONYMS'])
            tsv_writer.writerow(['ID', 'SC %', 'A rdfs:label', 'A oboInOwl:hasExactSynonym SPLIT=|'])
            # Write the rows
            for row in csv_reader:
                tsv_writer.writerow(["ensembl:" + row['gene_identifier'], 'SO:0000704', row['gene_symbol'] + " (Mmus)", row['name']])


input_csv = '/Users/hk9/Downloads/gene.csv'
output_tsv = '/Users/hk9/workspaces/workspace2/whole_mouse_brain_ontology/src/templates/ensmusg.tsv'
convert_csv_to_template(input_csv, output_tsv)