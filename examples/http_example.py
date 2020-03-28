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

# changing session context via headers
client.set_session(headers={'Authorization': 'Bearer xxxx'})

# # This is a blocking call, you receive response in the `res` variable
res = client.query(query, variables={'code': 'IN'})
print(res)
client.close()
