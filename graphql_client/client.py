from graphql_client.transport import GraphQLTransport, WebsocketTransport, TransportException

class GraphQLClient():
    def __init__(self, transport: GraphQLTransport) -> None:
        self.transport = transport
        self.headers = None

    def set_session(self, headers: dict = None) -> None:
        self.headers = headers
        self.transport.set_session(headers)

    def query(self, operation: str, operation_name: str = None, variables: dict = None) -> dict:
        return self.transport.execute(operation,
                                      operation_name=operation_name,
                                      variables=variables)

    def mutate(self, operation: str, operation_name: str = None, variables: dict = None) -> dict:
        return self.transport.execute(operation,
                                      operation_name=operation_name,
                                      variables=variables)

    def subscribe(self, operation: str, operation_name: str = None, variables: dict = None,
                  callback=None) -> str:
        if not isinstance(self.transport, WebsocketTransport):
            raise TransportException('Only `WebsocketTransport` can be used for subscriptions')
        return self.transport.subscribe(operation, operation_name, variables, callback)

    def stop_subscription(self, sub_id: str) -> None:
        if not isinstance(self.transport, WebsocketTransport):
            raise TransportException('Only `WebsocketTransport` can be used for subscriptions')
        self.transport.stop_subscription(sub_id)

    def stop(self) -> None:
        self.transport.stop_all_operations()

    def close(self) -> None:
        pass
