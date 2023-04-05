from py2neo import Node, Relationship
from .params import *
from .dbreference import DbReference


class Taxon:
    def __init__(self, name=None):
        self.name = name

    def parse_attributes(self, node):
        self.name = node.text

    def to_graph(self, graph, organism_node):
        taxon_node = Node(Taxon.__name__, name=self.name)
        graph.merge(taxon_node, Taxon.__name__, "name")
        graph.merge(Relationship(organism_node, "FROM_TAXON", taxon_node))

        return taxon_node


class Organism:
    def __init__(self, scientific_name=None, common_name=None):
        self.scientific_name = scientific_name
        self.common_name = common_name
        self.lineage = []
        self.dbreferences = []

    def parse_attributes(self, node):
        for name in node.findall('uniprot:name', namespaces=NAMESPACES):
            if name.get('type') == 'scientific':
                self.scientific_name = name.text
            elif name.get('type') == 'common':
                self.common_name = name.text
        
        for dbreference in node.findall('uniprot:dbReference', namespaces=NAMESPACES):
            dbreference_obj = DbReference()
            dbreference_obj.parse_attributes(dbreference)
            self.dbreferences.append(dbreference_obj)
        
        for taxon in node.findall('uniprot:lineage/uniprot:taxon', namespaces=NAMESPACES):
            taxon_obj = Taxon()
            taxon_obj.parse_attributes(taxon)
            self.lineage.append(taxon_obj)

    def to_graph(self, graph, entry_node):
        organism_node = Node(Organism.__name__, scientific_name=self.scientific_name, common_name=self.common_name)
        graph.merge(organism_node, Organism.__name__, "scientific_name")
        
        for dbreference in self.dbreferences:
            dbreference.to_graph(graph, organism_node)

        last_node = organism_node
        for taxon in self.lineage[::-1]:
            taxon_node = taxon.to_graph(graph, last_node)
            last_node = taxon_node

        graph.merge(Relationship(entry_node, "FROM_ORGANISM", organism_node))
        
        return organism_node