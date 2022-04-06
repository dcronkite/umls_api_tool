"""
Example program. Get a definition for each CUI.

Usage: python cui_to_best_definition.py -k API_KEY [-v current]
"""
import csv

from umls_api_tool.args import get_apikey_version
from umls_api_tool.auth import BasicAuthenticator


def cui_to_details(apikey, version='current', sabs=None):
    if not sabs:
        sabs = ['MSH', 'NCI']
    sabs = ','.join(sabs)  # this doesn't seem to work?
    auth = BasicAuthenticator(apikey)
    cui_data = []
    with open('cui-list.txt') as fh:
        for line in fh:
            cui = line.strip()
            json_data = auth.get(
                'content', version, 'CUI', cui, 'definitions',
                sabs=sabs, pageSize=1,
            )
            if err := json_data.get('error'):
                print(f'Error for {cui}: {err}')
                continue
            cui_data.append(
                {
                    'cui': cui,
                    'source': json_data['result'][0]['rootSource'],
                    'definition': json_data['result'][0]['value'],
                }
            )

    with open('cui-definitions.csv', 'w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=['cui', 'source', 'definition'])
        writer.writeheader()
        writer.writerows(cui_data)


if __name__ == '__main__':
    apikey, version = get_apikey_version()
    cui_to_details(apikey, version)
