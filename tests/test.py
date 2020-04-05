import time
import json
import threading
import unittest

from websocket_server import WebsocketServer
from graphql_client import *

# The protocol:
# https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md


# Called for every client connecting (after handshake)
def new_client(client, server):
    pass
	# print("[TEST_SERVER] => New client connected and was given id %d" % client['id'])
	# server.send_message_to_all("Hey all, a new client has joined us")


# Called for every client disconnecting
def client_left(client, server):
    pass
	# print("[TEST_SERVER] => Client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message):
    # print("[TEST_SERVER] => Client(%d) said: %s" % (client['id'], message))
    frame = json.loads(message)
    response = mock_server(frame)
    response.send(client, server)


class GQLResponse():
    def __init__(self, payload, time_between=0.1):
        if isinstance(payload, list):
            self._list_response = True
        elif isinstance(payload, dict):
            self._list_response = False

        self.payload = payload
        self.time_between = time_between

    def get_next_payload(self):
        pass

    def send(self, client, server):
        if self._list_response:
            # print('[TEST_SERVER] => Sending a list of messages to the client')
            for response in self.payload:
                # print('[TEST_SERVER] => Sending message to client', response)
                server.send_message(client, json.dumps(response))
                time.sleep(self.time_between)
        else:
            # print('[TEST_SERVER] => Sending message to client', self.payload)
            server.send_message(client, json.dumps(self.payload))


def mock_server(frame):
    if frame['type'] == GQL_CONNECTION_INIT:
        return GQLResponse({'type': GQL_CONNECTION_ACK})

    elif frame['type'] == GQL_START:
        op_id = frame['id']
        if frame['payload']['query'].strip().startswith('subscription'):
            return GQLResponse([
                {'id': op_id, 'type': GQL_DATA, 'payload': {'data': {'msg': 'hello world'}}},
                {'id': op_id, 'type': GQL_DATA, 'payload': {'data': {'msg': 'hello world'}}},
                {'id': op_id, 'type': GQL_DATA, 'payload': {'data': {'msg': 'hello world'}}},
                {'id': op_id, 'type': GQL_COMPLETE}
            ], time_between=0.5)

        return GQLResponse([
            {'id': op_id, 'type': GQL_DATA, 'payload': {'data': {'msg': 'hello world'}}},
            {'id': op_id, 'type': GQL_COMPLETE}
        ], time_between=0.5)

    elif frame['type'] == GQL_STOP:
        return GQLResponse({'id': frame['id'], 'type': GQL_COMPLETE})
        # return GQLResponse({'type': GQL_CONNECTION_KEEP_ALIVE})


class ApolloProtocolServer():
    def __init__(self, port=9001):
        self.port = port
        self.is_running = False
        self.server = None
        self.server_thread = None

    def _serve(self):
        try:
            self.server.run_forever()
        finally:
            self.server.server_close()

    def start_server(self):
        if not self.is_running:
            self.server = WebsocketServer(self.port)
            self.server.set_fn_new_client(new_client)
            self.server.set_fn_client_left(client_left)
            self.server.set_fn_message_received(message_received)

            self.server_thread = threading.Thread(target=self._serve, daemon=True)
            self.server_thread.start()

        self.is_running = True
        # print('[TEST_SERVER] => [DEBUG] => end of start server..')

    def stop_server(self):
        # print('[TEST_SERVER] => [DEBUG] => inside stop server..')
        if self.is_running:
            self.is_running = False
            # print('[TEST_SERVER] => [DEBUG] => calling server_close..')
            self.server.server_close()
            # print('[TEST_SERVER] => [DEBUG] => called server_close..')
            # print('[TEST_SERVER] => [DEBUG] => calling thread.join..')
            self.server_thread.join(timeout=2)
            # print('[TEST_SERVER] => [DEBUG] => called thread.join..')


query = """
query getUser($userId: Int!) {
  user (id: $userId) {
    id
    username
  }
}
"""

subscription = """
subscription getUser($userId: Int!) {
  user (id: $userId) {
    id
    username
  }
}
"""

class TestClient(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws_server = ApolloProtocolServer()

    def setUp(self):
        # print('[TEST] => setUp()')
        self.ws_server.start_server()
        self.client = GraphQLClient('ws://localhost:9001')

    def test_query(self):
        res = self.client.query(query, variables={'userId': 2})
        # print('[TEST] => Got response inside the test', res)
        self.assertTrue(res['type'] == GQL_DATA)

    def test_subscription(self):
        op_ids = []
        all_datas = []
        def my_callback(op_id, data):
            op_ids.append(op_id)
            all_datas.append(data)

        sub_id = self.client.subscribe(subscription, variables={'userId': 2}, callback=my_callback)
        # print('[TEST] => Got response inside the test', sub_id)
        # wait for 3 seconds to finish subscription
        time.sleep(3)
        self.client.stop_subscribe(sub_id)

        for op_id in op_ids:
            self.assertEqual(op_id, sub_id)

        for res in all_datas[:-1]:
            self.assertEqual(res['type'], GQL_DATA)

        self.assertEqual(all_datas[-1]['type'], GQL_COMPLETE)

    def test_multiple_queries(self):
        for _ in range(4):
            res = self.client.query(query, variables={'userId': 2})
            # print('[TEST] => Got response inside the test', res)
            self.assertTrue(res['type'] == GQL_DATA)

    def test_multiple_subscriptions(self):
        op_ids1 = []
        op_ids2 = []
        all_datas1 = []
        all_datas2 = []

        def my_callback1(op_id, data):
            # print('[TEST] => inside callback: ', op_id, data)
            op_ids1.append(op_id)
            all_datas1.append(data)

        def my_callback2(op_id, data):
            # print('[TEST] => inside callback: ', op_id, data)
            op_ids2.append(op_id)
            all_datas2.append(data)

        sub_id1 = self.client.subscribe(subscription, variables={'userId': 2}, callback=my_callback1)
        sub_id2 = self.client.subscribe(subscription, variables={'userId': 2}, callback=my_callback2)

        # wait for 4 seconds to finish subscription
        time.sleep(4)
        self.client.stop_subscribe(sub_id1)
        self.client.stop_subscribe(sub_id2)

        # check invariants for sub_id1
        for op_id in op_ids1:
            self.assertEqual(op_id, sub_id1)

        for res in all_datas1[:-1]:
            self.assertEqual(res['type'], GQL_DATA)

        self.assertEqual(all_datas1[-1]['type'], GQL_COMPLETE)

        # check invariants for sub_id2
        for op_id in op_ids2:
            self.assertEqual(op_id, sub_id2)

        for res in all_datas2[:-1]:
            self.assertEqual(res['type'], GQL_DATA)

        self.assertEqual(all_datas2[-1]['type'], GQL_COMPLETE)

    # TODO: one more testcase with multiple queries and multiple subscriptions mixed

    def tearDown(self):
        # print('[TEST] => tearDown()')
        self.client.close()
        self.ws_server.stop_server()


if __name__ == '__main__':
    unittest.main()
