from py2neo import Node, Relationship
from .params import *


class Gene:
    def __init__(self, name=None, synonyms=None):
        self.name = name
        self.synonyms = synonyms if synonyms is not None else []
    
    def parse_attributes(self, node):
        for gene_name in node.findall('uniprot:name', namespaces=NAMESPACES):
            if gene_name.get('type') == 'primary':
                self.name = gene_name.text
            elif gene_name.get('type') == 'synonym':
                self.synonyms.append(gene_name.text)

    def to_graph(self, graph, entry_node):
        gene_node = Node(Gene.__name__, name=self.name, synonyms=self.synonyms)
        graph.merge(gene_node, Gene.__name__, "name")
        graph.merge(Relationship(entry_node, "FROM_GENE", gene_node))
        
        return gene_node
