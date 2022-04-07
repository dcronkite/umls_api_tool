"""
Example program. Creates CSV file from list/file of CUIs.

Usage: python cui_to_details.py -k API_KEY [-v current]
"""
import csv

from umls_api_tool.args import get_apikey_version
from umls_api_tool.auth import BasicAuthenticator, FriendlyAuthenticator


def cui_to_details(apikey, version='current'):
    auth = BasicAuthenticator(apikey)
    cui_data = []
    semtypes = set()  # needed for determining all possible headers
    with open('cui-list.txt') as fh:
        for line in fh:
            cui = line.strip()
            json_data = auth.get(
                'content', version, 'CUI', cui
            )
            if err := json_data.get('error'):
                print(f'Error for {cui}: {err}')
                continue
            curr_semtypes = {semtype['name'] for semtype in json_data['result']['semanticTypes']}
            cui_data.append(
                {
                    'cui': cui,
                    'name': json_data['result']['name'],
                } | {
                    semtype: 1 for semtype in curr_semtypes
                }
            )
            semtypes |= curr_semtypes

    with open('cui-details.csv', 'w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=['cui', 'name'] + list(sorted(semtypes)))
        writer.writeheader()
        writer.writerows(cui_data)


def cui_to_details_friendly(apikey, version='current'):
    """Same as above, but using friendly authenticator."""
    auth = FriendlyAuthenticator.from_apikey(apikey, version)
    cui_data = []
    semtypes = set()  # needed for determining all possible headers
    with open('cui-list.txt') as fh:
        for line in fh:
            cui = line.strip()
            data = auth.get_details_for_cui(cui)
            cui_data.append(
                {
                    'cui': data['cui'],
                    'name': data['name'],
                    'definition': data['definition'],  # not in previous model
                    'source': data['source'],
                } | {
                    semtype: 1 for semtype in data['semtypes']
                }
            )
            semtypes |= set(data['semtypes'])

    with open('cui-details.csv', 'w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=['cui', 'name', 'definition', 'source'] + list(sorted(semtypes)))
        writer.writeheader()
        writer.writerows(cui_data)


if __name__ == '__main__':
    apikey, version = get_apikey_version()
    # cui_to_details(apikey, version)
    cui_to_details_friendly(apikey, version)
