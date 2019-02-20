import time
from graphql_client import GraphQLClient

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

insert_author = """
mutation insertAuthor($name: String!) {
    createAuthor (name: $name) {
      author {
        id
        name
      }
    }
}
"""

sub = """
subscription {
  articles {
    id title
  }
}
"""

def cb(id, data):
    print('got new data: ', data)

print('starting web socket client')
#websocket.enableTrace(True)
ws = GraphQLClient('ws://localhost:8080/v1alpha1/graphql')

res = ws.query(q)
print(res)
res = ws.query(q1)
print(res)

subalive = 10
wait = 40

id = ws.subscribe(sub, callback=cb)
print(f'started subscriptions, will keep it alive for {subalive} seconds')
time.sleep(subalive)
print(f'{subalive} seconds over, stopping the subscription')
ws.stop_subscribe(id)

print(f'subscription stopped. waiting {wait} seconds to close the connection')
time.sleep(wait)
ws.close()
