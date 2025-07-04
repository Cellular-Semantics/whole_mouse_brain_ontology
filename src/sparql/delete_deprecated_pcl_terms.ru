PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

DELETE {
  ?s obo:IAO_0100001 ?v .
  ?s ?p ?o .
}
WHERE {
  ?s obo:IAO_0100001 ?v .
  ?s ?p ?o .
  FILTER(STRSTARTS(STR(?s), "http://purl.obolibrary.org/obo/PCL_"))
}