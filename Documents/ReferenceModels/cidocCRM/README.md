FactMiners - ICOM CIDOC-CRM into Neo4j via Py2Neo
==========

The FactMiners social-game developers' community will use the ISO-standard Conceptual Reference Model of the international museum community for managing the underlying relationship between digital cultural heritage collection management and hosting a FactMiners Fact Cloud. IOW, the best way to make it easy for museum's and archives to participate in the FactMiners community, is to provide a state-of-the-art flexible, extensible digital cultural heritage collection management platform.

This goal is the basis of our collaboration with the brilliant designer-developers of www.Structr.org, the next-generation Content Management System (a stealth understatement if ever there was one! :-)) built on the Neo4j graph database.

For step one of getting the CRM into Neo4j, this is literally my first Python program. Judge only that it worked well enough to parse the ICOM CIDOC CRM (Conceptual Reference Model) text document and get it into Neo4j where this will serve as a reference model for FactMiners' metamodel construction.

The 0.1 verstion parses the Class Declarations section of the official CIDOC CRM document. This means there is full Class node info but limited Property node info. The next step will address this by parsing the Property Declarations section and 'node-ifying' them in the style of a FactMiners embedded metamodel subgraph.

Thankfully, the Python program and the text version of the source document do not have to be fooled with as I've zipped up the resulting Neo4j database for your pleasure.

This page needs more information and links, etc., but more than that I need some sleep. More soon.

BTW, Axel and Christian, I believe this version of the CIDOC-CRM will be most useful to you for exploring input into a Structr schema via your existing GraphGist Importer feature. More soon...

--Jim Salmons--
Cedar Rapids, Iowa USA
03/26/2014
