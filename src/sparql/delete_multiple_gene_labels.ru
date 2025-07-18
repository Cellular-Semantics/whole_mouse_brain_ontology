# This query deletes one rdfs:label from NCBI genes that have more than one labels

PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

DELETE {
  ?class rdfs:label ?labelToDelete .
}
WHERE {
  {
    SELECT ?class (MIN(?label) AS ?labelToKeep)
    WHERE {
      ?class rdfs:label ?label ;
             a ?type .
      FILTER(STRSTARTS(STR(?class), "http://identifiers.org/ncbigene/"))
    }
    GROUP BY ?class
    HAVING (COUNT(?label) > 1)
  }
  ?class rdfs:label ?labelToDelete .
  FILTER(?labelToDelete != ?labelToKeep)
}