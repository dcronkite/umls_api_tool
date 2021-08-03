import argparse


def get_arg_dict(parser: argparse.ArgumentParser = None):
    """Add apikey and version to arg dict"""
    if not parser:
        parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('-k', '--apikey', required=True,
                        help='Key from UMLS; see https://documentation.uts.nlm.nih.gov/rest/authentication.html')
    parser.add_argument('-v', '--version', default='current',
                        help='Specify UMLS version (e.g., 2015AA)')
    return vars(parser.parse_args())


def get_apikey_version():
    d = get_arg_dict()
    return d['apikey'], d['version']
