import json
import urllib.parse
from typing import Iterator

import requests
from lxml.html import fromstring
from loguru import logger

from umls_api_tool.request_limiter import TimelyRequestLimiter


class BasicAuthenticator:

    def __init__(self, apikey, request_limiter=None):
        self.time_granting_ticket = self.get_time_granting_ticket(apikey)
        self.base_url = 'https://uts-ws.nlm.nih.gov/rest'
        self._message_count = 0
        self.request_limiter = request_limiter if request_limiter else TimelyRequestLimiter()

    @staticmethod
    def get_time_granting_ticket(apikey):
        r = requests.post(
            f'https://utslogin.nlm.nih.gov/cas/v1/api-key',
            data={'apikey': apikey},
            headers={
                'Content-type': 'application/x-www-form-urlencoded',
                'Accept': 'text/plain',
                'User-Agent': 'python'
            },
        )
        return fromstring(r.text).xpath('//form/@action')[0]

    def get_service_ticket(self):
        self.request_limiter.ready()
        r = requests.post(
            self.time_granting_ticket,
            data={'service': 'http://umlsks.nlm.nih.gov'},
            headers={
                'Content-type': 'application/x-www-form-urlencoded',
                'Accept': 'text/plain',
                'User-Agent': 'python'
            },
        )
        return r.text

    def _build_url(self, *url):
        if len(url) == 1 and url[0].startswith('https'):
            return url[0]
        else:
            return '/'.join((self.base_url, *url))

    def _has_error(self, data: dict):
        if 'status' in data:
            logger.error(data)
            return True
        return False

    def get(self, *url, limit_pages=None, **params):
        """

        :param url: destination to query
        :param limit_pages: return no more than this number of pages (None/0 will be interpreted as return everything)
        :param params: these will be passed onto the UTS UMLS API
        :return:
        """
        results = {'result': []}
        page_number = 1
        page_count = 1  # init to 1, will be updated each iteration
        params = {
            'pageSize': 25,
            'pageNumber': page_number,
            **params,
        }
        while page_number <= page_count:
            if limit_pages and limit_pages > page_number:
                # return early if, e.g., testing: just grab the first page
                return results
            # get service ticket
            params['ticket'] = self.get_service_ticket()
            self.request_limiter.ready()
            r = requests.get(
                self._build_url(*url),
                params=urllib.parse.urlencode(params, safe=','),
            )
            # check for errors
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.error(e)
            # read result data
            r.encoding = 'utf-8'
            if r.status_code == 502:
                logger.error(r.text)
                raise ValueError(r.text)
            result = json.loads(r.text)
            if self._has_error(result):
                return results
            # prepare for retrieving subsequent pages
            page_number = result['pageNumber'] + 1  # prepare to get next page
            params['pageNumber'] = page_number
            page_count = result.get('pageCount', result.get('recCount', 1))  # check for single-page results
            if page_count == 1:
                return result
            results['result'] += result['result']
        return results


class LazyAuthenticator:
    """ Authenticator which just pass on the queries to the end user. """

    def __init__(self, authenticator: BasicAuthenticator, version='current'):
        self.auth = authenticator
        self.version = version

    def get(self, *url, **params):
        return self.auth.get(*url, **params)

    @classmethod
    def from_apikey(cls, apikey, version='current', request_limiter=None):
        return cls(BasicAuthenticator(apikey, request_limiter=request_limiter), version=version)

    def get_atoms_for_cui(self, cui, version=None, **params):
        return self.auth.get(
            'content', version or self.version, 'CUI', cui, 'atoms',
            **params,
        )

    def get_definitions_for_cui(self, cui, version=None, **params):
        return self.auth.get(
            'content', version or self.version, 'CUI', cui, 'definitions',
            **params
        )

    def get_details_for_cui(self, cui, version=None, **params):
        return self.auth.get(
            'content', version or self.version, 'CUI', cui,
            **params
        )

    def get_relations_for_cui(self, cui, version=None, **params):
        return self.auth.get(
            'content', version or self.version, 'CUI', cui, 'relations',
            **params,
        )


class FriendlyAuthenticator:
    """Attempts to format results and provide iterators. If you want more control, try Lazy or Basic."""

    def __init__(self, authenticator: BasicAuthenticator, version='current'):
        self.auth = LazyAuthenticator(authenticator, version=version)
        self.version = version

    @classmethod
    def from_apikey(cls, apikey, version='current', request_limiter=None):
        return cls(BasicAuthenticator(apikey, request_limiter=request_limiter), version=version)

    def _check_error(self, data, context):
        if err := data.get('error'):
            logger.warning(f'Error for {context}: {err}')
            return True
        return False

    def get_atoms_for_cui(self, cui, version=None, **params) -> Iterator[dict]:
        """Returns generator spitting out the next atom"""
        data = self.auth.get_atoms_for_cui(cui, version or self.version, **params)
        if self._check_error(data, cui):
            return None
        for atom in data['result']:
            yield {
                'cui': cui,
                'aui': atom['ui'],
                'name': atom['name'],
                'source': atom['rootSource'],
                'termtype': atom['termType'],
            }

    def get_definitions_for_cui(self, cui, version=None, **params) -> Iterator[dict]:
        data = self.auth.get_definitions_for_cui(cui, version or self.version, **params)
        if self._check_error(data, cui):
            return None
        for definition in data['result']:
            yield {
                'cui': cui,
                'source': definition['rootSource'],
                'definition': definition['value'],
            }

    def get_details_for_cui(self, cui, version=None, **params) -> dict:
        data = self.auth.get_details_for_cui(cui, version or self.version, **params)
        try:
            definition = next(self.get_definitions_for_cui(cui, pageSize=1, **params))
        except StopIteration:
            definition = None
        if self._check_error(data, cui):
            return None
        details = data['result']
        return {
            'cui': cui,
            'name': details['name'],
            'definition': definition['definition'] if definition else '',
            'source': definition['source'] if definition else '',
            'semtypes': [semtype['name'] for semtype in details['semanticTypes']],
        }

    def get_relations_for_cui(self, cui, version=None, **params) -> dict:
        data = self.auth.get_relations_for_cui(cui, version or self.version, **params)
        if self._check_error(data, cui):
            return None
        found_cuis = set()  # cui, relation -> to prevent dupes
        related_ids = set()  # to prevent duplicates/excess queries
        for relation in data['result']:
            # don't call again if this was already found
            if relation['relatedIdName'] in related_ids:
                continue
            related_ids.add(relation['relatedIdName'])
            # get relevant CUI
            relation_label = relation['relationLabel']
            addl_relation_label = relation['additionalRelationLabel']
            rel_data = self.auth.get(relation['relatedId'])['result']
            if (cui_url := rel_data.get('concepts', rel_data.get('concept', None))) is not None:
                cui_data = self.auth.get(cui_url)
            else:
                logger.warning(f'Failed to identify concept: {rel_data}')
                continue
            if not cui_data:
                logger.warning(f'Failed: {rel_data}')
                continue
            cui_data = cui_data['result']
            if 'results' in cui_data:
                target_cui = cui_data['results'][0]['ui']
                name = cui_data['results'][0]['name']
            else:
                target_cui = cui_data['ui']
                name = cui_data['name']
            if (cui_group := (target_cui, relation_label, addl_relation_label)) not in found_cuis:
                found_cuis.add(cui_group)
                yield {
                    'source_cui': cui,
                    'target_cui': target_cui,
                    'name': name,
                    'relation_label': relation_label,
                    'additional_relation_label': addl_relation_label,
                }
