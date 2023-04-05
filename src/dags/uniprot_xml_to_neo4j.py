from py2neo import Graph
from lxml import etree
from nodes.params import *
from nodes.uniprot_entry import UniProtEntry
from con_params import *


def parse_uniprot_entries(xml_file):
    root = etree.parse(xml_file)
    return root.findall('uniprot:entry', namespaces=NAMESPACES)


def store_in_neo4j(entries, uri, user, password):
    graph = Graph(uri, auth=(user, password))
    for entry in entries:
        entry.to_graph(graph)


def parse_uniprot_entry(entry):
    uniprot_entry = UniProtEntry()
    uniprot_entry.parse_attributes(entry)
    return uniprot_entry


def uniprot_xml_to_neo4j(xml_file):
    entries = parse_uniprot_entries(xml_file)

    uniprot_entries = [parse_uniprot_entry(entry) for entry in entries]

    store_in_neo4j(uniprot_entries, URI, USER, PASSWORD)


def batch_uniprot_xml_to_neo4j(xml_files):
    for xml_file in xml_files:
        uniprot_xml_to_neo4j(xml_file)


if __name__ == '__main__':
    uniprot_xml_to_neo4j('../../data/Q9Y265.xml')
