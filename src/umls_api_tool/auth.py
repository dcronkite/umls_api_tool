import json

import requests
from lxml.html import fromstring


class Authenticator:

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
        r = requests.get(
            '/'.join((self.base_url, *url)),
            params=params | {'ticket': self.get_service_ticket()},
        )
        r.encoding = 'utf-8'
        return json.loads(r.text)
