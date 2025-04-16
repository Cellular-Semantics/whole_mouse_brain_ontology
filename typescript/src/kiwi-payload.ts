import type {
  ExplorePageInitPayload,
  Visualization,
  Camera,
  point2d,
} from './abc-atlas/url-schema';

export function createExplorePageInitPayload(): ExplorePageInitPayload {
  const dummyFrame: Visualization = {
    dataCollectionId: `AP8JNN5LYABGVMGKY1B`,
    plotId: `Q1NCWWPG6FZ0DNIXJBQ`,
    metadataFilters:  [
        {
          "categoryId": "FS00DXV0T9R1X9FJ4QE",
          "selectedValues": ["01 IT-ET Glut"]
        },
        {
          "categoryId": "QY5S8KMO5HLJUF0P00K",
          "selectedValues": [
            "003 L5/6 IT TPE-ENT Glut"
          ]
        },
        {
          "categoryId": "15BK47DCIOF1SLLUW9P",
          "selectedValues": []
        },
        {
          "categoryId": "CBGC0U30VV9JPR60TJU",
          "selectedValues": []
        }
      ],
    camera: {
      projection: 'CARTESIAN',
      center: { x: 14.22116470336914, y: -5.733661651611328 },
      size: { x: 34.410255432128906, y: 41.63688659667969 },
    },
    genes: [{ symbol: `C230099D08Rik` }],
    colorBy: {
      mode: 'METADATA',
      value: `FS00DXV0T9R1X9FJ4QE`,
      transparency: 0.5,
      isTransparent: false,
    },
//     datasetId: `ds_${Math.random().toString(36).substr(2, 5)}`,
    visualizationId: `G4I4GFJXJB9ATZ3PTX1`,
    projectId: `LVDBJAW8BI5YSS1QUBG`,
    quantitativeFilters: [],
    annotation: {
      referenceId: `none`,
      featureTypeReferenceId: `none`,
      isInFront: true,
      fill: { option: 'NONE', color: '#000000', opacity: 100 },
      stroke: { option: 'DEFAULT', color: '#000000', opacity: 100 },
    },
  };

  const payload: ExplorePageInitPayload = {
    frames: [dummyFrame],
    layout: 'Single',
  };

  return payload;
}