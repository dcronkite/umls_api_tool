"""
Example program. Get CUIs using specified search terms (or 'covid')

Usage: python get_search_terms.py -k API_KEY [-v current] --search-terms covid
    * the 'src' directory must be on your PYTHONPATH (set/export PYTHONPATH=/path/to/src
"""
from umls_api_tool.args import get_arg_dict
from umls_api_tool.auth import BasicAuthenticator

from loguru import logger


def find_search_terms(apikey, version, search_terms, source_vocabs=None, any_term=False):
    """

    :param source_vocabs:
    :param apikey:
    :param version:
    :param search_terms:
    :param any_term: if True, each term in `search_terms` is executed as a separate search
    :return:
    """
    auth = BasicAuthenticator(apikey)
    if not any_term:
        search_terms = [' '.join(search_terms)]
    for term in search_terms:
        for json_data in _search(auth, version, term, source_vocabs):
            for result in json_data['result']['results']:
                print(f'{result["ui"]},{result["rootSource"]},{result["name"]}')


def _search(auth, version, term, source_vocabs=None):
    if source_vocabs:
        for vocab in source_vocabs:
            if json_data := auth.get('search', version, string=term, sabs=vocab,):
                yield json_data
            else:
                logger.warning(f'No results for "{term}" in "{vocab}"')
    else:
        if json_data := auth.get('search', version, string=term,):
            yield json_data
        else:
            logger.warning(f'No results for "{term}".')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--search-terms', required=False, dest='search_terms', default=('covid',), nargs='+',
                        help='Search for this term (entire string treated as a single search) unless "--any-term"'
                             ' option is specified.')
    parser.add_argument('--source-vocabs', required=False, default=None, dest='source_vocabs', nargs='+',
                        help='Any root source abbreviation in the UMLS. See the "Abbreviation" column for a'
                             ' list of UMLS source vocabulary abbreviations:'
                             ' https://www.nlm.nih.gov/research/umls/sourcereleasedocs/index.html.'
                             ' Note: This currently appears to be broken!')
    parser.add_argument('--any-term', default=False, action='store_true',
                        help='Add flag to search for any of the search terms.')
    find_search_terms(**get_arg_dict(parser))
