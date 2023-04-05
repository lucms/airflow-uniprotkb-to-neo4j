from py2neo import Node, Relationship
from .params import *
from .dbreference import DbReference


class Reference:
    def __init__(self, key=None, scopes=None, type=None, date=None, name=None, volume=None,
                 first=None, last=None, db=None, title=None, source_type=None, source_value=None):
        self.key = key
        self.scopes = scopes
        self.type = type
        self.date = date
        self.name = name
        self.volume = volume
        self.first = first
        self.last = last
        self.db = db
        self.title = title
        self.source_type = source_type
        self.source_value = source_value

        self.dbreferences = []
        self.authors = []

    def parse_attributes(self, node):
        self.key = node.get('key')
        self.scopes = [scope.text for scope in node.findall('uniprot:scope', namespaces=NAMESPACES)]
        
        for dbreference in node.findall('uniprot:dbReference', namespaces=NAMESPACES):
            dbreference_obj = DbReference()
            dbreference_obj.parse_attributes(dbreference)
            self.dbreferences.append(dbreference_obj)

        citation = node.find('uniprot:citation', namespaces=NAMESPACES)
        self.type = citation.get('type')
        self.date = citation.get('date')
        self.name = citation.get('name')
        self.volume = citation.get('volume')
        self.first = citation.get('first')
        self.last = citation.get('last')
        self.db = citation.get('db')
        title = citation.find('uniprot:title', namespaces=NAMESPACES)
        if title is not None:
            self.title = title.text

        for author in citation.findall('uniprot:authorList/uniprot:*', namespaces=NAMESPACES):
            author_obj = Author()
            author_obj.parse_attributes(author)
            self.authors.append(author_obj)

    def to_graph(self, graph, entry_node):
        reference_node = Node(Reference.__name__, key=self.key, scopes=self.scopes, type=self.type,
                              date=self.date, name=self.name, volume=self.volume, first=self.first, 
                              last=self.last, db=self.db, title=self.title, source_type=self.source_type, 
                              source_value=self.source_value)
        graph.merge(reference_node, Reference.__name__, "key")

        for elem in self.authors + self.dbreferences:
            elem.to_graph(graph, reference_node)

        graph.merge(Relationship(entry_node, "HAS_REFERENCE", reference_node))


class Author:
    def __init__(self, name=None):
        self.name = name

    def parse_attributes(self, node):
        self.name = node.get('name')

    def to_graph(self, graph, reference_node):
        author_node = Node(Author.__name__, name=self.name)
        graph.merge(author_node, Author.__name__, "name")
        graph.merge(Relationship(reference_node, "HAS_AUTHOR", author_node))
