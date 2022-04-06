"""
Example program. Maps codes from Human Phenotype Ontology
    to the US Edition of SNOMED CT via UMLS CUIs .

Usage: python crosswalk.py -k API_KEY [-v current]
    * the 'src' directory must be on your PYTHONPATH (set/export PYTHONPATH=/path/to/src
"""
from umls_api_tool.args import get_apikey_version
from umls_api_tool.auth import BasicAuthenticator


def parse_hpo_code_file(apikey, version='current'):
    auth = BasicAuthenticator(apikey)
    with open('hpo-codes.txt') as fh:
        for line in fh:
            code = line.strip()
            json_data = auth.get(
                'crosswalk', version, 'source', 'HPO', code,
                targetSource='SNOMEDCT_US'
            )
            if err := json_data.get('error'):
                print(f'Error for {code}: {err}')
                continue
            for source_atom_cluster in json_data['result']:
                print(
                    f'HPO Code - {code} - \t SNOMEDCT concept -- '
                    f'{source_atom_cluster["ui"]}: {source_atom_cluster["name"]}'
                )


if __name__ == '__main__':
    apikey, version = get_apikey_version()
    parse_hpo_code_file(apikey, version)
