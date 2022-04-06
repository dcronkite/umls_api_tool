import json
import urllib.parse
from typing import Iterator

import requests
from lxml.html import fromstring
from loguru import logger


class BasicAuthenticator:

    def __init__(self, apikey):
        self.time_granting_ticket = self.get_time_granting_ticket(apikey)
        self.base_url = 'https://uts-ws.nlm.nih.gov/rest'

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
        if not params:
            params = {
                'ticket': self.get_service_ticket(),
                'pageSize': 200,
            }
        else:
            params = {
                'ticket': self.get_service_ticket(),
                'pageSize': 200,
                **params,
            }
        r = None
        try:
            r = requests.get(
                '/'.join((self.base_url, *url)),
                params=urllib.parse.urlencode(params, safe=','),
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(e)
            if r:
                print(r.text)
            raise e
        r.encoding = 'utf-8'
        return json.loads(r.text)


class LazyAuthenticator:
    """ Authenticator which just pass on the queries to the end user. """

    def __init__(self, apikey, version='current'):
        self.auth = BasicAuthenticator(apikey)
        self.version = version

    def get_atoms_for_cui(self, cui, version=None, **params):
        return self.auth.get(
            'content', version or self.version, 'CUI', cui, 'atoms',
            **params,
        )


class FriendlyAuthenticator:
    """Attempts to format results and provide iterators. If you want more control, try Lazy or Basic."""

    def __init__(self, apikey, version='current'):
        self.auth = LazyAuthenticator(apikey)
        self.version = version

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
