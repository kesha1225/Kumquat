import typing
from collections import namedtuple
from kumquat.types import Scope

_server = namedtuple("server", ["host", "port"])
_client = namedtuple("client", ["host", "port"])


class Request:
    charset = "utf-8"

    def __init__(self, scope: Scope):
        self._type = scope.get("type")
        self.http_version = scope.get("http_version")
        self.server = _server(scope.get("server")[0], scope.get("server")[1])
        self.client = _client(scope.get("client")[0], scope.get("client")[1])
        self.scheme = scope.get("scheme")
        self.method = scope.get("method")
        self.root_path = scope.get("root_path")
        self.path = scope.get("path")
        self._path_dict = None
        self.raw_path = scope.get("raw_path")
        self.query_string = scope.get("query_string")
        self.query = {}
        if self.query_string:
            self.query = dict(
                [
                    tuple(query.split("="))
                    for query in self.query_string.decode(self.charset).split("&")
                ]
            )
        self.headers = dict(scope.get("headers"))

    @property
    def path_dict(self) -> dict:
        """
        dict of path params if it looks like /<param>
        :return:
        """
        return self._path_dict

    @path_dict.setter
    def path_dict(self, value):
        self._path_dict = value
