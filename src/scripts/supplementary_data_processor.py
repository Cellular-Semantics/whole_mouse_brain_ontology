import os
import argparse

import pandas as pd

C2C_ANNOTATION_MEMBERSHIP = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/supplementary/version2/cluster_to_cluster_annotation_membership.csv")


def generate_neurotransmitter_data(output_file: str):
    """
    Generates a cluster-to-neurotransmitter mapping data.
    Args:
        output_file: Output file path.
    """
    print("Generate neurotransmitter data")
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

    mapping_df = pd.DataFrame(mapping)
    mapping_df.to_csv(output_file, index=False, sep='\t')
    print("Generate neurotransmitter data generated at: ", output_file)

parser = argparse.ArgumentParser(description='Cli interface to process supplementary data')

parser.add_argument('-i', '--input', help="Path to input file")
parser.add_argument('-i2', '--input2', help="Path to second input file")
parser.add_argument('-o', '--output', help="Path to output file")
parser.add_argument('-b', '--base', help="List of all class base TSV files")
parser.add_argument('-nt', action='store_true', help="Generate neurotransmitter data.")

args = parser.parse_args()

if args.nt:
    generate_neurotransmitter_data(args.output)
else:
    raise ValueError("No action specified")