from py2neo import Node, Relationship
from .params import *
from .evidence import Evidence


class Feature:
    def __init__(self, type=None, id=None, description=None, position=None,
                 original=None, variation=None, begin_position=None,
                 end_position=None):
        self.type = type
        self.id = id
        self.description = description
        self.position = position
        self.original = original
        self.variation = variation
        self.begin_position = begin_position
        self.end_position = end_position
        self.evidence = None
    
    def parse_attributes(self, node):
        self.type = node.get('type')
        self.description = node.get('description')
        self.id = node.get('id')
        
        evidence = node.get('evidence')
        if evidence is not None:
            self.evidence = Evidence(key=evidence)
        
        original = node.find('uniprot:original', namespaces=NAMESPACES)
        if original is not None:
            self.original = original.text
        
        variation = node.find('uniprot:variation', namespaces=NAMESPACES)
        if variation is not None:
            self.variation = variation.text

        position = node.find('uniprot:location/uniprot:position', namespaces=NAMESPACES)
        if position is not None:
            self.position = position.get('position')

        begin_position = node.find('uniprot:location/uniprot:begin', namespaces=NAMESPACES)
        if begin_position is not None:
            self.begin_position = begin_position.get('position')

        end_position = node.find('uniprot:location/uniprot:end', namespaces=NAMESPACES)
        if end_position is not None:
            self.end_position = end_position.get('position')

    def to_graph(self, graph, entry_node):
        # Save position as Edge attribute - begin position or position, the one that exists
        self.key = self.position if self.position is not None else self.begin_position
        feature_node = Node(Feature.__name__, key=self.key, type=self.type, id=self.id,
                            description=self.description, position=self.position, original=self.original, 
                            variation=self.variation, begin_position=self.begin_position,
                            end_position=self.end_position)
        graph.merge(feature_node, Feature.__name__, "key")

        # Save associated evidence
        if self.evidence is not None:
            self.evidence.to_graph(graph, feature_node)

        graph.merge(Relationship(entry_node, "HAS_FEATURE", feature_node, position=self.key))
