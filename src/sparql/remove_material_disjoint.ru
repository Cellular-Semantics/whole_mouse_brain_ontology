PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX BFO: <http://purl.obolibrary.org/obo/BFO_>

DELETE {
    BFO:0000040 owl:disjointWith ?o1 .
}

WHERE {
    BFO:0000040 owl:disjointWith ?o1 .
}