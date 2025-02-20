PREFIX pcl: <http://purl.obolibrary.org/obo/PCL_>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

DELETE {
  ?class rdfs:subClassOf ?subClassOf .
  ?subClassOf owl:intersectionOf ?intersection .
}
INSERT {
  ?class rdfs:subClassOf ?restriction .
  ?restriction ?p ?o .
}
WHERE {
  ?class a owl:Class;
            rdfs:subClassOf ?subClassOf .
  ?subClassOf a owl:Class ;
            owl:intersectionOf ?intersection .
  ?intersection rdf:rest*/rdf:first ?restriction .

  ?restriction owl:onProperty <http://purl.obolibrary.org/obo/RO_0015001> .
  ?restriction ?p ?o .
  FILTER( strstarts(str(?class), str(pcl:)) )
}