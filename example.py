import time
from client import GraphQLClient
import websocket

query = """
query {
    author { id name }
}
"""
sub = """
subscription {
    author { id name }
}
"""
insert_author = """
mutation insertAuthor($name: String!) {
    insert_author (objects: [
    {
        name: $name
    }
    ]) {
    returning {
        id
        name
    }
    }
}
"""
#res = ws.query(insert_author, variables={'name': 'Anon'})
def cb(id, data):
    print('got new data: ', data)

q = """
query {
  allUsers { id username }
  user (id: 2) {
    id
    username
  }
}
"""

q1 = """
query {
  companies (where: {id: {_eq: 1}}) {
    id
    name
    created_at
  }
}
"""

print('starting web socket client')
#websocket.enableTrace(True)
ws = GraphQLClient('ws://localhost:8080/v1alpha1/graphql')

sub1 = "subscription { animals {id common_name}}"

#res = ws.query(q)
#print(res)
#res = ws.query(q1)
#print(res)
#ws.close()
subalive = 10
wait = 40
#id = ws.subscribe(sub1, callback=cb)
#print(f'started subscriptions, will keep it alive for {subalive} seconds')
#time.sleep(subalive)
#print(f'{subalive} seconds over, stopping the subscription')
#ws.stop_subscribe(id)
#
#time.sleep(2)

id = ws.subscribe(sub1, callback=cb)
print(f'started subscriptions, will keep it alive for {subalive} seconds')
time.sleep(subalive)
print(f'{subalive} seconds over, stopping the subscription')
ws.stop_subscribe(id)

print(f'subscription stopped. waiting {wait} seconds to close the connection')
time.sleep(wait)
ws.close()
