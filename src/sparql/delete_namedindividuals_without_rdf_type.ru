PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

DELETE {
  ?ni ?p ?o .
}
WHERE {
  ?ni a owl:NamedIndividual .
  ?ni ?p ?o .
  FILTER NOT EXISTS {
    ?ni rdf:type ?t .
    FILTER(?t != owl:NamedIndividual)
  }
}