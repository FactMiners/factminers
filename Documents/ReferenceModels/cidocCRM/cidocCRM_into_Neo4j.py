
##################
##
# Importing the ICOM CIDOC-CRM into Neo4j
# by Jim Salmons, devs_at_factminers.org
#
# Literally my first Python program. Judge only that it worked well enough to parse the
# ICOM CIDOC CRM (Conceptual Reference Model) text document and get it into Neo4j where
# this will serve as a reference model for FactMiners' metamodel construction.
#
# Version 0.1 Parsing the Class Declarations section. Full Class node info, 
# limited Property node info. The next step will address this by parsing
# the Property Declarations section and 'node-ifying' them in the style of a
# FactMiners embedded metamodel subgraph.
#
# EVERYTHING BEYOND HERE IS DUBIOUS. IT RAN WELL ENOUGH FOR ME, that's all I'll say.
#
import re
import time
import codecs
from collections import deque
##
# Get ready for Neo4j
from py2neo import neo4j, cypher, ogm, node, rel
graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
store = ogm.Store(graph_db)
# session = cypher.Session()
# tx = session.create_transaction()
graph_db.clear()
node_index = graph_db.get_or_create_index(neo4j.Node, "crmClassNodes")
rels_index = graph_db.get_or_create_index(neo4j.Relationship, "crmClassRels")

###
##
# OGM class - not used so far... Oops!
#
class CRMclass(object):

    def __init__(self, name=None, subclasses=None, superclasses=None, scopenote=None, examples=None, properties=None, crm_id=None):
        self.name = name
        self.subclasses = subclasses
        self.superclasses = superclasses
        self.scopenote = scopenote
        self.examples = examples
        self.properties = properties
        self.crm_id = crm_id

    def __str__(self):
        return self.name

###
##
# Utility functions
#
def grab_crm_class_per_line(lyne):
    match = re.search(r"^(?P<crm_class>(?P<crm_id>E\d+).+)", lyne.strip(), re.IGNORECASE | re.MULTILINE)
    if match:
        found_class = {"crm_class": match.group("crm_class"), "crm_id": match.group("crm_id")}
    else:
        found_class = ""
    return found_class

def test_for_next_section(lyne, upcoming_sections):
    for next_section in upcoming_sections:
        if lyne.find(next_section) > -1 :
            return True
    return False

def grab_example(lyne):
    match = re.search(r"^[*\s]+(?P<example>.+)", lyne, re.IGNORECASE | re.MULTILINE)
    if match:
        example = match.group("example")
    else:
        example = ""
    return example

def decode_property(property_stmt):
    # reobj = re.compile(r"^(P\d+.+)\((.+)\)\s*:\s(E\d+.+)|^(P\d+.+):\s+(E\d+.+)", re.IGNORECASE | re.MULTILINE)
    reobj = re.compile(r"^((P\d+).+)\((.+)\)\s*:\s(E\d+.+)|^((P\d+).+):\s+(E\d+.+)", re.IGNORECASE | re.MULTILINE)
    match = reobj.search(property_stmt)
    if match:
        if match.group(1) is not None:
            prop_name = match.group(1).strip()
            crm_id = match.group(2)
            recip_name = match.group(3).strip()
            range_name = match.group(4).strip()
        if match.group(5) is not None:
            prop_name = match.group(5).strip()
            crm_id = match.group(6).strip()
            recip_name = None
            range_name = match.group(7).strip()
        neo_name = prop_name.upper().replace(' ', '_')
        prop_spec = {'NEO_NAME' : neo_name,
            'crm_id' : crm_id,
            'prop_name': prop_name, 
            'recip_name': recip_name, 
            'range_name': range_name}
    else:
        # TODO: Handle (props as qualifier?) - currently ignore
        prop_spec = None
    return prop_spec

###
##
# Get the file into memory as an array for walking through...
# Start sucking... line-by-line
#
raw_lines=deque([])                        # will hold the lines of the file

# with open("cidocCRM_WTFmf.txt",'rU') as crm_file:
with open("cidoc_crm_5.1.2_classes_clean.txt",'rU') as crm_file:
    for line in crm_file:                  # for each line of the file
        line=line.rstrip()                  # remove leading and trailing crap
        if line:                           # skip blank lines
            raw_lines.append(line)
crm_file.close()
# Done with the file... let's work on it...

# hold and print raw_lines
start_len = str(len(raw_lines))
print "Starting length: " + start_len

#######
#
# Before creating the Neo4j data, we gather up all the info we need by parsing the text of
# the CRM document. Each CRM class (e.g., E40 Person) is the key in a Dictionary with its
# value being a Dictionary of the section contents for that CRM class.
#
full_crm = dict()

#######
#
# Start the looper-duper to gather up the data by parsing the
# text of the latest 5.1.2 release.
#

# The file's first line is a CRM Class entry's first line...
while len(raw_lines) > 0:
    #Step 0. Prep vars (in the order that these sections appear in the text)
    cur_crmClass = CRMclass()
    setattr(cur_crmClass, 'subclasses', [])
    # Forget OOP above for now...
    cur_class = ""
    cur_crmid = ""
    cur_subclasses = []
    cur_superclasses = []
    cur_scopenote = ""
    cur_examples = []
    cur_properties = []

    # Step 1. Get first line of the file which is our first crm_class
    class_spec = grab_crm_class_per_line(raw_lines.popleft().strip())
    cur_crmid = class_spec['crm_id']
    cur_class = class_spec['crm_class']
    full_crm[cur_class] = {
        "subclasses" : cur_subclasses,
        "superclasses" : cur_superclasses,
        "scopenote" : cur_scopenote,
        "examples" : cur_examples,
        "properties" : cur_properties,
        "crm_id" : cur_crmid
        }

    # Step 2. Subclass (optional)
    #   grab first subclass off same line
    #   grab additional Exx lines
    #   stop on empty line or next sect
    cur_lyne = raw_lines.popleft()
    if cur_lyne.find("Subclass of:") > -1 :
        # Get em...
        # First and maybe only one on this lyne...
        match = re.search(r"^Subclass of:\W+(?P<firstSubclass>E\d+.+)", cur_lyne, re.IGNORECASE | re.MULTILINE)
        if match:
            cur_subclasses.append(match.group("firstSubclass"))
        # any more?
        lines_copy = list(raw_lines)
        for next_lyne in lines_copy:     # First Subclass
            another = grab_crm_class_per_line(next_lyne)
            if another == "":
                cur_lyne = raw_lines.popleft()
                break
            cur_subclasses.append(another['crm_class'])
            cur_lyne = raw_lines.popleft()

    # Step 3. Superclass (optional)
    #   grab first subclass off same line
    #   grab additional Exx lines
    #   stop on empty line or next sect
    if cur_lyne.find("Superclass of:") > -1 :
        # Get em...
        # First and maybe only one on this lyne...
        match = re.search(r"^Superclass of:\W+(?P<firstSuperclass>E\d+.+)", cur_lyne, re.IGNORECASE | re.MULTILINE)
        if match:
            cur_superclasses.append(match.group("firstSuperclass"))
        # any more?
        # cur_lyne = raw_lines.popleft()
        lines_copy = list(raw_lines)
        for next_lyne in lines_copy:     # First superclass
            another = grab_crm_class_per_line(next_lyne)
            if another == "":
                cur_lyne = raw_lines.popleft()
                break
            cur_superclasses.append(another['crm_class'])
            cur_lyne = raw_lines.popleft()

    # Step 4. Scope note (optional)
    #   grab lines until next section
    #   stop on Examples or Properties
    if cur_lyne.find("Scope note:") > -1 :
        cur_scopenote = cur_lyne
        # any more?
        lines_copy = list(raw_lines)
        for next_lyne in lines_copy:     # More note?
            next_section_found = test_for_next_section(next_lyne, ["Examples:", "Properties:"])
            if next_section_found == True:
                cur_lyne = raw_lines.popleft()
                break
            cur_scopenote += "\n" + next_lyne
            cur_lyne = raw_lines.popleft()

    # Step 5. Examples (optional)
    #   grab lines until next section
    #   stop on empty line or next section
    if cur_lyne.find("Examples:") > -1 :
        # Grab them
        lines_copy = list(raw_lines)
        for next_lyne in lines_copy:     # First Example
            example_found = grab_example(next_lyne)
            if example_found != "":
                cur_examples.append(example_found)
                cur_lyne = raw_lines.popleft()
            else:
                if next_lyne.find("Properties:") > -1 :
                    cur_lyne = raw_lines.popleft()
                # else it is likely a CRM Class and is the next item to process...
                break

    # Step 6. Properties (optional)
    #   add props to class-keyed arbitrary
    #   add subprops to class-keyed subprop array array
    #   stop on empty line or next crm_class
    if cur_lyne.find("Properties:") > -1 :
        # Grab them
        lines_copy = list(raw_lines)
        for next_lyne in lines_copy:     # First Property
            crm_class_found = grab_crm_class_per_line(next_lyne)
            if crm_class_found == "":
                # remove tabs and extra space
                next_prop = next_lyne.strip().replace("/t","")
                cur_properties.append(next_prop)
                cur_lyne = raw_lines.popleft()
            else:
                break
                
    # Step 7. Whamo!
    #
    # Add the vitals to the model element dictionary for input to Neo4j
    full_crm[cur_class].update({
        "subclasses" : cur_subclasses,
        "superclasses" : cur_superclasses,
        "scopenote" : cur_scopenote,
        "examples" : cur_examples,
        "properties" : cur_properties
        })
    # Just checking...
    print "CRM Class processed: " + cur_class
    # print "Superclass of: " + ", ".join(cur_superclasses)
    # print "Subclasses: " + ", ".join(cur_subclasses)
    # print scopenote
    # print "Examples: " + ", ".join(cur_examples)
    # print "Properties: " + ", ".join(cur_properties)
print "That is all folks! " + str(len(full_crm))

################################################
#
# Now we put the model elements into Neo4j
#
###
##
# Going into Neo4j via a Py2Neo Cypher transaction so we can hook up
# IS_A 'subclass' and 'property' relationships, etc.
#

# Step 1. Create the 89 'class' nodes
for crm_class, class_info in full_crm.items():
    # Create the node... add scope notes and examples as available...
    props = {'name' : crm_class, 'crm_id' : class_info['crm_id']}
    if 'scopenote' in class_info and len(class_info['scopenote']) > 0 :
        sn = class_info['scopenote']
        props['scopenote'] = sn
    if ('examples' in class_info) and (len(class_info['examples']) > 0) :
        pretty_examples = ""
        # make pretty
        for eg in class_info['examples']:
            pretty_examples = pretty_examples + '* ' + eg + '\n'
        props['examples'] = pretty_examples
    # crm_db = graph_db.create(node(props))
    crm_classNode = graph_db.get_or_create_indexed_node('crmClassNodes', 'name', crm_class, props)

# Step 2. For each node, create an 'IS_A' relationship from their 
#   respective subclasses
for crm_class, class_info in full_crm.items():
    this_classNode = graph_db.get_indexed_node('crmClassNodes', 'name', crm_class)
    if ('subclasses' in class_info) and (len(class_info['subclasses']) > 0) :
        # Get the parent(s) and create the IS_A 'inheritance'/composition relationship
        for parent_name in class_info['subclasses']:
            parent_classNode = graph_db.get_indexed_node('crmClassNodes', 'name', parent_name)
            if parent_classNode is not None:
                # check for existing IS_A rel
                isa_rel = graph_db.match_one(this_classNode, 'IS_A', parent_classNode)
                if isa_rel is None:
                    proto = (this_classNode, 'IS_A', parent_classNode)
                    # result = rels_index.get_or_create()
                    result = rels_index.get_or_create('IS_A', this_classNode['name'] + ' IS_A ' + parent_classNode['name'], proto)
                    print crm_class + " IS_A (subclass of) " + parent_classNode['name']
                else:
                    print "Nothing to see here, move along..."
# Step 3. For each node, create all properties/relationships between domains and ranges
#for crm_class, class_info in full_crm.items():
#    this_classNode = graph_db.get_indexed_node('crmClassNodes', 'name', crm_class)
    if ('properties' in class_info) and (len(class_info['properties']) > 0):
        for prop in class_info['properties']:
            alt_nym = ""
            prop_spec = decode_property(prop)
            if prop_spec is not None:
                if prop_spec['recip_name'] is not None:
                    alt_nym = " (" + prop_spec['recip_name'] + ") "
                range_node = graph_db.get_indexed_node('crmClassNodes', 'name', prop_spec['range_name'])
                if range_node is not None:
                    # check for existing rel
                    isa_rel = graph_db.match_one(this_classNode, prop_spec['NEO_NAME'], range_node)
                    if isa_rel is None:
                        props = {'crm_name': prop_spec['prop_name'], 'crm_id': prop_spec['crm_id']}
                        if prop_spec['recip_name'] is not None:
                            props['recip_name'] = prop_spec['recip_name']
                        proto = (this_classNode, prop_spec['NEO_NAME'], range_node, props)
                        result = rels_index.get_or_create('crmProps', this_classNode['name'] + ' ' + prop_spec['NEO_NAME'] + ' ' + range_node['name'], proto)
                        print "Prop: " + prop_spec['prop_name'] + alt_nym + " | Range: " + prop_spec['range_name']
                    else:
                        print "Nothing to see here, move along..."
            else:
                print "\t*** Type qualifier prop (or problem) :" + prop + " ***"

print "Now, really, that's all, folks! :-)"
