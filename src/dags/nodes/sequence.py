from py2neo import Graph, Node, Relationship, Subgraph
from .params import *


class Sequence:
    def __init__(self, length=None, mass=None, checksum=None, 
                 modified=None, version=None, sequence=None):
        self.length = length
        self.mass = mass
        self.checksum = checksum
        self.modified = modified
        self.version = version
        self.sequence = sequence

    def parse_attributes(self, node):
        self.length = node.get("length")
        self.mass = node.get("mass")
        self.checksum = node.get("checksum")
        self.modified = node.get("modified")
        self.version = node.get("version")
        self.sequence = node.text

    def to_graph(self, graph, entry_node):
        sequence_node = Node(Sequence.__name__, length=self.length, mass=self.mass,
                             checksum=self.checksum, modified=self.modified, version=self.version,
                             sequence=self.sequence)
        graph.merge(sequence_node, Sequence.__name__, "sequence")
        graph.merge(Relationship(entry_node, "HAS_SEQUENCE", sequence_node))
        
        return sequence_node
