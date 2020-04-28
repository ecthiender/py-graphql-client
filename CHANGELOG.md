# Unreleased

## Fixes

## Enhancements/Features
- Added support for context manager API
  now you can use the client with context manager API, like so:
  ```python
  with GraphQLClient("ws://localhost/graphql") as client:
      client.subscribe(...)
  ```


# 0.1.1

## Fixes
- fixed: when stop_subscribe was called it would stop the receive thread, so further subscription would not work
- fixed: if more than operations were scheduled, the correct callback might not receive the correct data
- refactor: use a separate thread all the time to continously receive data from the server and put it on queues
- refactor: use separate queues for each operation to properly keep track of incoming and data and who it is meant for
- other misc improvements
- Removing sleep, the `conn.recv` call is blocking
- Added `graphql-ws` subprotocol header to help with some WSS connections

## Enhancements/Features
- UUIDv4 for generating operation IDs (#16)
- Added tests


# 0.1.0
- basic working of GraphQL over Websocket (Apollo) protocol
