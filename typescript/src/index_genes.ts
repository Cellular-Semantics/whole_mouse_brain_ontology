import { readFileSync, writeFileSync } from 'fs';
import { resolve } from 'path';
import { decodeKiwiPayload, encodeAsKiwiQuery} from './kiwi-url-utils';
import { createPayload, writePayloadToFile } from './kiwi-payload';


function getOutputPath(): string {
    const args = process.argv.slice(3);
    if (args.length === 0) {
        throw new Error('Output path argument is missing.');
    }
    return resolve(args[0]);
}

function getGeneTablePath(): string {
    const args = process.argv.slice(2);
    if (args.length === 0) {
        throw new Error('Output path argument is missing.');
    }
    return resolve(args[0]);
}

export function generatePayloadTableForGenes(genes_table_path: string, out_path: string): void {
    const fileContent = readFileSync(genes_table_path, 'utf8');
    const lines = fileContent.trim().split('\n');

    // Use the header to determine column indices.
    const header = lines.shift();
    if (!header) {
        throw new Error('TSV file is empty or missing header.');
    }
    const headers = header.split('\t');

    const cellLabelIndex = headers.indexOf('Cell_label');
    const labelsetIndex = headers.indexOf('Labelset');
    const genesIndex = headers.indexOf('Markers_label');
    const markerSetIdIndex = headers.indexOf('defined_class');

    if (cellLabelIndex === -1 || labelsetIndex === -1 || genesIndex === -1) {
        throw new Error('Required columns not found in TSV file.');
    }

    const payloadDictionary: Record<string, any> = {};
    for (let i = 0; i < lines.length; i++) {
        const columns = lines[i].split('\t');
        const annotation ={
            cell_label: columns[cellLabelIndex],
            labelset: columns[labelsetIndex]
        };
        const genes = columns[genesIndex].split(',').map(gene => gene.trim());
        const markerSetId = columns[markerSetIdIndex];
        const payload = createPayload(annotation, genes)
        payloadDictionary[markerSetId] = encodeAsKiwiQuery(payload);
    }

    writePayloadToFile(out_path, payloadDictionary);
}

generatePayloadTableForGenes(getGeneTablePath(), getOutputPath());
console.log('ABC genes url generation successfully completed!');