import time
import websocket
from graphql_client import GraphQLClient

# some sample GraphQL server which supports websocket transport and subscription
 ws = GraphQLClient('ws://localhost:5000/graphql')

## Simple Query Example ##

# query example with GraphQL variables
query = """
query getUser($userId: Int!) {
  user (id: $userId) {
    id
    username
  }
}
"""

# This is a blocking call, you receive response in the `res` variable

res = ws.query(q1, variables={'userId': 2})
print(res)


## Subscription Example ##

subscription_query = """
subscription getUser {
  user (id: 2) {
    id
    username
  }
}
"""

def my_callback(_id, data):
    print(f"Got data for Sub ID: {_id}. Data: {data}")

# sub_id = ws.subscribe(subscription_query, callback=my_callback)
sub_id = ws.subscribe(s1, variables={'userId': 2}, callback=my_callback)

# do some operation while the subscription is running...
print(f'started subscriptions, will keep it alive for 4 seconds')
time.sleep(4)
print(f'4 seconds over, stopping the subscription')
ws.stop_subscribe(sub_id)
ws.close()
