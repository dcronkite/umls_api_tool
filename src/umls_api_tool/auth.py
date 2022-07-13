import json
import time
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

    def get(self, *url, **params):
        params = {
            'ticket': self.get_service_ticket(),
            'pageSize': 200,
            **params,
        }
        self.request_limiter.ready()
        r = requests.get(
            '/'.join((self.base_url, *url)),
            params=urllib.parse.urlencode(params, safe=','),
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(e)
        r.encoding = 'utf-8'
        return json.loads(r.text)


class LazyAuthenticator:
    """ Authenticator which just pass on the queries to the end user. """

    def __init__(self, authenticator: BasicAuthenticator, version='current'):
        self.auth = authenticator
        self.version = version

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
            'content', version, 'CUI', cui, 'definitions',
            **params
        )

    def get_details_for_cui(self, cui, version=None, **params):
        return self.auth.get(
            'content', version, 'CUI', cui,
            **params
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
