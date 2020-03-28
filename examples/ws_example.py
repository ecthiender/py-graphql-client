import time
import random

from graphql_client import GraphQLClient, WebsocketTransport

transport = WebsocketTransport('wss://hge-testing.herokuapp.com/v1/graphql')
client = GraphQLClient(transport)

query = """
query getUser($userId: Int!) {
  users(where:{u_id: {_eq: $userId}}) {
    u_id
    u_name
  }
}
"""

res = client.query(query, variables={'userId': 2})
print(res)

subscription_query = """
subscription getUser {
  user (id: 2) {
    id
    username
  }
}
"""

def my_callback(_id, data):
    print(f"<Subs Callback>: Got data for Sub ID: {_id}. Data: {data}")

sub_id = client.subscribe(subscription_query, variables={'userId': 2}, callback=my_callback)

# do some operation while the subscription is running...
time.sleep(3)

client.stop_subscription(sub_id)
client.close()
