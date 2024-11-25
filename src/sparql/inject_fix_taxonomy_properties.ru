PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

DELETE {
  <http://purl.obolibrary.org/obo/RO_0015003> a owl:AnnotationProperty .
}
INSERT {
  <http://purl.obolibrary.org/obo/RO_0015003> a owl:ObjectProperty .
}
WHERE {
  <http://purl.obolibrary.org/obo/RO_0015003> a owl:AnnotationProperty .
}