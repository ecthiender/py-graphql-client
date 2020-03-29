# py-graphql-client

Dead-simple to use GraphQL client over websocket. Using the [apollo-transport-ws](https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md) protocol. Supports HTTP too.

## Install

```bash
pip install py-graphql-client
```

## Examples

### Super easy to setup and run subscriptions

```python
from graphql_client import GraphQLClient, WebsocketTransport

transport = WebsocketTransport('ws://localhost:8080/graphql')
client = GraphQLClient(transport)

def callback(_id, data):
  print(f"Got new data on: Operation ID: {_id}. Data: {data}")

latest_notifications = """
  subscription getLatestNotifications($limit: Int!) {
    notifications (last: $limit) {
      id
      title
      content
    }
  }
"""
sub_id = client.subscribe(latest_notifications, variables={'limit': 5}, callback=callback)

...
# later stop the subscription
client.stop_subscription(sub_id)
client.close()
```

### Set session context via HTTP headers

```python
from graphql_client import GraphQLClient, WebsocketTransport

transport = WebsocketTransport('ws://localhost:8080/graphql')
client = GraphQLClient(transport)

...

client.set_session(headers={'Authorization': 'Bearer xxxxx'})

sub_id = client.subscribe(latest_notifications, variables={'limit': 5}, callback=callback)
```

### Normal queries and mutations work too

```python
from graphql_client import GraphQLClient

transport = WebsocketTransport('ws://localhost:8080/graphql')
client = GraphQLClient('ws://localhost:8080/graphql')

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

mutation = """
  mutation ($username: String!) {
    registerUser (username: $username) {
      userId
      username
    }
  }
"""
res = client.mutate(mutation, variables={'username': 'alice'})
print(res)

client.close()
```

### Using HTTP transport

```python
from graphql_client import GraphQLClient, HttpTransport

# first create a `HttpTransport`
transport = HttpTransport('https://countries.trevorblades.com/')
# then create a `GraphQLClient` which uses the `HttpTransport`
client = GraphQLClient(transport)

query = """
query getCountry($code: ID!) {
  country(code: $code) {
    code
    name
    capital
  }
}
"""

client.set_session(headers={'Authorization': 'Bearer xxxx'})
res = client.query(query, variables={'code': 'IN'})
print(res)

# unset all headers
client.set_session(headers=None)
res = client.query(query, variables={'code': 'IN'})
print(res)

# mutations work too

create_user = """
  mutation createUser($username: String!, $password: String!) {
    insertUser(username: $username, password: $password) {
      userId
      username
    }
  }
"""
res = client.mutate(create_user, variables={'username': 'alice', 'password': 'p@55w0rd'})
print(res)

client.close()
```

## TODO
- tests
- should use asyncio websocket library?

<!--
## Features
- Websockets and GraphQL subscriptions supported!
- Flexible transport option (choose either `HttpTransport` or `WebsocketTransport`)
- Run mutiple subscriptions in parallel over a single websocket connection
- Re-authorize on subscriptions without closing the websocket connection
- HTTP session manager
-->
