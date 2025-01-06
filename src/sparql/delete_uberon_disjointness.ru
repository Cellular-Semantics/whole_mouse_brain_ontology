PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

DELETE {
  ?restriction rdf:type owl:Restriction .
  ?restriction owl:onProperty obo:BFO_0000050 .
  ?restriction owl:someValuesFrom obo:UBERON_0000010 .
  ?restriction owl:disjointWith ?innerRestriction .
  ?innerRestriction rdf:type owl:Restriction .
  ?innerRestriction owl:onProperty obo:BFO_0000050 .
  ?innerRestriction owl:someValuesFrom obo:UBERON_0001017 .
}
WHERE {
  ?restriction rdf:type owl:Restriction .
  ?restriction owl:onProperty obo:BFO_0000050 .
  ?restriction owl:someValuesFrom obo:UBERON_0000010 .
  ?restriction owl:disjointWith ?innerRestriction .
  ?innerRestriction rdf:type owl:Restriction .
  ?innerRestriction owl:onProperty obo:BFO_0000050 .
  ?innerRestriction owl:someValuesFrom obo:UBERON_0001017 .
}