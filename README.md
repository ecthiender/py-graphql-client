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

query = """
  subscription {
    notifications {
      id
      title
      content
    }
  }
"""

with GraphQLClient('ws://localhost:8080/graphql') as client:

  sub_id = client.subscribe(query, callback=callback)
  # do other stuff
  # ...
  # later stop the subscription
  client.stop_subscribe(sub_id)

def callback(_id, data):
  print("got new data..")
  print(f"msg id: {_id}. data: {data}")
```

### Variables can be passed

```python
from graphql_client import GraphQLClient

query = """
    subscription ($limit: Int!) {
      notifications (order_by: {created: "desc"}, limit: $limit) {
        id
        title
        content
      }
    }
  """

with GraphQLClient('ws://localhost:8080/graphql') as client:
  sub_id = ws.subscribe(query, variables={'limit': 10}, callback=callback)
  # ...

def callback(_id, data):
  print("got new data..")
  print(f"msg id: {_id}. data: {data}")


```

### Headers can be passed too

```python
from graphql_client import GraphQLClient

query = """
    subscription ($limit: Int!) {
      notifications (order_by: {created: "desc"}, limit: $limit) {
        id
        title
        content
      }
    }
  """

with GraphQLClient('ws://localhost:8080/graphql') as client:
  sub_id = client.subscribe(query,
                            variables={'limit': 10},
                            headers={'Authorization': 'Bearer xxxx'},
                            callback=callback)
  ...
  client.stop_subscribe(sub_id)

def callback(_id, data):
  print("got new data..")
  print(f"msg id: {_id}. data: {data}")
```

### Normal queries and mutations work too

```python
from graphql_client import GraphQLClient

query = """
  query ($limit: Int!) {
    notifications (order_by: {created: "desc"}, limit: $limit) {
      id
      title
      content
    }
  }
"""

with GraphQLClient('ws://localhost:8080/graphql') as client:
    res = client.query(query, variables={'limit': 10}, headers={'Authorization': 'Bearer xxxx'})
    print(res)
```

### Without the context manager API

```python
from graphql_client import GraphQLClient

query = """
  query ($limit: Int!) {
    notifications (order_by: {created: "desc"}, limit: $limit) {
      id
      title
      content
    }
  }
"""

client = GraphQLClient('ws://localhost:8080/graphql') as client:
res = client.query(query, variables={'limit': 10}, headers={'Authorization': 'Bearer xxxx'})
print(res)
client.close()
```


## TODO
- support http as well
- should use asyncio websocket library?
