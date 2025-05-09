# unpacks following pattern:
#
#         <owl:equivalentClass>
#             <owl:Class>
#                 <owl:intersectionOf rdf:parseType="Collection">
#                     <rdf:Description rdf:about="http://purl.obolibrary.org/obo/CL_0000000"/>
#                     <owl:Restriction>
#                         <owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/RO_0015001"/>
#                         <owl:hasValue rdf:resource="https://purl.brain-bican.org/taxonomy/CCN20230722/CS20230722_CLAS_21"/>
#                     </owl:Restriction>
#                     <owl:Restriction>
#                         <owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/RO_0015001"/>
#                         <owl:hasValue rdf:resource="https://purl.brain-bican.org/taxonomy/CCN20230722/CS20230722_SUBC_215"/>
#                     </owl:Restriction>
#                 </owl:intersectionOf>
#             </owl:Class>
#         </owl:equivalentClass>
#
# into multiple restrictions:
#
#         <owl:equivalentClass>
#             <owl:Class>
#                 <owl:intersectionOf rdf:parseType="Collection">
#                     <rdf:Description rdf:about="http://purl.obolibrary.org/obo/CL_0000000"/>
#                     <owl:Restriction>
#                         <owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/RO_0015001"/>
#                         <owl:hasValue rdf:resource="https://purl.brain-bican.org/taxonomy/CCN20230722/CS20230722_CLAS_21"/>
#                     </owl:Restriction>
#                 </owl:intersectionOf>
#             </owl:Class>
#         </owl:equivalentClass>
#
# and deletes the original owl:equivalentClass owl:intersectionOf owl:Class pattern

PREFIX pcl: <http://purl.obolibrary.org/obo/PCL_>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

DELETE {
  ?class owl:equivalentClass ?equivClass .
  ?equivClass owl:intersectionOf ?intersection .
}
INSERT {
  ?class owl:equivalentClass ?newEquivalentClass .
  ?newEquivalentClass owl:intersectionOf ?newIntersection .
  ?newIntersection rdf:first ?description .
  ?newIntersection rdf:rest ?rest .
  ?rest rdf:first ?restriction .
  ?rest rdf:rest rdf:nil .
}
WHERE {
  ?class a owl:Class;
            owl:equivalentClass ?equivClass .
  ?equivClass a owl:Class ;
              owl:intersectionOf ?intersection .
  ?intersection rdf:first ?description ;
                rdf:rest ?restList .
  ?restList rdf:rest*/rdf:first ?restriction .
  ?restriction owl:onProperty <http://purl.obolibrary.org/obo/RO_0015001> ;
               owl:hasValue ?value .

  BIND (BNODE() AS ?newEquivalentClass)
  BIND (BNODE() AS ?newIntersection)
  BIND (BNODE() AS ?rest)
  FILTER( strstarts(str(?class), str(pcl:)) )
}