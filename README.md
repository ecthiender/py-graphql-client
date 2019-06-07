# py-graphql-client
Dead-simple to use GraphQL client over websocket. Using the
[apollo-transport-ws](https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md)
protocol.

## Install

```bash
pip install py-graphql-client
```

## Examples

### Setup subscriptions super easily

```python
from graphql_client import GraphQLClient

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
ws.close()
```

### Variables can be passed

```python
from graphql_client import GraphQLClient

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

### Normal queries and mutations work too

```python
from graphql_client import GraphQLClient

ws = GraphQLClient('ws://localhost:8080/graphql')
query = """
  query ($limit: Int!) {
    notifications (order_by: {created: "desc"}, limit: $limit) {
      id
      title
      content
    }
  }
"""
res = ws.query(query, variables={'limit': 10})
print(res)
ws.close()
```


## TODO
- tests
- support http as well
- should use asyncio websocket library?
