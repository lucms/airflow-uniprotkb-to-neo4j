from py2neo import Node, Relationship
from .params import *
from .dbreference import DbReference


class Evidence:
    def __init__(self, type=None, key=None):
        self.type = type
        self.key = key
        self.source = None

    def parse_attributes(self, node):
        self.type = node.get('type')
        self.key = node.get('key')
        source = node.find('uniprot:source/uniprot:dbReference', namespaces=NAMESPACES)
        if source is not None:
            self.source = DbReference()
            self.source.parse_attributes(source)

    def to_graph(self, graph, entry_node):
        evidence_node = Node(Evidence.__name__, type=self.type, key=self.key)
        graph.merge(evidence_node, Evidence.__name__, "key")
        
        if self.source is not None:
            self.source.to_graph(graph, evidence_node)

        graph.merge(Relationship(entry_node, "HAS_EVIDENCE", evidence_node))
        
        return evidence_node
