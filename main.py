from CredReg import CredRegParser, get_args, do_command
import sys

if __name__ ==  "__main__":
    args = get_args()
    parser = CredRegParser()
    do_command(args, parser)
