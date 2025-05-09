import { readFileSync, writeFileSync } from 'fs';
import { resolve } from 'path';
import type { ExplorePageInitPayload, Visualization } from './abc-atlas/url-schema';
import { decodeKiwiPayload, encodeAsKiwiQuery} from './kiwi-url-utils';

/**
 * Generates a scRNAseq frame for the given annotation.
 * @param annotation - The annotation object containing labelset and cell_label.
 * @returns The generated scRNAseq frame object.
 */
function generateScRNAseqFrame(annotation: any, genes_filter: string[] = []): Visualization {
  const { metadataFilters, categoryId } = generateMetadataFilters(annotation);
  return {
    dataCollectionId: 'AP8JNN5LYABGVMGKY1B',
    plotId: 'Q1NCWWPG6FZ0DNIXJBQ',
    metadataFilters: metadataFilters,
    camera: {
      projection: 'CARTESIAN',
      center: { x: 6.2308759689331055, y: 4.501317501068115 },
      size: { x: 63.66279983520508, y: 41.63688659667969 },
    },
    genes: genes_filter.map(g => ({ symbol: g })),
    colorBy: {
      mode: 'METADATA',
      value: categoryId ?? undefined,
      transparency: 0.5,
      isTransparent: false,
    },
    visualizationId: 'G4I4GFJXJB9ATZ3PTX1',
    projectId: 'LVDBJAW8BI5YSS1QUBG',
    quantitativeFilters: [],
    annotation: {
      referenceId: 'none',
      featureTypeReferenceId: 'none',
      isInFront: true,
      fill: { option: 'NONE', color: '#000000', opacity: 100 },
      stroke: { option: 'DEFAULT', color: '#000000', opacity: 100 },
    },
  };
}

/**
* Generates a MerFish frame for the given annotation.
* @param annotation - The annotation object containing labelset and cell_label.
* @returns The generated MerFish frame object.
*/
function generateMerFishFrame(annotation: any, genes_filter: string[] = []): Visualization {
  const { metadataFilters, categoryId } = generateMetadataFilters(annotation);
  return {
    dataCollectionId: 'K9JN23P24KQCGK9U75A',
    plotId: 'SY3SLMNPID3C68MGS8V',
    metadataFilters: metadataFilters,
    camera: {
      projection: 'WEB_IMAGE',
      center: { x: 35.968414306640625, y: 23.939821243286133 },
      size: { x: 48.88800048828125, y: 59.15515899658203 },
      gridFeatureId: '2NQTIE7TAMP8PQAHO4P',
      slideBounds: {
        minCorner: { x: -5.166423320770264, y: -4.229303359985352 },
        maxCorner: { x: 5.117286682128906, y: 3.8190176486968994 },
      },
      hideUnselected: false,
      offsetIndex: 0,
    },
    genes: genes_filter.map(g => ({ symbol: g })),
    colorBy: {
      mode: 'METADATA',
      value: categoryId ?? undefined,
      transparency: 0.5,
      isTransparent: false,
    },
    visualizationId: '6MT7UC6ETYECBWF50PK',
    projectId: 'LVDBJAW8BI5YSS1QUBG',
    quantitativeFilters: [],
    annotation: {
      referenceId: 'none',
      featureTypeReferenceId: 'none',
      isInFront: true,
      fill: { option: 'NONE', color: '#000000', opacity: 100 },
      stroke: { option: 'DEFAULT', color: '#000000', opacity: 100 },
    },
  };
}

/**
 * Generates metadata filters based on the given annotation.
 * @param annotation - The annotation object containing labelset and cell_label.
 * @returns An array of metadata filters.
 */
function generateMetadataFilters(annotation: any) {
    const metadataFilters = [
    { categoryId: 'FS00DXV0T9R1X9FJ4QE', selectedValues: [] as string[] }, // class
    { categoryId: 'QY5S8KMO5HLJUF0P00K', selectedValues: [] as string[] }, // subclass
    { categoryId: '15BK47DCIOF1SLLUW9P', selectedValues: [] as string[] }, // supertype
    { categoryId: 'CBGC0U30VV9JPR60TJU', selectedValues: [] as string[] }  // cluster
  ];

  let relatedCategoryId: string | null = null;

  switch (annotation.labelset) {
    case 'class':
      metadataFilters[0].selectedValues.push(annotation.cell_label);
      relatedCategoryId = metadataFilters[0].categoryId;
      break;
    case 'subclass':
      metadataFilters[1].selectedValues.push(annotation.cell_label);
      relatedCategoryId = metadataFilters[1].categoryId;
      break;
    case 'supertype':
      metadataFilters[2].selectedValues.push(annotation.cell_label);
      relatedCategoryId = metadataFilters[2].categoryId;
      break;
    case 'cluster':
      metadataFilters[3].selectedValues.push(annotation.cell_label);
      relatedCategoryId = metadataFilters[3].categoryId;
      break;
    default:
      break;
  }
  return { metadataFilters, categoryId: relatedCategoryId };;
}

/**
 * Creates a payload object for a given annotation.
 * @param annotation - The annotation object containing labelset and cell_label.
 * @returns The generated ExplorePageInitPayload object.
 */
export function createPayload(annotation: any, genes_filter: string[] = []): ExplorePageInitPayload {
  const scRNAseqFrame = generateScRNAseqFrame(annotation, genes_filter);
  const merFishFrame = generateMerFishFrame(annotation, genes_filter);

  return {
    frames: [scRNAseqFrame, merFishFrame],
    layout: 'DoubleHorizontal',
  };
}

/**
 * Writes a payload dictionary to the given file.
 * @param outputPathArg - The path where the payload dictionary will be written.
 * @param payloadDictionary - The dictionary containing payloads to write.
 */
export function writePayloadToFile(outputPathArg: string, payloadDictionary: Record<string, any>): void {
  const outputPath = resolve(outputPathArg);
  writeFileSync(outputPath, JSON.stringify(payloadDictionary, null, 2), 'utf8');
  console.log(`Payload dictionary written to ${outputPath}`);
}

/**
 * Generates a payload table from a JSON file and writes it to the specified output path.
 * @param jsonFilePath - The path to the JSON file containing annotations.
 * @param outputPathArg - The path where the payload dictionary will be written.
 */
export function generatePayloadTable(jsonFilePath: string, outputPathArg: string): void {
  const resolvedJsonFilePath = resolve(jsonFilePath);
  const fileContent = readFileSync(resolvedJsonFilePath, 'utf8');
  const jsonData = JSON.parse(fileContent);
  const annotations = jsonData.annotations;

  const payloadDictionary: Record<string, any> = {};

  for (const annotation of annotations) {
    if (annotation.labelset === 'neurotransmitter') {
      continue; // Skip neurotransmitter annotations
    }
    const payload = createPayload(annotation);
//     console.log(JSON.stringify(payload, null, 2))
    payloadDictionary[annotation.cell_set_accession] = encodeAsKiwiQuery(payload);
  }

  writePayloadToFile(outputPathArg, payloadDictionary);
}