PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX PCL: <http://purl.obolibrary.org/obo/PCL_>

DELETE {
	?sub ?property ?value .
}

INSERT {
    ?sub ?property ?new_value.
}

WHERE {
    VALUES ?property {owl:deprecated}
    ?sub ?property ?value .
    FILTER(Datatype(?value)!=xsd:boolean)
    BIND(xsd:boolean(?value) as ?new_value)
}