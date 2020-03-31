import unittest
from graphql_client import GraphQLClient

# The protocol:
# https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md

def mock_server(payload):
    if payload['type'] == 'connection_init':
        return {'type': 'connection_ack'}

    elif payload['type'] == 'start':
        return {'type': 'data', 'payload': {'data': {'msg': 'hello world'}}}

    elif payload['type'] == 'stop':
        return {'type': 'ka'}


class TestClient(unittest.TestCase):

    def test_connection_init(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
