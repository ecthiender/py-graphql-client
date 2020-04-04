import time
from graphql_client import GraphQLClient

# some sample GraphQL server which supports websocket transport and subscription
client = GraphQLClient('ws://localhost:9001')

# Simple Query Example

# query example with GraphQL variables
query = """
query getUser($userId: Int!) {
  users (id: $userId) {
    id
    username
  }
}
"""

# This is a blocking call, you receive response in the `res` variable

print('Making a query first')
res = client.query(query, variables={'userId': 2})
print('query result', res)


# Subscription Example

subscription_query = """
subscription getUser {
  users (id: 2) {
    id
    username
  }
}
"""

# Our callback function, which will be called and passed data everytime new data is available
def my_callback(op_id, data):
    print(f"Got data for Operation ID: {op_id}. Data: {data}")

print('Making a graphql subscription now...')
sub_id = client.subscribe(subscription_query, callback=my_callback)
print('Created subscription and waiting. Callback function is called whenever there is new data')

#  do some operation while the subscription is running...
time.sleep(10)
client.stop_subscribe(sub_id)
client.close()
