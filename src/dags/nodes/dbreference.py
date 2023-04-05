from py2neo import Node, Relationship
from .params import *


class DbReference:
    def __init__(self, type=None, id=None):
        self.type = type
        self.id = id
        self.properties = []
        self.molecule = None

    def parse_attributes(self, node):
        self.type = node.get('type')
        self.id = node.get('id')

        molecule = node.find('uniprot:molecule', namespaces=NAMESPACES)
        if molecule is not None:
            self.molecule = Molecule()
            self.molecule.parse_attributes(molecule)
    
        properties = node.findall("uniprot:property", namespaces=NAMESPACES)
        for property in properties:
            property_obj = Property()
            property_obj.parse_attributes(property)
            self.properties.append(property_obj)

    def to_graph(self, graph, entry_node):
        # Setting type+value as id attribute, because two databases could present the same id
        # and this would mess things up
        self.type_id = f'{self.type}-{self.id}'
        dbreference_node = Node(DbReference.__name__, type=self.type, id=self.id, type_id=self.type_id)
        graph.merge(dbreference_node, DbReference.__name__, "type_id")
        
        if self.molecule is not None:
            self.molecule.to_graph(graph, dbreference_node)

        for property in self.properties:
            property.to_graph(graph, dbreference_node)

        graph.merge(Relationship(entry_node, "HAS_DBREFERENCE", dbreference_node))
        
        return dbreference_node


class Property:
    def __init__(self, type=None, value=None):
        self.type = type
        self.value = value

    def parse_attributes(self, node):
        self.type = node.get('type')
        self.value = node.get('value')

    def to_graph(self, graph, dbreference_node):
        property_node = Node(Property.__name__, type=self.type, value=self.value)
        graph.merge(property_node, Property.__name__, "type")
        graph.merge(Relationship(property_node, "HAS_DBREFERENCE", dbreference_node))
        
        return property_node
    

class Molecule:
    def __init__(self, id=None):
        self.type = id

    def parse_attributes(self, node):
        self.id = node.get('id')

    def to_graph(self, graph, dbreference_node):
        molecule_node = Node(Molecule.__name__, id=self.id)
        graph.merge(molecule_node, Molecule.__name__, "id")
        graph.merge(Relationship(molecule_node, "HAS_DBREFERENCE", dbreference_node))
        
        return molecule_node
