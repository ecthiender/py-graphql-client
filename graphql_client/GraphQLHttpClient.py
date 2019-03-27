import requests

class GraphQLHttpClient:

    def __init__(self, url):
        self.http_url = url

    def query(self, query, variables=None, headers=None):
        payload = { 'headers': headers, 'query' : query, 'variables': variables }
        resp = requests.post(self.http_url, json=payload)
        return resp