FactMiners - ICOM CIDOC-CRM (AKA #cidocCRM)
==========

These are one-off and work-in-process workspaces for FactMiners design and development activity related to use of the CIDOC Conceptual Reference Model within the Reference Models partition of the metamodel subgraph partition of a FactMiners Fact Cloud.

My first brute-force effort was to use py2Neo to get the #cidocCRM Definition document parsed and imported into a Neo4j graph database.

My challenges in decyphering the full text of this reference document were enough to put me on a different path when the CIDOC SIG published the 6.0 release of the model. Rather than continually tweak the parsing scripts regexes and assumptions about overall document structure, it occured to me that the #cidocCRM would benefit from being converted to a TEI P5 document!

With a P5 version of the #cidocCRM Definition document, metamodelers and developers would be able to immediately jump to importing or referencing directly the official edition of the CIDOC CRM Definition.

--Jim Salmons--
Cedar Rapids, Iowa USA
03/26/2015

