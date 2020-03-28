"""
The Websocket transport implementation for the apollo-ws-transport protocol
Apollo protocol: https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md
"""

import string
import os
import random
import sys
import json
import logging
import threading

import websocket

from graphql_client.transport.base import GraphQLTransport, TransportException

# subprotocol header
GQL_WS_SUBPROTOCOL = "graphql-ws"

# all the protocol message types
# https://github.com/apollographql/subscriptions-transport-ws/blob/master/src/message-types.ts
GQL_CONNECTION_INIT = 'connection_init' # Client -> Server
GQL_CONNECTION_ACK = 'connection_ack'   # Server -> Client
GQL_CONNECTION_ERROR = 'connection_error' # Server -> Client

GQL_CONNECTION_KEEP_ALIVE = 'ka' # Server -> Client

GQL_CONNECTION_TERMINATE = 'connection_terminate' # Client -> Server
GQL_START = 'start'                               # Client -> Server
GQL_DATA = 'data'                                 # Server -> Client
GQL_ERROR = 'error'                               # Server -> Client
GQL_STOP = 'stop'                                 # Client -> Server
GQL_COMPLETE = 'complete'                         # Server -> Client

DEBUG = os.getenv('DEBUG', False)
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)


class ConnectionException(Exception):
    """Exception thrown during connection errors to the GraphQL server"""


class WebsocketClient():
    def __init__(self, url):
        self.ws_url = url
        self._connection = websocket.create_connection(self.ws_url,
                                                       subprotocols=[GQL_WS_SUBPROTOCOL])

    def _start_server_receive_thread(self):
        """start a thread, which keeps receiving messages from the server and puts it
        in a queue"""

        while True:
            _upstream_data = self._connection.recv()
            try:
                payload = json.loads(_upstream_data)
            except json.JSONDecodeError as err:
                # JUST BLOW UP!
                print(f'Server sent invalid JSON data: {_upstream_data} \n {err}')
                sys.exit(1)
            print(payload)

    def send(self, payload):
        self._connection.send(json.dumps(payload))

    def receive(self):
        return self._connection.recv()

    def close(self):
        return self._connection.close()


class WebsocketTransport(GraphQLTransport):
    def __init__(self, url):
        self.server_url = url
        self.client = None
        self.headers = None
        self._connection_init_done = False
        self._operation_map = {}

    def _make_client(self):
        if not self.client:
            self.client = WebsocketClient(self.server_url)

    def _wait_for(self, message_types, operation_id=None, retries=10):
        if retries == 0:
            raise TransportException('unexpected error: retries over; no response from server')
        resp = self.client.receive()
        logging.debug(f'server frame <= {resp}')
        res = json.loads(resp)
        if operation_id and not self._operation_map[operation_id]['running']:
            return res
        if res['type'] in message_types:
            return res
        return self._wait_for(message_types, operation_id, retries=retries-1)

    def _send_msg(self, msg, payload=None, operation_id=None):
        self._make_client()
        frame = {'type': msg}
        if payload:
            frame['payload'] = payload
        if operation_id:
            frame['id'] = operation_id
        logging.debug(f'client frame => {frame}')
        self.client.send(frame)

    def set_session(self, headers=None):
        self.headers = headers
        self._send_msg(GQL_CONNECTION_INIT, payload={'headers': headers})
        res = self._wait_for([GQL_CONNECTION_ACK, GQL_CONNECTION_ERROR])
        if res['type'] == GQL_CONNECTION_ACK:
            self._connection_init_done = True
        elif res['type'] == GQL_CONNECTION_ERROR:
            self._connection_init_done = False
            raise ConnectionException(f'could not initialise session with headers: {headers}')

    def execute(self, operation, operation_name=None, variables=None) -> dict:
        if not self._connection_init_done:
            self.set_session()

        self._send_msg(GQL_START, operation_id=gen_id(),
                       payload={'query': operation, 'variables': variables,
                                'operation_name': operation_name})

        res = self._wait_for([GQL_DATA, GQL_ERROR, GQL_CONNECTION_ERROR])
        if res['type'] == GQL_DATA:
            return res
        if res['type'] == GQL_ERROR:
            return res
        if res['type'] == GQL_CONNECTION_ERROR:
            print(f'unexpected connection error {res["payload"]}')

    def subscribe(self, operation, operation_name=None, variables=None, callback=None):
        if not self._connection_init_done:
            self.set_session()

        # logging.debug(f'Operation Map (before starting sub): {self._operation_map}')
        op_id = gen_id()
        self._send_msg(GQL_START, operation_id=op_id,
                       payload={'query': operation, 'variables': variables,
                                'operation_name': operation_name})

        thread_id = threading.Thread(target=self._subscription_recieve_thread,
                                     args=(op_id, callback,))
        self._operation_map[op_id] = {'thread_id': thread_id, 'running': True}
        # logging.debug(f'Operation Map (after starting sub): {self._operation_map}')
        thread_id.start()
        return op_id

    def _subscription_recieve_thread(self, op_id, callback):
        while self._operation_map[op_id]['running']:
            res = self._wait_for([GQL_DATA, GQL_ERROR, GQL_CONNECTION_ERROR, GQL_COMPLETE],
                                 operation_id=op_id)
            if res['type'] == GQL_DATA:
                callback(op_id, res)
            if res['type'] == GQL_ERROR:
                callback(op_id, res)
            if res['type'] == GQL_CONNECTION_ERROR:
                print(f'unexpected connection error {res["payload"]}')
                break

    def stop_subscription(self, op_id):
        # print('<STOP_SUB: Op ID:>', op_id)
        # logging.debug(f'Operation Map (before stopping sub): {self._operation_map}')
        self._operation_map[op_id]['running'] = False
        # logging.debug(f'Operation Map (after altering): {self._operation_map}')
        self._send_msg(GQL_STOP, operation_id=op_id)
        self._operation_map[op_id]['thread_id'].join(10)
        del(self._operation_map[op_id])
        # logging.debug(f'Operation Map (after stopping sub): {self._operation_map}')

    def _default_callback(self, sub_id, data):
        print(f'<App> Inside default callback: SubID: {sub_id}. Data: {data}')

    def stop_all_operations(self):
        self.client.close()

# generate random alphanumeric id
def gen_id(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
