from py2neo import Node
from .params import *
from .protein_name import ProteinName
from .gene import Gene
from .organism import Organism
from .reference import Reference
from .comment import Comment
from .dbreference import DbReference
from ._keyword import Keyword
from .feature import Feature
from .evidence import Evidence
from .sequence import Sequence


class UniProtEntry:
    def __init__(self, dataset=None, created=None, modified=None, version=None,
                 xmlnamespace=None, primary_accession=None, secondary_accessions=None, 
                 name=None):
        """
        Represents a uniprot entry, with all attributes and related nodes.
        """
        self.dataset = dataset
        self.created = created
        self.modified = modified
        self.version = version
        self.xmlnamespace = xmlnamespace
        self.primary_accession = primary_accession
        self.secondary_accessions = secondary_accessions
        self.name = name
        self.names = None
        self.genes = []
        self.organism = None
        self.references = []
        self.comments = []
        self.dbreferences = []
        self.keywords = []
        self.features = []
        self.evidences = []
        self.sequence = None

    def parse_attributes(self, node):
        """
        Parse UniProtEntry attributes. This method encapsulates the messy XML parsing
        to provide a clean, intuitive interface of UniProt data.
        """
        # Parse direct attributes
        self.dataset = node.get('dataset')
        self.created = node.get('created')
        self.modified = node.get('modified')
        self.version = node.get('version')
        self.xmlnamespace = node.get('xmlnamespace')

        # Parse accessions - primary and secondary
        accessions = [
            accession.text for accession in
            node.findall('uniprot:accession', namespaces=NAMESPACES)
        ]
        self.primary_accession = accessions[0]
        if len(accessions) > 1:
            self.secondary_accessions = accessions[1:]

        # Parse uniprot name
        self.name = node.find('uniprot:name', namespaces=NAMESPACES).text
        
        # Parse protein names
        self.names = ProteinName()
        self.names.parse_attributes(node.find('uniprot:protein', namespaces=NAMESPACES))
        
        # Parse genes
        for gene in node.findall('uniprot:gene', namespaces=NAMESPACES):
            gene_node = Gene()
            gene_node.parse_attributes(gene)
            self.genes.append(gene_node)

        # Parse organism
        organism = node.find('uniprot:organism', namespaces=NAMESPACES)
        self.organism = Organism()
        self.organism.parse_attributes(organism)

        # Parse references
        for reference in node.findall('uniprot:reference', namespaces=NAMESPACES):
            reference_obj = Reference()
            reference_obj.parse_attributes(reference)
            self.references.append(reference_obj)

        # Parse comments - order is important here!
        for order, comment in enumerate(node.findall('uniprot:comment', namespaces=NAMESPACES)):
            comment_obj = Comment(order, self.name)
            comment_obj.parse_attributes(comment)
            self.comments.append(comment_obj)

        # Parse db references
        for dbreference in node.findall('uniprot:dbReference', namespaces=NAMESPACES):
            dbreference_obj = DbReference()
            dbreference_obj.parse_attributes(dbreference)
            self.dbreferences.append(dbreference_obj)

        # Parse keywords
        for keyword in node.findall('uniprot:keyword', namespaces=NAMESPACES):
            keyword_obj = Keyword()
            keyword_obj.parse_attributes(keyword)
            self.keywords.append(keyword_obj)

        # Parse features
        for feature in node.findall('uniprot:feature', namespaces=NAMESPACES):
            feature_obj = Feature()
            feature_obj.parse_attributes(feature)
            self.features.append(feature_obj)

        # Parse evidences
        for evidence in node.findall('uniprot:evidence', namespaces=NAMESPACES):
            evidence_obj = Evidence()
            evidence_obj.parse_attributes(evidence)
            self.evidences.append(evidence_obj)

        # Parse sequence
        sequence = node.find('uniprot:sequence', namespaces=NAMESPACES)
        self.sequence = Sequence()
        self.sequence.parse_attributes(sequence)

    def to_graph(self, graph):
        # Create a Node with UniProtEntry data
        entry_node = Node(UniProtEntry.__name__, dataset=self.dataset, created=self.created,
                          modified=self.modified, version=self.version, xmlnamespace=self.xmlnamespace,
                          primary_accession=self.primary_accession,
                          secondary_accessions=self.secondary_accessions, name=self.name)
        
        # Write UniProtEntry Node to neo4j database
        graph.merge(entry_node, UniProtEntry.__name__, "name")

        # Write Nodes related to the UniProtEntry Node to neo4j database
        elements = (self.genes + [self.names, self.organism, self.sequence] +
                    self.dbreferences + self.keywords + self.references + self.comments +
                    self.features + self.evidences)
        for elem in elements:
            elem.to_graph(graph, entry_node)