# py-graphql-client
Dead-simple to use GraphQL client over websocket. It uses the
[apollo-transport-ws](https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md)
protocol.

## Examples

### Setup subscriptions super easily

```python
from client import GraphQLClient

ws = GraphQLClient('ws://localhost:8080/graphql')
def callback(_id, data):
  print("got new data..")
  print(f"msg id: {_id}. data: {data}")

query = """
  subscription {
    notifications {
      id
      title
      content
    }
  }
"""
sub_id = ws.subscribe(query, callback=callback)
...
# later stop the subscription
ws.stop_subscribe(sub_id)
```

### Variables can be passed

```python
from client import GraphQLClient

ws = GraphQLClient('ws://localhost:8080/graphql')
def callback(_id, data):
  print("got new data..")
  print(f"msg id: {_id}. data: {data}")

query = """
  subscription ($limit: Int!) {
    notifications (order_by: {created: "desc"}, limit: $limit) {
      id
      title
      content
    }
  }
"""
sub_id = ws.subscribe(query, variables={'limit': 10}, callback=callback)
```

**Normal queries and mutations work as well.**

## TODO
- should use asyncio websocket library
- support http as well
