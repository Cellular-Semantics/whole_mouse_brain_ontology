// Source of the script: https://github.com/AllenInstitute/bkp-client/blob/dev/src/services/explore-visualizations/kiwi-url-utils.ts
// This file is part of the Allen Cell Explorer project. It is significantly trimmed/simplified to adapt to the WMBO use case.

import type {
    box2d,
    Camera,
    ColorOption,
    ColorSettings,
    ExplorePageInitPayload,
    FilterCategory,
    NullColoring,
    QuantitativeFilter,
    Visualization,
    Schema,
} from './abc-atlas/url-schema';

import { getUrlCodec } from './url-codec';

// these base64 encoders are stolen directly from MDN!
function base64ToBytes(base64: string) {
    // atob and btoa are deprecated... in nodejs! which for some reason
    // is what TS thinks this function is from - it is well supported in the browser
    // and fine to use for the purpose of binary->base64 encoding!
    const binString = atob(decodeURIComponent(base64));
    console.log('binString:', binString);
    return Uint8Array.from(binString, (m) => m.codePointAt(0) ?? 0);
}

function bytesToBase64(bytes: Uint8Array) {
    const binString = String.fromCodePoint(...bytes);
    return encodeURIComponent(btoa(binString));
}


export function encodeAsKiwiQuery(p: ExplorePageInitPayload): string {
    const codec: Schema = getUrlCodec();
    const bytes = codec.encodeExplorePageInitPayload(p);
    const str = bytesToBase64(bytes);

    return str;
}

export function decodeKiwiPayload(urlSafeEncodedPayload: string) {
    const codec: Schema = getUrlCodec();
    const bytes = base64ToBytes(urlSafeEncodedPayload);

    const pageInit = codec.decodeExplorePageInitPayload(bytes);
    return pageInit;
}
