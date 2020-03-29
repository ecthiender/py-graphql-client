# -*- coding: utf-8 -*-
"""A simple GraphQL client that works over both Websocket and HTTP as the transport protocol.
Over HTTP it follows the general convention/protocol: https://graphql.github.io/learn/serving-over-http/
Over websocket it follows the apollo protocol: https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md
"""

from graphql_client.client import GraphQLClient
from graphql_client.transport import WebsocketTransport, HttpTransport
