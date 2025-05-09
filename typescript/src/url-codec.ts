import { compileSchema, parseSchema } from 'kiwi-schema';
import { urlSchema } from './abc-atlas/urlSchemaSource';
import type { Schema } from './abc-atlas/url-schema';

// note: it would be nice to use parcel to load the kiwi file directly as a string, like so:
// import explorePageSchema from 'bundle-text:../kiwi.schema';
// however, that wont work when testing this code with Vitest, so instead we use a script to generate urlSchemaSource.ts
// and then we can import it normally

let codec: Schema;

export function getUrlCodec(): Schema {
    if (!codec) {
        codec = compileSchema(parseSchema(urlSchema));
    }
    return codec;
}
