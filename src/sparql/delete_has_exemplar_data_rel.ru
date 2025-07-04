PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

DELETE {
  ?s rdfs:subClassOf ?restriction .
  ?restriction owl:onProperty <http://purl.obolibrary.org/obo/RO_0015001> .
  ?restriction owl:hasValue ?value .
}
WHERE {
  ?s rdfs:subClassOf ?restriction .
  ?restriction owl:onProperty <http://purl.obolibrary.org/obo/RO_0015001> ;
               owl:hasValue ?value .
  FILTER(STRSTARTS(STR(?value), "https://purl.brain-bican.org/taxonomy/CCN20230722/"))
} ;

DELETE {
  ?s owl:equivalentClass ?equiv .
  ?equiv owl:intersectionOf ?list .
  ?item owl:onProperty <http://purl.obolibrary.org/obo/RO_0015001> .
  ?item owl:hasValue ?value .
}
WHERE {
  ?s owl:equivalentClass ?equiv .
  ?equiv owl:intersectionOf ?list .
  ?list rdf:rest*/rdf:first ?item .
  ?item owl:onProperty <http://purl.obolibrary.org/obo/RO_0015001> ;
         owl:hasValue ?value .
  FILTER(STRSTARTS(STR(?value), "https://purl.brain-bican.org/taxonomy/CCN20230722/"))
}