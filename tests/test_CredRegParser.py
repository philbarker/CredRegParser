import pytest
from CredReg import CredRegParser
from rdflib import Graph, URIRef, Literal
from json import loads, dumps

cred_reg_base_uri = "https://credentialengineregistry.org/resources/"
ctid = "ce-f1782b95-d234-4237-83e4-48b8c0f538d8"


@pytest.fixture
def empty_parser():
    parser = CredRegParser()
    return parser


@pytest.fixture
def parser():
    parser = CredRegParser(ctid=ctid)
    return parser


@pytest.fixture
def expected_json_str():
    with open("./tests/data/" + ctid) as file:
        expected_json = file.read()
    return expected_json


@pytest.fixture
def expected_json(expected_json_str):
    return loads(expected_json_str)


def test_init(empty_parser):
    assert empty_parser.cr_uri_base == cred_reg_base_uri
    assert empty_parser.md_json == {}
    assert len(empty_parser.md_graph) == 0
    with pytest.raises(RuntimeError):
        # expect erorr for various mal-formed base uris
        parser = CredRegParser(ctid=ctid, base="http:not.valid/uri/")
        parser = CredRegParser(ctid=ctid, base="http://not.valid/uri")


def test_set_resource_uri(empty_parser):
    # FIXME add some mal-formed ctids
    parser = empty_parser
    parser.set_resource_uri(ctid)
    assert (
        parser.resource_uri
        == "https://credentialengineregistry.org/resources/ce-f1782b95-d234-4237-83e4-48b8c0f538d8"
    )
    #    not_a_ctid = "not-a-ctid"
    parser = empty_parser
    with pytest.raises(RuntimeError):
        # expect erorr for various mal-formed ctids
        parser.set_resource_uri("ct-f1782b95-d234-4237-83e4-48b8c0f538d8")
        parser.set_resource_uri("ce-f182b95-d234-4237-83e4-48b8c0f538d8")
        parser.set_resource_uri("ce-f1782b95-g234-4237-83e4-48b8c0f538d8")
        parser.set_resource_uri("ce-f1782b95-d2344237-83e4-48b8c0f538d8")
        parser.set_resource_uri("ce-f1782b95-d234-4237-83ex-48b8c0f538d8")
        parser.set_resource_uri("ce-f1782b95-d234-4237-83e4-48b8c0f538d8")
        parser.set_resource_uri("ce-f1782b95-d234-4237-83e4-48b8c0f538d")


def test_get_json_str(empty_parser, expected_json_str):
    # FIXME: add some non-existant ctids
    parser = empty_parser
    parser.set_resource_uri(ctid)
    json_str = parser._get_json_str()
    assert len(json_str) == len(expected_json_str)
    assert (
        json_str[:100] == expected_json_str[:100]
    )  # after ~100 chars the ordering is arbitrary


def test_set_json(empty_parser, expected_json):
    parser = empty_parser
    parser.set_resource_uri(ctid)
    parser.set_md_json()
    assert len(parser.md_json) == len(expected_json)
    assert parser.md_json["@context"] == expected_json["@context"]
    assert parser.md_json["@id"] == expected_json["@id"]
    assert parser.md_json["@type"] == expected_json["@type"]
    assert parser.md_json["ceterms:name"] == expected_json["ceterms:name"]


def test_get_context(empty_parser):
    parser = empty_parser
    parser.set_resource_uri(ctid)
    parser.set_md_json()
    context_url, context = parser._get_context()
    assert context_url == "https://credreg.net/ctdl/schema/context/json"


def test_extract_namespaces(empty_parser):
    parser = empty_parser
    parser.set_resource_uri(ctid)
    parser.set_md_json()
    context_url, context = parser._get_context()
    assert context_url == "https://credreg.net/ctdl/schema/context/json"
    namespaces = parser._extract_namespaces(context)
    assert namespaces["ceterms"] == "https://purl.org/ctdl/terms/"


def test_set_md_graph(parser):
    assert (
        "ceterms",
        URIRef("https://purl.org/ctdl/terms/"),
    ) in parser.md_graph.namespaces()
    cred = URIRef(
        "https://credentialengineregistry.org/resources/ce-f1782b95-d234-4237-83e4-48b8c0f538d8"
    )
    type_prop = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    expected_type = URIRef("https://purl.org/ctdl/terms/BachelorDegree")
    assert expected_type in parser.md_graph.objects(cred, type_prop)
    assert len(parser.md_graph) == 20
