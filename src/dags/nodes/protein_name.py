from py2neo import Node, Relationship
from .params import *


class ProteinName:
    def __init__(self, name=None, short_names=None):
        self.name = name
        self.short_names = short_names
        self.alternative_names = []

    def parse_attributes(self, node):
        # Parse recommended full name and short names 
        recommended_name = node.find('uniprot:recommendedName', namespaces=NAMESPACES)
        if recommended_name is not None:
            self.name = recommended_name.find('uniprot:fullName', namespaces=NAMESPACES).text
            
            # If short names exist, get them
            short_names = recommended_name.findall('uniprot:shortName', namespaces=NAMESPACES)
            if short_names is not None:
                self.short_names = [short_name.text for short_name in short_names]

        # Parse alternative full names and short names
        for name in node.findall('uniprot:alternativeName', namespaces=NAMESPACES):
            alternative_name = name.find('uniprot:fullName', namespaces=NAMESPACES).text

            # If alternative short names exist, get them
            alternative_short_names = name.findall('uniprot:shortName', namespaces=NAMESPACES)
            if alternative_short_names is not None:
                alternative_short_names = [short_name.text for short_name in alternative_short_names]

            # Save alternative name as a ProteinName
            self.alternative_names.append(
                ProteinName(name=alternative_name, short_names=alternative_short_names)
            )

    def to_graph(self, graph, entry_node):
        name_node = Node(ProteinName.__name__, name=self.name, short_names=self.short_names)
        graph.merge(name_node, ProteinName.__name__, "name")
        
        # Save alternative protein names as separate nodes
        for alternative_name in self.alternative_names:
            alternative_name_node = Node(
                ProteinName.__name__,
                name=alternative_name.name,
                 short_names=alternative_name.short_names
            )
            graph.merge(alternative_name_node, ProteinName.__name__, "name")
            graph.merge(Relationship(name_node, "HAS_SYNONYM", alternative_name_node))

        graph.merge(Relationship(entry_node, "HAS_NAME", name_node))
        return name_node
