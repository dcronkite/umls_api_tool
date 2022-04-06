"""
Example program. Get all atoms for file of CUIs.

Usage: python cui_to_atoms.py -k API_KEY [-v current]
"""
import csv

from umls_api_tool.args import get_apikey_version
from umls_api_tool.auth import BasicAuthenticator


def cui_to_atoms(apikey, version='current', language='ENG'):
    auth = BasicAuthenticator(apikey)
    cui_data = []
    with open('cui-list.txt') as fh:
        for line in fh:
            cui = line.strip()
            json_data = auth.get(
                'content', version, 'CUI', cui, 'atoms',
                language=language,
            )
            if err := json_data.get('error'):
                print(f'Error for {cui}: {err}')
                continue
            for atom in json_data['result']:
                cui_data.append(
                    {
                        'cui': cui,
                        'aui': atom['ui'],
                        'name': atom['name'],
                        'source': atom['rootSource'],
                        'termtype': atom['termType'],
                    }
                )

    with open('cui-atoms.csv', 'w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=['cui', 'aui', 'name', 'source', 'termtype'])
        writer.writeheader()
        writer.writerows(cui_data)


if __name__ == '__main__':
    apikey, version = get_apikey_version()
    cui_to_atoms(apikey, version)
