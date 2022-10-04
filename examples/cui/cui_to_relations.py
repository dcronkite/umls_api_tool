import csv

from umls_api_tool.args import get_apikey_version
from umls_api_tool.auth import FriendlyAuthenticator
from umls_api_tool.request_limiter import TimelyRequestLimiter


def cui_to_relations_friendly(apikey, version='current', language='ENG'):
    auth = FriendlyAuthenticator.from_apikey(apikey, version, TimelyRequestLimiter())
    with open('cui-list.txt') as fh:
        with open('cui-relations.csv', 'w', newline='') as out:
            writer = csv.DictWriter(out, fieldnames=['source_cui', 'target_cui', 'name', 'relation_label',
                                                     'additional_relation_label'])
            writer.writeheader()
            for i, line in enumerate(fh):
                if i > 1:
                    break  # only do 2 lines as this takes a while (and don't want to abuse testing)
                cui = line.strip()
                for atom in auth.get_relations_for_cui(cui, language=language):
                    writer.writerow(atom)


if __name__ == '__main__':
    apikey, version = get_apikey_version()
    cui_to_relations_friendly(apikey, version)
