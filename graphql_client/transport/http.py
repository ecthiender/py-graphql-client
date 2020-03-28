import requests

from graphql_client.transport.base import GraphQLTransport, TransportException

class HttpTransport(GraphQLTransport):

    def __init__(self, url):
        self.url = url
        self.client = None
        self.headers = None

    def set_session(self, headers=None):
        self.headers = headers
        self._make_client()
        self.client.headers = headers

    def _make_client(self):
        if not self.client:
            self.client = requests.Session()

    def execute(self, operation: str, operation_name: str = None, variables: dict = None) -> dict:
        self._make_client()
        payload = {
            'query': operation,
            'variables': variables,
            'operation_name': operation_name
        }
        resp = self.client.post(self.url, json=payload)

        if resp.status_code <= 200 and resp.status_code >= 400:
            err = f'Received non-200 HTTP response: {resp.status_code}. Body: {resp.text}'
            raise TransportException(err)

        res = resp.json()
        return res

    def stop_all_operations(self):
        self.client.close()
