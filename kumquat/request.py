"""
request schema
"""
from collections import namedtuple
from kumquat.types import Scope
import typing

_server = namedtuple("server", ["host", "port"])
_client = namedtuple("client", ["host", "port"])


class Request:
    """
    request data class
    """

    charset = "utf-8"

    def __init__(self, scope: Scope):
        self._type = scope.get("type")
        self.http_version = scope.get("http_version")
        self.server = _server(scope["server"][0], scope["server"][1])
        self.client = _client(scope["client"][0], scope["client"][1])
        self.scheme = scope.get("scheme")
        self.method = scope.get("method")
        self.root_path = scope.get("root_path")
        self.path = scope["path"].rstrip("/") if scope["path"] != "/" else scope["path"]
        self._path_dict: typing.Dict[str, str] = {}
        self.raw_path = scope.get("raw_path")
        self.query_string = scope.get("query_string")
        self.query: typing.Dict[str, str] = {}
        if self.query_string:
            for query in self.query_string.decode(self.charset).split("&"):
                query_key, query_value = query.split("=")
                query[query_key] = query_value

        self.headers = dict(scope["headers"])

    @property
    def path_dict(self) -> dict:
        """
        dict of path params if it looks like /<param>
        :return:
        """
        return self._path_dict

    @path_dict.setter
    def path_dict(self, value) -> None:
        self._path_dict = value
