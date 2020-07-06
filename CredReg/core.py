from rdflib import Graph, URIRef, plugin
from urllib.error import HTTPError

# import requests
from json import loads, dumps
from cache_requests import Session
import re

requests = Session()


class CredRegParser:
    """Handles interactions with the Credential Registry, to get data and store it as a json dict and rdf graph.

    Attributes
    ----------
    cr_uri_base  : str
        The base uri for the Credential Registry
    resource_uri : str
        The Credential Registry uri for the resource
    status_code  : str
        The status code returned from the Registry when getting the resource
    md_json    : dict
        The JSON data about the resource from the Registry
    md_graph   : rdflib Graph
        The data from about the resource as a RDF graph

    Methods
    -------
    def __init__(ctid="": str, base="https://credentialengineregistry.org/resources/": str)
        Create new parser with cr_uri_base attribute set to value of base; if ctid for resource is set, fetch and store metadata for it.
    set_base_uri(base: str):
        Set the base_uri attribute to the given parameter
    set_resource_uri(ctid: str)
        set the resource_uri attribute given the ctid if it matches a http[s] URI pattern
    set_md_json()
        attempt to get the json metadata and store it as md_json
    set_md_graph()
        attempt to get the json metadata and store it as md_graph
    """

    def __init__(self, ctid="", base="https://credentialengineregistry.org/resources/"):
        """Create new parser with cr_uri_base attribute set to value of base; if ctid for resource is set, fetch and store metadata for it."""

        self.set_base_uri(base)
        if ctid == "":
            self.resource_uri = ""
            self.md_json = dict()
            self.md_graph = Graph()
            self.status_code = ""
        else:
            self.status_code = ""
            self.set_resource_uri(ctid)
            self.set_md_json()
            self.set_md_graph()

    def set_base_uri(self, base: str):
        """Set the resource_uri attribute given the ctid if it matches a http[s] URI pattern"""
        if (base[:7] == "http://" or base[:8] == "https://") and base[-1:] == "/":
            self.cr_uri_base = base
        else:
            msg = 'Base uri must start with "http[s]://" and end with "/". '
            msg = msg + "Base uri %s does not." % base
            raise RuntimeError(msg)
        return self

    def set_resource_uri(self, ctid: str):
        """set the resource_uri attribute given the ctid"""
        # some sanity tests on the ctid
        # typical ctid: ce-f1782b95-d234-4237-83e4-48b8c0f538d8
        ctid_pattern = re.compile("^ce-[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$")
        if ctid_pattern.match(ctid):
            self.resource_uri = self.cr_uri_base + ctid
        else:
            msg = "%s does not look like a valid ctid." % ctid
            raise RuntimeError(msg)
        return self

    def _get_json_str(self):
        """Get metadata from the registry for the resource, if resource_uri is set; raise RuntimeError if resource_uri is not set or if status_code indicates an error"""
        if self.resource_uri != "":
            response = requests.get(self.resource_uri)
        else:
            msg = "Set resource uri before trying to get json str from it."
            raise RuntimeError(msg)
        if response.status_code < 300:
            self.status_code = str(response.status_code)
            return response.status_code, response.text
        else:
            return response.status_code, "no data returned"

    def set_md_json(self):
        # fixme: check for errors from get_json_str before setting md_json
        status_code, text = self._get_json_str()
        if status_code < 300:
            self.md_json = loads(text)
            return self
        else:
            msg = "No data returned for resource ctid %s. Code %s" % (
                self.resource_uri,
                status_code,
            )
            raise RuntimeError(msg)

    def _get_context(self):
        context_url = self.md_json["@context"]
        if context_url[:4] == "http":
            # note use of cache_requests above
            response = requests.get(context_url)
        else:
            msg = "Error getting context, context is not a url"
            raise RuntimeError(msg)
        if response.status_code < 300:
            data = loads(response.text)
        else:
            msg = "Error retrieving context. HTTP status code: " + str(
                response.status_code
            )
            raise RuntimeError(msg)
        return context_url, data["@context"]

    def _extract_namespaces(self, context):
        namespaces = dict()
        for key in context.keys():
            if (type(context[key]) is str) and (context[key][:4] == "http"):
                namespaces[key] = context[key]
        return namespaces

    def set_md_graph(self):
        """Get the json metadata for resource self.resource_uri and store it as md_graph"""
        md_graph = Graph()
        # the following were to get the context and set namespaces, but that seems to be handled by Graph.parse()
        #        context_url, context = self._get_context()
        #        namespaces = self._extract_namespaces(context)
        #        for ns in namespaces.keys():
        #            uri = URIRef(namespaces[ns])
        #            md_graph.bind(ns, uri)
        if self.resource_uri == "":
            msg = "Set cred uri before trying to get its metadata."
            raise RuntimeError(msg)
        else:
            try:
                md_graph.parse(location=self.resource_uri, format="json-ld")
                self.md_graph = md_graph
            except HTTPError as h:
                msg = h.url + " " + str(h.code) + " " + h.msg
                raise RuntimeError(msg)
            except Exception as e:
                raise e
        return self

    def dump_md_graph(self):
        print(self.md_graph.serialize(format="ttl").decode("utf-8"))
