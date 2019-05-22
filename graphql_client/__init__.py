# -*- coding: utf-8 -*-
"""
A simple GraphQL client that works over Websocket as the transport
protocol, instead of HTTP.
This follows the Apollo protocol.
https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md
"""

import string
import random
import json
import time
import threading

from websocket import create_connection


GQL_WS_SUBPROTOCOL = "graphql-ws"


class GraphQLClient:
    """
    A simple GraphQL client that works over Websocket as the transport
    protocol, instead of HTTP.
    This follows the Apollo protocol.
    https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md
    """

    def __init__(self, url):
        self.ws_url = url
        self._conn = create_connection(self.ws_url, subprotocols=[GQL_WS_SUBPROTOCOL])
        self._subscription_running = False
        self._subscription_thread = None

    def _on_message(self, query_id, message):
        if message["type"] == "ka":
            # skip keepalive messages
            return
        print(message)

    def _conn_init(self, headers=None):
        payload = {"type": "connection_init", "payload": {"headers": headers}}
        self._conn.send(json.dumps(payload))
        self._conn.recv()

    def _start(self, payload):
        query_id = gen_id()
        frame = {"id": query_id, "type": "start", "payload": payload}
        self._conn.send(json.dumps(frame))
        return query_id

    def _stop(self, query_id):
        payload = {"id": query_id, "type": "stop"}
        self._conn.send(json.dumps(payload))
        return self._conn.recv()

    def query(self, query, variables=None, headers=None):
        self._conn_init(headers)
        payload = {"headers": headers, "query": query, "variables": variables}
        query_id = self._start(payload)
        resp = json.loads(self._conn.recv())
        self._stop(query_id)
        return resp

    def subscribe(self, query, variables=None, headers=None, callback=None):
        self._conn_init(headers)
        payload = {"headers": headers, "query": query, "variables": variables}
        callback = callback or self._on_message
        query_id = self._start(payload)

        def subs():
            self._subscription_running = True
            while self._subscription_running:
                resp = json.loads(self._conn.recv())
                if resp["type"] == "error" or resp["type"] == "complete":
                    print(resp)
                    self.stop_subscription(query_id)
                    break
                elif resp["type"] != "ka":
                    callback(query_id, resp)
                time.sleep(1)

        self._subscription_thread = threading.Thread(target=subs)
        self._subscription_thread.start()
        return query_id

    def stop_subscription(self, query_id):
        self._subscription_running = False
        self._subscription_thread.join()
        self._stop(query_id)

    def close(self):
        self._conn.close()


# generate random alphanumeric id
def gen_id(size=6, chars=string.ascii_letters + string.digits):
    return "".join(random.choice(chars) for _ in range(size))
