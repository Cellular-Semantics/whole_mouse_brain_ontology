PREFIX pcl: <http://purl.obolibrary.org/obo/PCL_>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

DELETE {
  ?class rdfs:subClassOf ?intersection .
  ?intersection owl:intersectionOf ?list .
#   ?list rdf:rest*/rdf:first ?otherClass .
}
WHERE {
  ?class a owl:Class ;
         rdfs:subClassOf ?intersection .
  ?intersection a owl:Class ;
                owl:intersectionOf ?list .
  ?list rdf:rest*/rdf:first ?otherClass .
  ?otherClass owl:onProperty <http://purl.obolibrary.org/obo/RO_0015001> .
  FILTER( strstarts(str(?class), str(pcl:)) )
}