"""
Example program. Get CUIs using specified search terms (or 'covid')

Usage: python get_search_terms.py -k API_KEY [-v current] --search-terms covid
    * the 'src' directory must be on your PYTHONPATH (set/export PYTHONPATH=/path/to/src
"""
from umls_api_tool.args import get_arg_dict
from umls_api_tool.auth import Authenticator


def find_search_terms(apikey, version, search_terms):
    auth = Authenticator(apikey)
    json_data = auth.get(
        'search', version,
        string=' '.join(search_terms)
    )
    for result in json_data['result']['results']:
        print(f'{result["ui"]}: {result["name"]}')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--search-terms', required=False, dest='search_terms', default=('covid',), nargs='+')
    find_search_terms(**get_arg_dict(parser))

