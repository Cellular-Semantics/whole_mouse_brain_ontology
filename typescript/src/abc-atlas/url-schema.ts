export type Projection = 'WEB_IMAGE' | 'CARTESIAN';

export type Layout =
    | 'Single'
    | 'DoubleVertical'
    | 'DoubleHorizontal'
    | 'TripleLeft'
    | 'TripleRight'
    | 'TripleBottom'
    | 'TripleTop'
    | 'Quadruple'
    | 'QuadrupleRight'
    | 'QuadrupleBottom'
    | 'QuadrupleTop'
    | 'QuadrupleLeft';

export type ColorMode = 'QUANTITATIVE' | 'METADATA';

export type FilterType = 'METADATA' | 'QUANTITATIVE' | 'GENE';

export type NullColoring = 'HIDE' | 'ZEROS' | 'COLOR';

export type ColorOption = 'NONE' | 'DEFAULT' | 'CUSTOM';

export interface point2d {
    x: number;
    y: number;
}

export interface box2d {
    minCorner: point2d;
    maxCorner: point2d;
}

export interface Interval {
    min: number;
    max: number;
}

export interface NumericColor {
    clampRange?: Interval;
    nullColor?: string;
    invertMap?: boolean;
    gradient?: string[];
    name?: string;
    type?: string;
    excludeZeros?: boolean;
    nullColoring?: NullColoring;
}

export interface Slide {
    id?: string;
    value?: string;
    priorityOrder?: number;
}

export interface Camera {
    projection?: Projection;
    center?: point2d;
    size?: point2d;
    gridFeatureId?: string;
    slideBounds?: box2d;
    hideUnselected?: boolean;
    offsetIndex?: number;
}

export interface FilterCategory {
    categoryId?: string;
    selectedValues?: string[];
}

export interface QuantitativeFilter {
    index?: number;
    symbol?: string;
    range?: Interval;
}

export interface DrawStyle {
    option?: ColorOption;
    color?: string;
    opacity?: number;
}

export interface Annotation {
    referenceId?: string;
    featureTypeReferenceId?: string;
    isInFront?: boolean;
    fill?: DrawStyle;
    stroke?: DrawStyle;
}

export interface Gene {
    symbol?: string;
}

export interface ColorSettings {
    mode?: ColorMode;
    value?: string;
    transparency?: number;
    isTransparent?: boolean;
    range?: Interval;
    index?: number;
    color?: NumericColor;
}

export interface Visualization {
    dataCollectionId?: string;
    plotId?: string;
    metadataFilters?: FilterCategory[];
    camera?: Camera;
    genes?: Gene[];
    colorBy?: ColorSettings;
    datasetId?: string;
    visualizationId?: string;
    projectId?: string;
    quantitativeFilters?: QuantitativeFilter[];
    annotation?: Annotation;
}

export interface ExplorePageInitPayload {
    frames?: Visualization[];
    layout?: Layout;
}

export interface Schema {
    encodepoint2d(message: point2d): Uint8Array;
    decodepoint2d(buffer: Uint8Array): point2d;
    encodebox2d(message: box2d): Uint8Array;
    decodebox2d(buffer: Uint8Array): box2d;
    encodeInterval(message: Interval): Uint8Array;
    decodeInterval(buffer: Uint8Array): Interval;
    encodeNumericColor(message: NumericColor): Uint8Array;
    decodeNumericColor(buffer: Uint8Array): NumericColor;
    Projection: Projection;
    Layout: Layout;
    ColorMode: ColorMode;
    encodeSlide(message: Slide): Uint8Array;
    decodeSlide(buffer: Uint8Array): Slide;
    encodeCamera(message: Camera): Uint8Array;
    decodeCamera(buffer: Uint8Array): Camera;
    FilterType: FilterType;
    encodeFilterCategory(message: FilterCategory): Uint8Array;
    decodeFilterCategory(buffer: Uint8Array): FilterCategory;
    NullColoring: NullColoring;
    encodeQuantitativeFilter(message: QuantitativeFilter): Uint8Array;
    decodeQuantitativeFilter(buffer: Uint8Array): QuantitativeFilter;
    ColorOption: ColorOption;
    encodeDrawStyle(message: DrawStyle): Uint8Array;
    decodeDrawStyle(buffer: Uint8Array): DrawStyle;
    encodeAnnotation(message: Annotation): Uint8Array;
    decodeAnnotation(buffer: Uint8Array): Annotation;
    encodeGene(message: Gene): Uint8Array;
    decodeGene(buffer: Uint8Array): Gene;
    encodeColorSettings(message: ColorSettings): Uint8Array;
    decodeColorSettings(buffer: Uint8Array): ColorSettings;
    encodeVisualization(message: Visualization): Uint8Array;
    decodeVisualization(buffer: Uint8Array): Visualization;
    encodeExplorePageInitPayload(message: ExplorePageInitPayload): Uint8Array;
    decodeExplorePageInitPayload(buffer: Uint8Array): ExplorePageInitPayload;
}
