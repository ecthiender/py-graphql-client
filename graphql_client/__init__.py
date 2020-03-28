# -*- coding: utf-8 -*-
"""
A simple GraphQL client that works over Websocket as the transport
protocol, instead of HTTP.
This follows the Apollo protocol.
https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md
"""

import sys
import string
import random
import json
import threading

import websocket


GQL_WS_SUBPROTOCOL = "graphql-ws"

# all the message types
GQL_CONNECTION_INIT = 'connection_init'
GQL_START = 'start'
GQL_STOP = 'stop'
GQL_CONNECTION_TERMINATE = 'connection_terminate'
GQL_CONNECTION_ERROR = 'connection_error'
GQL_CONNECTION_ACK = 'connection_ack'
GQL_DATA = 'data'
GQL_ERROR = 'error'
GQL_COMPLETE = 'complete'
GQL_CONNECTION_KEEP_ALIVE = 'ka'


class ConnectionException(Exception):
    """Exception thrown during connection errors to the GraphQL server"""


class GraphQLClient():
    """
    A simple GraphQL client that works over Websocket as the transport
    protocol, instead of HTTP.
    This follows the Apollo protocol.
    https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md
    """

    def __init__(self, url):
        self.ws_url = url
        self._connection = websocket.create_connection(self.ws_url,
                                                       on_message=self._on_message,
                                                       subprotocols=[GQL_WS_SUBPROTOCOL])
        self._connection.on_message = self._on_message
        self._subscription_running = False
        self._st_id = None

    def _on_message(self, message, skip_ka=True):
        """ default callback handler when message arrives """
        data = json.loads(message)
        # skip keepalive messages
        if not(skip_ka and data['type'] == GQL_CONNECTION_KEEP_ALIVE):
            print(message)

    # wait for any valid message, while ignoring GQL_CONNECTION_KEEP_ALIVE
    def _receive(self):
        """the recieve function of the client. Which validates response from the
        server and returns data """
        res = self._connection.recv()
        try:
            msg = json.loads(res)
        except json.JSONDecodeError as err:
            print(f'Server sent invalid JSON data: {res} \n {err}')
            sys.exit(1)
        if msg['type'] != GQL_CONNECTION_KEEP_ALIVE:
            return msg
        # FIXME: this can lead to potential inifinite loop when server doesn't
        # send anything other than GQL_CONNECTION_KEEP_ALIVE
        return self._receive()

    def _connection_init(self, headers=None):
        # send the `connection_init` message with the payload
        payload = {'type': 'connection_init', 'payload': {'headers': headers}}
        self._connection.send(json.dumps(payload))

        res = self._receive()
        if res['type'] == 'connection_error':
            err = res['payload'] if 'payload' in res else 'unknown error'
            raise ConnectionException(err)
        if res['type'] == 'connection_ack':
            return None

        err_msg = "Unknown message from server, this client did not understand. " + \
            "Original message: " + res['type']
        raise ConnectionException(err_msg)

    def _start(self, payload):
        _id = gen_id()
        frame = {'id': _id, 'type': GQL_START, 'payload': payload}
        self._connection.send(json.dumps(frame))
        return _id

    def _stop(self, _id):
        # print('inside _stop()')
        payload = {'id': _id, 'type': GQL_STOP}
        self._connection.send(json.dumps(payload))
        # print(f'sent message {GQL_STOP}')
        # print('inside _stop :: recving...')
        resp = self._connection.recv()
        # print('inside _stop :: recvd resp', resp)
        return resp

    def query(self, query, variables=None, headers=None):
        self._connection_init(headers)
        payload = {'headers': headers, 'query': query, 'variables': variables}
        _id = self._start(payload)
        res = self._receive()
        self._stop(_id)
        return res


    def _subscription_recieve_thread(self, sub_id, callback):
        # print('inside the subs method')
        while self._subscription_running:
            # print('subscription is running')
            # print('recving...')
            resp = self._connection.recv()
            res = json.loads(resp)
            # print('inside subs:: recved resp', resp)
            if res['type'] == GQL_CONNECTION_KEEP_ALIVE:
                continue
            if res['type'] == GQL_ERROR or res['type'] == GQL_COMPLETE:
                # print(res)
                self.stop_subscribe(sub_id)
                break
            elif res['type'] == GQL_DATA:
                callback(sub_id, res)

    def subscribe(self, query, variables=None, headers=None, callback=None):
        self._connection_init(headers)
        payload = {'headers': headers, 'query': query, 'variables': variables}
        callback = self._on_message if not callback else callback
        sub_id = self._start(payload)
        self._subscription_running = True
        self._st_id = threading.Thread(target=self._subscription_recieve_thread, args=(sub_id, callback,))
        self._st_id.start()
        return sub_id

    def stop_subscribe(self, _id):
        self._subscription_running = False
        self._stop(_id)
        self._st_id.join(3)

    def close(self):
        self._connection.close()


# generate random alphanumeric id
def gen_id(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
