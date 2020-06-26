import argparse


def get_args():
    p = argparse.ArgumentParser(
        prog="main.py",
        description="Get and optionally print data about a resource in the Credential Registry",
        epilog="Please note this is unfinished and buggy",
    )
    p.add_argument(
        "-c",
        "--ctid",
        type=str,
        required=False,
        default="ce-f1782b95-d234-4237-83e4-48b8c0f538d8",
        help="The ctid of the resource in the Credential Registry",
    )
    p.add_argument(
        "-b",
        "--base",
        required=False,
        type=str,
        default="https://credentialengineregistry.org/resources/",
        help="The base URI for the Credential Registry",
    )
    p.add_argument(
        "-j",
        "--jsonld",
        action="store_true",
        help="Retrieve the json-ld representation of the resource metadata",
    )
    p.add_argument(
        "-g",
        "--graph",
        action="store_true",
        help="Retrieve the resource metadata as an RDF Graph",
    )
    p.add_argument(
        "-d",
        "--dump",
        action="store_true",
        help="Print the JSON-LD or graph metadata as Turtle",
    )
    return p.parse_args()


def do_command(args, parser):
    """Read data from Credential Engine Registry and optionally dump it as JSON-LD or RDF TTL"""
    #    CredRegParser().set_resource_uri(ctid).set_md_graph().dump_md_graph()
    ctid = args.ctid
    base = args.base
    parser.set_base_uri(base)
    parser.set_resource_uri(ctid)
    if args.jsonld:
        parser.set_md_json()
        if args.dump:
            print(parser.md_json)
    if args.graph:
        parser.set_md_graph()
        if args.dump:
            parser.dump_md_graph()
