PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

DELETE {
  ?term1 owl:disjointWith ?term2 .
  ?axiom ?p ?o .
}
WHERE {
  {
    ?term1 owl:disjointWith ?term2 .
  }
  UNION
  {
    ?axiom a owl:Axiom ;
           owl:annotatedSource ?term1 ;
           owl:annotatedProperty owl:disjointWith ;
           owl:annotatedTarget ?term2 .
    ?axiom ?p ?o .
  }
}