# -*- coding: utf-8 -*-
"""
A simple GraphQL client that works over Websocket as the transport
protocol, instead of HTTP.
This follows the Apollo protocol.
https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md
"""

import json
import threading
import uuid
import queue
import logging
from typing import Callable

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

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ConnectionException(Exception):
    """Exception thrown during connection errors to the GraphQL server"""

class InvalidPayloadException(Exception):
    """Exception thrown if payload recived from server is mal-formed or cannot be parsed """

class GraphQLClient():
    """
    A simple GraphQL client that works over Websocket as the transport
    protocol, instead of HTTP.
    This follows the Apollo protocol.
    https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md
    """
    def __init__(self, url):
        self.ws_url = url
        self._connection_init_done = False
        # cache of the headers for a session
        self._headers = None
        # map of subscriber id to a callback function
        self._subscriber_callbacks = {}
        # our general receive queue
        self._queue = queue.Queue()
        # map of queues for each subscriber
        self._subscriber_queues = {}
        self._shutdown_receiver = False
        self._subscriptions = []
        self.connect()

    def connect(self) -> None:
        """
        Initializes a connection with the server.
        """
        self._connection = websocket.create_connection(self.ws_url,
                                                       subprotocols=[GQL_WS_SUBPROTOCOL])
        # start the reciever thread
        self._recevier_thread = threading.Thread(target=self._receiver_task)
        self._recevier_thread.start()

    def _reconnect(self):
        subscriptions = self._subscriptions
        self.__init__(self.ws_url)

        for subscription in subscriptions:
            self.subscribe(query=subscription['query'],
                           variables=subscription['variables'],
                           headers=subscription['headers'],
                           callback=subscription['callback'])

    def __dump_queues(self):
        logger.debug('[GQL_CLIENT] => Dump of all the internal queues')
        logger.debug('[GQL_CLIENT] => Global queue => \n %s', self._queue.queue)
        dumps = list(map(lambda q: (q[0], q[1].queue), self._subscriber_queues.items()))
        logger.debug('[GQL_CLIENT] => Operation queues: \n %s', dumps)

    # wait for any valid message, while ignoring GQL_CONNECTION_KEEP_ALIVE
    def _receiver_task(self):
        """the recieve function of the client. Which validates response from the
        server and queues data """
        reconnected = False
        while not self._shutdown_receiver and not reconnected:
            self.__dump_queues()
            try:
                res = self._connection.recv()
            except websocket._exceptions.WebSocketConnectionClosedException as e:
                self._reconnect()
                reconnected = True
                continue

            try:
                msg = json.loads(res)
            except json.JSONDecodeError as err:
                logger.warning('Ignoring. Server sent invalid JSON data: %s \n %s', res, err)
                continue

            # ignore messages which are GQL_CONNECTION_KEEP_ALIVE
            if msg['type'] != GQL_CONNECTION_KEEP_ALIVE:

                # check all GQL_DATA and GQL_COMPLETE should have 'id'.
                # Otherwise, server is sending malformed responses, error out!
                if msg['type'] in [GQL_DATA, GQL_COMPLETE] and 'id' not in msg:
                    # TODO: main thread can't catch this exception; setup
                    # exception queues. but this scenario will only happen with
                    # servers having glaring holes in implementing the protocol
                    # correctly, which is rare. hence this is not very urgent
                    err = f'Protocol Violation.\nExpected "id" in {msg}, but could not find.'
                    raise InvalidPayloadException(err)

                # if the message has an id, it is meant for a particular operation
                if 'id' in msg:
                    op_id = msg['id']

                    # put it in the correct operation/subscriber queue
                    if op_id in self._subscriber_queues:
                        self._subscriber_queues[op_id].put(msg)
                    else:
                        self._subscriber_queues[op_id] = queue.Queue()
                        self._subscriber_queues[op_id].put(msg)

                    # if a callback fn exists with the id, call it
                    if op_id in self._subscriber_callbacks:
                        user_fn = self._subscriber_callbacks[op_id]
                        user_fn(op_id, msg)

                # if it doesn't have an id, put in the global queue
                else:
                    self._queue.put(msg)

    def _insert_subscriber(self, op_id, callback_fn):
        self._subscriber_callbacks[op_id] = callback_fn

    def _remove_subscriber(self, op_id):
        del self._subscriber_callbacks[op_id]

    def _create_operation_queue(self, op_id):
        self._subscriber_queues[op_id] = queue.Queue()

    def _remove_operation_queue(self, op_id):
        if op_id in self._subscriber_queues:
            del self._subscriber_queues[op_id]

    def _get_operation_result(self, op_id):
        return self._subscriber_queues[op_id].get()

    def _connection_init(self, headers=None):
        # if we have already initialized and the passed headers are same as
        # prev headers, then do nothing and return
        if self._connection_init_done and headers == self._headers:
            return

        self._headers = headers
        # send the `connection_init` message with the payload
        payload = {'type': GQL_CONNECTION_INIT, 'payload': {'headers': headers}}
        self._connection.send(json.dumps(payload))

        res = self._queue.get()

        if res['type'] == GQL_CONNECTION_ERROR:
            err = res['payload'] if 'payload' in res else 'unknown error'
            raise ConnectionException(err)
        if res['type'] == GQL_CONNECTION_ACK:
            self._connection_init_done = True
            return

        err_msg = "Unknown message from server, this client did not understand. " + \
            "Original message: " + res['type']
        raise ConnectionException(err_msg)

    def _start(self, payload, callback=None):
        """ pass a callback function only if this is a subscription """
        op_id = uuid.uuid4().hex
        frame = {'id': op_id, 'type': GQL_START, 'payload': payload}
        self._create_operation_queue(op_id)
        if callback:
            self._insert_subscriber(op_id, callback)
        self._connection.send(json.dumps(frame))
        return op_id

    def _stop(self, op_id):
        payload = {'id': op_id, 'type': GQL_STOP}
        self._connection.send(json.dumps(payload))

    def query(self, query: str, variables: dict = None, headers: dict = None) -> dict:
        """
        Run a GraphQL query or mutation. The `query` argument is a GraphQL query
        string. You can pass optional variables and headers.

        PS: To run a subscription, see the `subscribe` method.
        """
        self._connection_init(headers)
        payload = {'headers': headers, 'query': query, 'variables': variables}
        op_id = self._start(payload)
        res = self._get_operation_result(op_id)
        self._stop(op_id)
        ack = self._get_operation_result(op_id)
        if ack['type'] != GQL_COMPLETE:
            logger.warning('Expected to recieve complete, but received: %s', ack)
        self._remove_operation_queue(op_id)
        return res

    def subscribe(self, query: str, variables: dict = None, headers: dict = None,
                  callback: Callable[[str, dict], None] = None) -> str:
        """
        Run a GraphQL subscription.

        Parameters:
        query (str): the GraphQL query string
        callback (function): a callback function. This is mandatory.
        This callback function is called, everytime there is new data from the
        subscription.
        variables (dict): (optional) GraphQL variables
        headers (dict): (optional) a dictionary of headers for the session

        Returns:
        op_id (str): The operation id (a UUIDv4) for this subscription operation
        """

        # sanity check that the user passed a valid function
        if not callback or not callable(callback):
            raise TypeError('the argument `callback` is mandatory and it should be a function')

        self._connection_init(headers)
        payload = {'headers': headers, 'query': query, 'variables': variables}
        op_id = self._start(payload, callback)
        self._subscriptions.append({
            'query': query,
            'variables': variables,
            'headers': headers,
            'callback': callback
        })
        return op_id

    def stop_subscribe(self, op_id: str) -> None:
        """
        Stop a subscription. Takes an operation ID (`op_id`) and stops the
        subscription.
        """
        self._stop(op_id)
        self._remove_subscriber(op_id)
        self._remove_operation_queue(op_id)

    def close(self) -> None:
        """
        Close the connection with the server. To reconnect, use the `connect`
        method.
        """
        self._shutdown_receiver = True
        self._recevier_thread.join()
        self._connection.close()

    def __enter__(self):
        """ enter method for context manager """
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """ exit method for context manager """
        self.close()
