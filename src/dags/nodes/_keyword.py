from py2neo import Node, Relationship
from .params import *


class Keyword:
    def __init__(self, id=None, keyword=None):
        self.id = id
        self.keyword = keyword

    def parse_attributes(self, node):
        self.id = node.get('id')
        self.keyword = node.text

    def to_graph(self, graph, entry_node):
        keyword_node = Node(Keyword.__name__, id=self.id, keyword=self.keyword)
        graph.merge(keyword_node, Keyword.__name__, "id")
        graph.merge(Relationship(entry_node, "HAS_KEYWORD", keyword_node))
        
        return keyword_node
