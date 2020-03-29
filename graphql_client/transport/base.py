import abc


class TransportException(Exception):
    """..."""

class GraphQLTransport(abc.ABC):
    @abc.abstractmethod
    def set_session(self, headers: dict = None) -> None:
        pass

    @abc.abstractmethod
    def execute(self, operation: str, operation_name: str = None, variables: dict = None) -> dict:
        pass

    @abc.abstractmethod
    def stop_all_operations(self):
        pass
