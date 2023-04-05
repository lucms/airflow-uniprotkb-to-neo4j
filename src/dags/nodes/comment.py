from py2neo import Node, Relationship
from .params import *
from .evidence import Evidence


class Comment:
    def __init__(self, order, entry_name, type=None, name=None, 
                 link=None, text=None, organisms_differ=None,
                 experiments=None, event=None):
        self.order = order
        self.entry_name = entry_name
        self.type = type
        self.name = name
        self.text = text
        self.organisms_differ = organisms_differ
        self.experiments = experiments
        self.event = event
        self.link = link
        self.interactants = []
        self.subcellular_locations = []
        self.isoforms = []
        self.conflict = None
        self.evidences = []

    def parse_attributes(self, node):
        self.type = node.get('type')
        self.name = node.get('name')
        
        organisms_differ = node.find('uniprot:organismsDiffer', namespaces=NAMESPACES)
        if organisms_differ is not None:
            self.organisms_differ = organisms_differ.text
        
        experiments = node.find('uniprot:experiments', namespaces=NAMESPACES)
        if experiments is not None:
            self.experiments = experiments.text
        
        event = node.find('uniprot:event', namespaces=NAMESPACES)
        if event is not None:
            self.event = event.get('type')

        link = node.find('uniprot:link', namespaces=NAMESPACES)
        if link is not None:
            self.link = link.get('uri')

        text = node.find('uniprot:text', namespaces=NAMESPACES)
        
        if text is not None:
            self.text = text.text
            evidences = text.get('evidence')
            if evidences is not None:
                for evidence in evidences.split():
                    evidence_obj = Evidence(key=evidence)
                    self.evidences.append(evidence_obj)
        
        for interactant in node.findall('uniprot:interactant', namespaces=NAMESPACES):
            interactant_obj = Interactant()
            interactant_obj.parse_attributes(interactant)
            self.interactants.append(interactant_obj)

        for subcellular_location in node.findall('uniprot:subcellularLocation', namespaces=NAMESPACES):
            subcellular_location_obj = SubcellularLocation()
            subcellular_location_obj.parse_attributes(subcellular_location)
            self.subcellular_locations.append(subcellular_location_obj)

        for isoform in node.findall('uniprot:isoform', namespaces=NAMESPACES):
            isoform_obj = Isoform()
            isoform_obj.parse_attributes(isoform)
            self.isoforms.append(isoform_obj)

        conflict = node.find('uniprot:conflict', namespaces=NAMESPACES)
        if conflict is not None:
            self.conflict = Conflict()
            self.conflict.parse_attributes(conflict)

    def to_graph(self, graph, entry_node):
        # Creating a unique key to comments, as they don't have one
        self.key = f'{self.order}-{self.type}-{self.entry_name}' 
        comment_node = Node(Comment.__name__, key=self.key, order=self.order, text=self.text,
                            name=self.name, organisms_differ=self.organisms_differ,
                            experiments=self.experiments, event=self.event, link=self.link)

        graph.merge(comment_node, Comment.__name__, "key")
        
        if self.conflict is not None:
            conflict = [self.conflict]
        else:
            conflict = []

        for elem in self.interactants + conflict + self.subcellular_locations + self.isoforms + self.evidences:
            elem.to_graph(graph, comment_node)

        graph.merge(Relationship(entry_node, "HAS_COMMENT", comment_node))


class Interactant:
    def __init__(self, intact_id=None, id=None, label=None):
        self.intact_id = intact_id
        self.id = id
        self.label = label

    def parse_attributes(self, node):
        self.intact_id = node.get('intactId')

        id = node.find('uniprot:id', namespaces=NAMESPACES)
        if id is not None:
            self.id = id.text

        label = node.find('uniprot:label', namespaces=NAMESPACES)
        if label is not None:
            self.label = label.text

    def to_graph(self, graph, comment_node):
        interactant_node = Node(Interactant.__name__, intact_id=self.intact_id, id=self.id, label=self.label)
        graph.merge(interactant_node, Interactant.__name__, "id")
        graph.merge(Relationship(comment_node, "HAS_INTERACTANT", interactant_node))


class SubcellularLocation:
    def __init__(self, location=None):
        self.location = location
        self.evidences = []

    def parse_attributes(self, node):
        location = node.find('uniprot:location', namespaces=NAMESPACES)
        self.location = location.text
        evidence = location.get('evidence')
        if evidence is not None:
            for evidence in location.get('evidence').split():
                evidence_obj = Evidence(key=evidence)
                self.evidences.append(evidence_obj)

    def to_graph(self, graph, comment_node):
        subcellular_location_node = Node(SubcellularLocation.__name__, location=self.location)
        graph.merge(subcellular_location_node, SubcellularLocation.__name__, "location")

        for evidence in self.evidences:
            evidence.to_graph(graph, subcellular_location_node)

        graph.merge(Relationship(comment_node, "HAS_SUBCELLULAR_LOCATION", subcellular_location_node))


class Conflict:
    def __init__(self, type=None, sequence_resource=None, sequence_id=None, sequence_version=None):
        self.type = type
        self.sequence_resource = sequence_resource
        self.sequence_id = sequence_id
        self.sequence_version = sequence_version

    def parse_attributes(self, node):
        self.type = node.get('type')
        sequence = node.find('uniprot:sequence', namespaces=NAMESPACES)
        self.sequence_resource = sequence.get('resource')
        self.sequence_id = sequence.get('id')
        self.sequence_version = sequence.get('version')

    def to_graph(self, graph, comment_node):
        conflict_node = Node(Conflict.__name__,  type=self.type, sequence_resource=self.sequence_resource, 
                             sequence_id=self.sequence_id, sequence_version=self.sequence_version)
        graph.merge(conflict_node, Conflict.__name__, "sequence_id")
        graph.merge(Relationship(comment_node, "HAS_CONFLICT", conflict_node))


class Isoform:
    def __init__(self, id=None, name=None, sequence_type=None, sequence_ref=None):
        self.id = id
        self.name = name
        self.sequence_type = sequence_type
        self.sequence_ref = sequence_ref

    def parse_attributes(self, node):
        self.id = node.find('uniprot:id', namespaces=NAMESPACES).text
        self.name = node.find('uniprot:name', namespaces=NAMESPACES).text
        sequence = node.find('uniprot:sequence', namespaces=NAMESPACES)
        if sequence is not None:
            self.sequence_type = sequence.get('type')
            self.sequence_ref = sequence.get('ref')

    def to_graph(self, graph, comment_node):
        isoform_node = Node(Isoform.__name__, id=self.id, name=self.name,
                            sequence_type=self.sequence_type, sequence_ref=self.sequence_ref)
        graph.merge(isoform_node, Isoform.__name__, "id")
        graph.merge(Relationship(comment_node, "HAS_ISOFORM", isoform_node))

